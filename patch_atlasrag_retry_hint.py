from pathlib import Path

path = Path("src/atlasrag/llm.py")
if not path.is_file():
    raise SystemExit("ERROR: Run this from the AtlasRAG repository root.")

source = path.read_text(encoding="utf-8")
backup = path.with_name("llm.py.before_provider_retry_hint.bak")
if not backup.exists():
    backup.write_text(source, encoding="utf-8")

start = source.index("def run_with_bounded_retries(")
end = source.index("\n\nclass LLMClient:", start)

replacement = r'''def run_with_bounded_retries(operation, *, retries: int, base_delay_s: float,
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
'''

source = source[:start] + replacement + source[end:]
path.write_text(source, encoding="utf-8")
print("Patched src/atlasrag/llm.py successfully.")
print(f"Backup: {backup}")
print("Run: pytest tests/test_ratelimit.py tests/test_llm.py -q")
