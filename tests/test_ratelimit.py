import json
import types

import pytest

from atlasrag.ratelimit import parse_wait, suggested_wait, is_quota_error, call_with_quota_wait
from atlasrag.bench.audit_runner import run_audit, summarize, load_done
from atlasrag.bench.schema import Question


class LLMRateLimitExceeded(Exception):          # same class NAME as llm.py's; matching is by name
    pass


def quota_exc(msg="Rate limit reached ... Please try again in 2.505s. Need more tokens?"):
    try:
        try:
            raise RuntimeError(msg)
        except RuntimeError as inner:
            raise LLMRateLimitExceeded("rate limited after 3 attempts; rerun later to resume") from inner
    except LLMRateLimitExceeded as e:
        return e


def test_parse_wait_formats():
    assert parse_wait("Please try again in 2.505s. Need more tokens?") == pytest.approx(2.505)
    assert parse_wait("try again in 1m30.5s") == pytest.approx(90.5)
    assert parse_wait("try again in 350ms") == pytest.approx(0.35)
    assert parse_wait("try again in 1h2m3s") == pytest.approx(3723)
    assert parse_wait("no hint here") is None


def test_hint_is_found_through_the_exception_chain_and_headers():
    assert suggested_wait(quota_exc()) == pytest.approx(2.505)
    e = LLMRateLimitExceeded("x")
    e.response = types.SimpleNamespace(headers={"retry-after": "7"})
    assert suggested_wait(e) == 7.0
    assert is_quota_error(quota_exc()) and not is_quota_error(ValueError("x"))


def test_wait_then_succeed_is_bounded_and_honours_hint():
    calls, slept = [], []
    def fn():
        calls.append(1)
        if len(calls) < 3:
            raise quota_exc()
        return "ok"
    assert call_with_quota_wait(fn, sleep=slept.append, log=lambda *_: None) == "ok"
    assert slept == [pytest.approx(3.005), pytest.approx(3.005)]


def test_gives_up_after_max_resumes_and_never_waits_out_long_limits():
    slept = []
    with pytest.raises(LLMRateLimitExceeded):
        call_with_quota_wait(lambda: (_ for _ in ()).throw(quota_exc()), max_resumes=2,
                             sleep=slept.append, log=lambda *_: None)
    assert len(slept) == 2                                       # bounded
    slept.clear()
    with pytest.raises(LLMRateLimitExceeded):                    # daily-style limit: stop, don't sleep
        call_with_quota_wait(lambda: (_ for _ in ()).throw(quota_exc("try again in 1h20m3s")),
                             sleep=slept.append, log=lambda *_: None)
    assert slept == []
    with pytest.raises(ValueError):                              # other errors are never swallowed
        call_with_quota_wait(lambda: (_ for _ in ()).throw(ValueError("bug")), sleep=slept.append)


def Q(i, qtype="simple"):
    return Question(id=f"q{i}", question=f"question number {i}?", qtype=qtype, reference_answer="a",
                    gold_chunk_ids=["c1"], gold_paper_ids=["p"], status="accepted")


class JudgeLLM:
    """Returns a passing verdict; raises a TPM-style rate limit on the Nth uncached call."""
    def __init__(self, fail_on=None, fail_times=1):
        self.n, self.fail_on, self.fail_times = 0, fail_on, fail_times

    def chat(self, messages, **kw):
        self.n += 1
        if self.fail_on is not None and self.fail_on <= self.n < self.fail_on + self.fail_times:
            raise quota_exc()
        return json.dumps({"answer_supported": True, "needs_all_passages": True,
                           "quantities_comparable": None, "same_quantity": None})


def test_audit_stops_cleanly_then_resumes_without_redoing_work(tmp_path):
    qs = [Q(i) for i in range(5)]
    out = tmp_path / "audit.jsonl"
    llm = JudgeLLM(fail_on=3, fail_times=1)
    r1 = run_audit(llm, qs, {"c1": "text"}, out)
    assert r1["new"] == 2 and r1["stopped"]["before_id"] == "q2" and r1["stopped"]["suggested_wait_s"] == pytest.approx(2.505)
    assert set(load_done(out)) == {"q0", "q1"}                    # partial work preserved
    r2 = run_audit(llm, qs, {"c1": "text"}, out)
    assert r2["already_done"] == 2 and r2["new"] == 3 and r2["stopped"] is None
    assert summarize(out, qs)["judged"] == 5 and summarize(out, qs)["passed"] == 5
    assert llm.n == 3 + 3                                         # 2 ok + 1 failed, then 3 more: nothing repeated


def test_audit_wait_mode_rides_out_a_tpm_limit(tmp_path):
    qs = [Q(i) for i in range(3)]
    slept = []
    r = run_audit(JudgeLLM(fail_on=2, fail_times=2), qs, {"c1": "t"}, tmp_path / "a.jsonl",
                  wait_on_rate_limit=True, sleep=slept.append, log=lambda *_: None)
    assert r["new"] == 3 and r["stopped"] is None and len(slept) == 2


def test_audit_non_rate_limit_errors_propagate(tmp_path):
    class Boom:
        def chat(self, *a, **k):
            raise RuntimeError("real bug")
    with pytest.raises(RuntimeError):
        run_audit(Boom(), [Q(0)], {"c1": "t"}, tmp_path / "a.jsonl")
