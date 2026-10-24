"""OpenAI-compatible client (Groq free tier by default) with token accounting
and an on-disk cache.

- `calls` counts LOGICAL calls the system made (cache hits included), so cost
  metrics are identical whether or not the cache was warm.
- Measure latency on uncached runs only.
- For a stability rerun (benchmark honesty rule), change cache_namespace."""
from __future__ import annotations
import hashlib
import json
import os
import time
from pathlib import Path


class LLMRateLimitExceeded(RuntimeError):
    """A provider rate limit remained after the configured bounded retries."""


class LLMEmptyCompletion(RuntimeError):
    """The provider returned no usable completion (often because reasoning was truncated)."""


def run_with_bounded_retries(operation, *, retries: int, base_delay_s: float,
                             max_delay_s: float, sleep=time.sleep,
                             retryable: tuple[type[BaseException], ...],
                             max_provider_wait_s: float = 30.0):
    """Retry with bounded backoff while respecting short provider retry hints.

    Rate-limit hints up to max_provider_wait_s are honored with a small safety
    margin. Longer hints stop early rather than sleeping through a likely
    exhausted quota/window. The SDK's own retries remain disabled.
    """
    from .ratelimit import suggested_wait

    for attempt in range(retries + 1):
        try:
            return operation()
        except retryable as exc:
            is_rate_limit = isinstance(exc, retryable[0])
            hint = suggested_wait(exc) if is_rate_limit else None

            if is_rate_limit and hint is not None and hint > max_provider_wait_s:
                raise LLMRateLimitExceeded(
                    f"provider requested retry after {hint:.1f}s, exceeding the "
                    f"configured {max_provider_wait_s:.1f}s short-wait cap; stop and resume later"
                ) from exc

            if attempt == retries:
                if is_rate_limit:
                    detail = str(exc).strip()
                    suffix = f"; provider message: {detail}" if detail else ""
                    if hint is not None:
                        suffix += f"; suggested_wait_s={hint:.1f}"
                    raise LLMRateLimitExceeded(
                        f"rate limited after {attempt + 1} attempts; rerun later to resume{suffix}"
                    ) from exc
                raise

            if is_rate_limit and hint is not None:
                delay = min(max_provider_wait_s, hint) + 0.5
            else:
                delay = min(base_delay_s * (2 ** attempt), max_delay_s)
            sleep(delay)


