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


def run_with_bounded_retries(operation, *, retries: int, base_delay_s: float,
                             max_delay_s: float, sleep=time.sleep,
                             retryable: tuple[type[BaseException], ...]):
    """Run an operation at most ``retries + 1`` times with capped backoff.

    The OpenAI client is configured with its own retries disabled, so this is
    the sole retry policy and its delay budget is explicit and testable.
    """
    for attempt in range(retries + 1):
        try:
            return operation()
        except retryable as exc:
            if attempt == retries:
                if isinstance(exc, retryable[0]):
                    raise LLMRateLimitExceeded(
                        f"rate limited after {attempt + 1} attempts; rerun later to resume"
                    ) from exc
                raise
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
        self.reasoning_effort = cfg.get("reasoning_effort")
        # reasoning models burn completion tokens on hidden thinking; give them room
        self.headroom = int(cfg.get("token_headroom", 0)) if self.reasoning_effort else 0
        self.cache_dir = None
        if cache_root is not None:
            self.cache_dir = Path(cache_root) / cfg.get("cache_namespace", "default")
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        # calls/prompt_tokens/completion_tokens/cache_hits: LOGICAL accounting (cache-independent). Do not change
        # their meaning: Run 1 cost figures are computed from them.
        # The rest describe what actually hit the provider (your quota).
        self.stats = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "cache_hits": 0,
                      "cache_misses": 0, "provider_calls": 0, "retry_attempts": 0,
                      "rate_limit_errors": 0, "connection_errors": 0, "rate_limit_stops": 0,
                      "empty_completions": 0,
                      "provider_prompt_tokens": 0, "provider_completion_tokens": 0}

    def snapshot(self) -> dict:
        return dict(self.stats)

    def _key(self, model, messages, temperature, max_tokens) -> str:
        blob = json.dumps([model, messages, temperature, max_tokens, self.reasoning_effort], sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()

    def chat(self, messages: list[dict], temperature: float = 0.0,
             max_tokens: int = 700, model: str | None = None) -> str:
        model = model or self.model
        self.stats["calls"] += 1
        path = None
        if self.cache_dir is not None:
            path = self.cache_dir / f"{self._key(model, messages, temperature, max_tokens)}.json"
            if path.exists():
                hit = json.loads(path.read_text(encoding="utf-8"))
                self.stats["cache_hits"] += 1
                self.stats["prompt_tokens"] += hit["prompt_tokens"]
                self.stats["completion_tokens"] += hit["completion_tokens"]
                return hit["text"]

        from openai import RateLimitError, APIConnectionError

        self.stats["cache_misses"] += 1
        attempt = {"n": 0}

        def create():
            attempt["n"] += 1
            self.stats["provider_calls"] += 1
            if attempt["n"] > 1:
                self.stats["retry_attempts"] += 1
            kwargs = {}
            if self.reasoning_effort:
                kwargs["extra_body"] = {"reasoning_effort": self.reasoning_effort}
            try:
                return self.client.chat.completions.create(
                    model=model, messages=messages, temperature=temperature,
                    max_tokens=max_tokens + self.headroom, **kwargs)
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
        # quota actually consumed, counted even if the completion turns out empty
        self.stats["provider_prompt_tokens"] += getattr(r.usage, "prompt_tokens", 0) or 0
        self.stats["provider_completion_tokens"] += getattr(r.usage, "completion_tokens", 0) or 0
        text = r.choices[0].message.content or ""
        if not text.strip():
            self.stats["empty_completions"] += 1
            raise RuntimeError(
                f"empty completion from {model} (finish_reason={r.choices[0].finish_reason}). "
                "If 'length': raise llm.token_headroom in the config; reasoning models spend tokens thinking.")
        pt = getattr(r.usage, "prompt_tokens", 0) or 0
        ct = getattr(r.usage, "completion_tokens", 0) or 0
        self.stats["prompt_tokens"] += pt
        self.stats["completion_tokens"] += ct
        if path is not None:
            path.write_text(json.dumps({"text": text, "prompt_tokens": pt,
                                        "completion_tokens": ct}), encoding="utf-8")
        return text
