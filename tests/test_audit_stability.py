import json
import math
from pathlib import Path

import pytest

from atlasrag.bench.audit_stability import (classify, summarize, collect, run_stability, write_report,
                                            STABLE_PASS, STABLE_FAIL, UNSTABLE)
from atlasrag.bench.schema import Question

ROOT = Path(__file__).resolve().parents[1]


def test_classify_and_agreement():
    v = {"a": [True, True, True], "b": [False, False], "c": [True, False], "d": []}
    assert classify(v) == {"a": STABLE_PASS, "b": STABLE_FAIL, "c": UNSTABLE}
    s = summarize({"a": [True, True], "c": [True, False]}, {"a": "simple", "c": "chain"})
    assert s["classes"] == {STABLE_PASS: 1, UNSTABLE: 1} and s["pairwise_agreement"] == 0.5
    assert s["by_type"] == {"chain": {UNSTABLE: 1}, "simple": {STABLE_PASS: 1}}
    assert math.isnan(summarize({}, {})["pairwise_agreement"])


def Q(i, qtype="simple"):
    return Question(id=f"q{i}", question=f"question number {i}?", qtype=qtype, reference_answer="a",
                    gold_chunk_ids=["c1"], gold_paper_ids=["p"], status="accepted")


class Judge:
    """Rep 1 passes everything; rep 2 fails every other question; rep 3 hits a rate limit on its 2nd call."""
    def __init__(self, ns):
        self.ns, self.n = ns, 0

    def chat(self, messages, **kw):
        self.n += 1
        if self.ns.endswith("r3") and self.n == 2:
            from atlasrag.llm import LLMRateLimitExceeded
            raise LLMRateLimitExceeded("rate limited after 3 attempts")
        ok = not (self.ns.endswith("r2") and self.n % 2 == 0)
        return json.dumps({"answer_supported": ok, "needs_all_passages": True,
                           "quantities_comparable": None, "same_quantity": None})


def test_run_stability_writes_one_file_per_rep_and_classifies(tmp_path):
    qs = [Q(i) for i in range(4)]
    res = run_stability(lambda ns: Judge(ns), qs, {"c1": "text"}, tmp_path, reps=2)
    assert res["stopped"] == []
    files = [tmp_path / "audit_stability_r1.jsonl", tmp_path / "audit_stability_r2.jsonl"]
    verdicts = collect(qs, files)
    cls = classify(verdicts)
    assert [cls[f"q{i}"] for i in range(4)] == [STABLE_PASS, UNSTABLE, STABLE_PASS, UNSTABLE]
    write_report(tmp_path / "s.json", summarize(verdicts, {q.id: q.qtype for q in qs}))
    assert json.loads((tmp_path / "s.json").read_text())["classes"][UNSTABLE] == 2


def test_rate_limit_stops_cleanly_and_unfinished_runs_do_not_bias_the_comparison(tmp_path):
    qs = [Q(i) for i in range(4)]
    res = run_stability(lambda ns: Judge(ns), qs, {"c1": "text"}, tmp_path, reps=3)
    assert len(res["stopped"]) == 1 and res["stopped"][0]["rep"] == 3
    files = [tmp_path / f"audit_stability_r{k}.jsonl" for k in (1, 2, 3)]
    verdicts = collect(qs, files)
    assert list(verdicts) == ["q0"]                       # only the one question every run actually judged
    assert len(verdicts["q0"]) == 3


def test_extra_existing_runs_are_included():
    qs = [Q(0), Q(1)]
    v = collect(qs, [], extra_runs=[{"q0": True, "q1": False}, {"q0": True, "q1": True}])
    assert classify(v) == {"q0": STABLE_PASS, "q1": UNSTABLE}


MAN, AUD = ROOT / "data/bench/v2_review_manifest.json", ROOT / "data/bench/audit.jsonl"


@pytest.mark.skipif(not (MAN.exists() and AUD.exists()), reason="repo audit data not present")
def test_recorded_audits_of_the_27_questions_disagree_as_measured():
    """Regression anchor for the measured instability: two audits, same judge, same 27 questions."""
    man = {r["id"]: r for r in json.load(open(MAN, encoding="utf-8"))}
    aud = {r["id"]: r for r in (json.loads(l) for l in open(AUD, encoding="utf-8") if l.strip())}
    if len(aud) < 27:
        pytest.skip("audit.jsonl incomplete")
    verdicts = {i: [man[i]["audit_ok"], aud[i]["ok"]] for i in man}
    nonsimple = {i: v for i, v in verdicts.items() if man[i]["qtype"] != "simple"}
    assert sum(classify(verdicts)[i] == UNSTABLE for i in verdicts) == 4
    cls = classify(nonsimple)
    assert (list(cls.values()).count(STABLE_PASS), list(cls.values()).count(STABLE_FAIL), list(cls.values()).count(UNSTABLE)) == (1, 5, 4)


def test_numeric_fraction():
    from atlasrag.bench.chunk_noise import numeric_fraction
    assert numeric_fraction("the Hubble constant is large") == 0.0
    assert numeric_fraction("0.0 0.5 1.0 z 60 90") == pytest.approx(5 / 6)
    assert numeric_fraction("") == 0.0