class LLMClient:
    def __init__(self, cfg: dict, cache_root: Path | None = None):
        from openai import OpenAI
        key = os.environ.get(cfg.get("api_key_env", "GROQ_API_KEY"))
        if not key:
            raise RuntimeError(f"{cfg.get('api_key_env', 'GROQ_API_KEY')} is not set (see .env.example)")
        # Disable SDK retries so the retry limit below is the only retry loop.
        self.client = OpenAI(base_url=cfg["base_url"], api_key=key, max_retries=0)
        self.model = cfg["model"]
        self.max_retries = int(cfg.get("max_retries", 2))
        self.retry_base_seconds = float(cfg.get("retry_base_seconds", 1.0))
        self.retry_max_seconds = float(cfg.get("retry_max_seconds", 4.0))
        # Keep sequential benchmark generation below Groq's free-plan RPM cap.
        # Cache hits bypass this; only provider requests are paced.
        self.min_provider_interval_seconds = float(cfg.get("min_provider_interval_seconds", 0.0))
        self._last_provider_request_at: float | None = None
        self.reasoning_effort = cfg.get("reasoning_effort")
        # reasoning models burn completion tokens on hidden thinking; give them room
        self.headroom = int(cfg.get("token_headroom", 0)) if self.reasoning_effort else 0
        self.cache_dir = None
        if cache_root is not None:
            # Use an environment override for isolated runs; never silently mix
            # new generation/stability output into the tracked Run 1 cache.
            namespace_override = os.getenv("ATLAS_CACHE_NAMESPACE")
            namespace = namespace_override if namespace_override is not None else cfg.get("cache_namespace", "default")
            if (not isinstance(namespace, str) or not namespace.strip()
                    or namespace in {".", ".."} or "/" in namespace or "\\" in namespace):
                raise ValueError("ATLAS_CACHE_NAMESPACE / llm.cache_namespace must be a single non-empty folder name")
            self.cache_dir = Path(cache_root) / namespace
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        # calls/prompt_tokens/completion_tokens/cache_hits: LOGICAL accounting (cache-independent). Do not change
        # their meaning: Run 1 cost figures are computed from them.
        # The rest describe what actually hit the provider (your quota).
        self.stats = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "cache_hits": 0,
                      "cache_misses": 0, "provider_calls": 0, "retry_attempts": 0,
                      "rate_limit_errors": 0, "connection_errors": 0, "rate_limit_stops": 0,
                      "empty_completions": 0, "cache_corruptions": 0,
                      "provider_prompt_tokens": 0, "provider_completion_tokens": 0}

    def snapshot(self) -> dict:
        return dict(self.stats)

    def _key(self, model, messages, temperature, max_tokens, reasoning_effort=None, token_headroom=None) -> str:
        blob = json.dumps([model, messages, temperature, max_tokens, reasoning_effort, token_headroom], sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()

    def chat( self, messages: list[dict], temperature: float = 0.0, max_tokens: int = 700, model: str | None = None, reasoning_effort: str | None = None, token_headroom: int | None = None, ) -> str:
        model = model or self.model
        effort = reasoning_effort if reasoning_effort is not None else self.reasoning_effort
        headroom = token_headroom if token_headroom is not None else self.headroom
        self.stats["calls"] += 1
        path = None
        if self.cache_dir is not None:
            path = self.cache_dir / f"{self._key(model, messages, temperature, max_tokens, effort, headroom)}.json"
            if path.exists():
                try:
                    hit = json.loads(path.read_text(encoding="utf-8"))
                    if not isinstance(hit, dict) or not isinstance(hit.get("text"), str) or not hit["text"].strip():
                        raise ValueError("invalid cached response shape")
                    pt, ct = int(hit["prompt_tokens"]), int(hit["completion_tokens"])
                    if pt < 0 or ct < 0:
                        raise ValueError("negative cached token count")
                except (OSError, ValueError, TypeError, KeyError):
                    # A torn/manual cache file must not permanently break the same prompt.
                    self.stats["cache_corruptions"] += 1
                    try:
                        path.unlink()
                    except OSError:
                        pass
                else:
                    self.stats["cache_hits"] += 1
                    self.stats["prompt_tokens"] += pt
                    self.stats["completion_tokens"] += ct
                    return hit["text"]

        from openai import RateLimitError, APIConnectionError

        self.stats["cache_misses"] += 1
        attempt = {"n": 0}

        def create():
            if self._last_provider_request_at is not None and self.min_provider_interval_seconds:
                remaining = self.min_provider_interval_seconds - (time.monotonic() - self._last_provider_request_at)
                if remaining > 0:
                    time.sleep(remaining)
            attempt["n"] += 1
            self.stats["provider_calls"] += 1
            if attempt["n"] > 1:
                self.stats["retry_attempts"] += 1
            kwargs = {}
            if effort:
                kwargs["extra_body"] = {"reasoning_effort": effort}
            # Pace every provider attempt, including failed 429/connection attempts.
            # Otherwise an error followed by a quick retry can bypass the RPM guard.
            self._last_provider_request_at = time.monotonic()
            try:
                response = self.client.chat.completions.create(
                    model=model, messages=messages, temperature=temperature,
                    max_tokens=max_tokens + headroom, **kwargs)
                return response
            except RateLimitError:
                self.stats["rate_limit_errors"] += 1
                raise
            except APIConnectionError:
                self.stats["connection_errors"] += 1
                raise

        try:
            r = run_with_bounded_retries(
                create,
                retries=self.max_retries,
                base_delay_s=self.retry_base_seconds,
                max_delay_s=self.retry_max_seconds,
                retryable=(RateLimitError, APIConnectionError),
            )
        except LLMRateLimitExceeded:
            self.stats["rate_limit_stops"] += 1
            raise
        # Quota consumed is counted even if the completion turns out empty.
        usage = getattr(r, "usage", None)
        self.stats["provider_prompt_tokens"] += getattr(usage, "prompt_tokens", 0) or 0
        self.stats["provider_completion_tokens"] += getattr(usage, "completion_tokens", 0) or 0
        choices = getattr(r, "choices", None)
        if not choices:
            self.stats["empty_completions"] += 1
            raise LLMEmptyCompletion(f"empty completion from {model} (provider returned no choices)")
        choice = choices[0]
        text = getattr(getattr(choice, "message", None), "content", None) or ""
        if not text.strip():
            self.stats["empty_completions"] += 1
            raise LLMEmptyCompletion(
                f"empty completion from {model} (finish_reason={getattr(choice, 'finish_reason', None)}). "
                "If 'length': raise llm.token_headroom in the config; reasoning models spend tokens thinking.")
        pt = getattr(usage, "prompt_tokens", 0) or 0
        ct = getattr(usage, "completion_tokens", 0) or 0
        self.stats["prompt_tokens"] += pt
        self.stats["completion_tokens"] += ct
        if path is not None:
            path.write_text(json.dumps({"text": text, "prompt_tokens": pt,
                                        "completion_tokens": ct}), encoding="utf-8")
        return text
