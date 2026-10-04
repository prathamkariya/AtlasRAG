"""Provider-hint-aware waiting for batch scripts. Does NOT touch llm.py's retry policy.

Why: a TPM (tokens-per-minute) 429 says exactly how long to wait ("try again in 2.505s").
llm.py's bounded retries (1s, 2s) can give up just short of that. Batch scripts may
opt in (--wait-on-rate-limit) to sleep the suggested time, bounded:
  - at most `max_resumes` waits per call
  - each wait capped at `max_wait_each` seconds
  - a hint LONGER than the cap (a daily/hourly limit) is not waited out: it re-raises,
    so the script stops cleanly and you rerun later.
Exceptions are matched by class name, so this works with whatever LLMRateLimitExceeded
llm.py defines."""
from __future__ import annotations
import re
import time

_QUOTA_NAMES = {"LLMRateLimitExceeded", "RateLimitError"}
_HINT = re.compile(r"try again in\s+((?:\d+(?:\.\d+)?(?:ms|h|m|s)\s*)+)", re.I)
_PART = re.compile(r"(\d+(?:\.\d+)?)(ms|h|m|s)", re.I)
_UNIT = {"ms": 0.001, "s": 1.0, "m": 60.0, "h": 3600.0}


def _chain(exc):
    seen = []
    while exc is not None and exc not in seen:
        seen.append(exc)
        exc = exc.__cause__ or exc.__context__
    return seen


def is_quota_error(exc: BaseException) -> bool:
    return any(type(e).__name__ in _QUOTA_NAMES for e in _chain(exc))


def parse_wait(text: str):
    m = _HINT.search(text or "")
    if not m:
        return None
    return sum(float(n) * _UNIT[u.lower()] for n, u in _PART.findall(m.group(1)))


def suggested_wait(exc: BaseException):
    """Seconds the provider asked us to wait, if the exception chain says so."""
    for e in _chain(exc):
        hdrs = getattr(getattr(e, "response", None), "headers", None)
        if hdrs is not None:
            try:
                return float(hdrs.get("retry-after"))
            except (TypeError, ValueError):
                pass
        w = parse_wait(str(e))
        if w is not None:
            return w
    return None


def call_with_quota_wait(fn, max_resumes: int = 6, max_wait_each: float = 30.0,
                         default_wait: float = 10.0, sleep=time.sleep, log=print):
    for attempt in range(max_resumes + 1):
        try:
            return fn()
        except Exception as e:
            if not is_quota_error(e) or attempt == max_resumes:
                raise
            hint = suggested_wait(e)
            if hint is not None and hint > max_wait_each:
                raise                                   # daily/hourly limit: stop, don't wait
            wait = (hint if hint is not None else default_wait) + 0.5
            log(f"[rate limit] waiting {wait:.1f}s (resume {attempt + 1}/{max_resumes})")
            sleep(wait)
