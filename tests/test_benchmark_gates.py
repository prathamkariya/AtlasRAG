import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from atlasrag.bench.schema import Question, save_questions, load_questions
from atlasrag.bench.review_meta import mark_review, review_mode
from atlasrag.bench.finalize import (finalize, gate_reasons, build_manifest, parse_minimums, check_minimums,
                                     norm_q, sha_text_bytes)
from atlasrag.bench.audit_stability import validation_run, collect, classify

ROOT = Path(__file__).resolve().parents[1]


def Q(i, qtype="simple", papers=("pA",), chunks=None, status="accepted", split="test", human=True,
      judge="gpt-oss-120b", gen="gpt-oss-20b", question=None):
    q = Question(id=f"q{i}", question=question or f"What is quantity number {i} in the study?", qtype=qtype,
                 reference_answer="a", gold_chunk_ids=chunks or ([f"c{i}"] if qtype == "simple" else [f"c{i}a", f"c{i}b"]),
                 gold_paper_ids=list(papers), status=status, split=split,
                 validation=json.dumps({"ok": True, "judge_model": judge, "generator_model": gen}) if judge else "")
    if human is not None:
        mark_review(q, "human" if human else "llm_assisted")
    return q


GOOD = {"verdicts": [True, True, True], "class": "stable_pass"}


def test_mark_review_records_the_last_decision_only():
    q = Q(0, human=None)
    assert review_mode(q) is None
    mark_review(q, "llm_assisted"); mark_review(q, "human")
    assert review_mode(q) == "human" and q.notes.count("review:") == 1
    q.notes = "kept note " + q.notes
    mark_review(q, "llm_assisted")
    assert q.notes.startswith("kept note") and review_mode(q) == "llm_assisted"
    with pytest.raises(ValueError):
        mark_review(q, "robot")


def test_every_gate_fires_by_name():
    st = {f"q{i}": dict(GOOD) for i in range(20)}
    assert gate_reasons(Q(0), st) == []
    assert "not_accepted" in gate_reasons(Q(1, status="candidate"), st)
    assert "not_test_split" in gate_reasons(Q(2, split="train"), st)
    assert "no_human_review" in gate_reasons(Q(3, human=False), st)
    assert "no_human_review" in gate_reasons(Q(4, human=None), st)
    assert gate_reasons(Q(3, human=False), st, require_human=False) == []
    assert "no_stability_record" in gate_reasons(Q(99), st)
    st["q5"] = {"verdicts": [True, False, True], "class": "unstable"}
    assert "judge_unstable" in gate_reasons(Q(5), st)
    st["q6"] = {"verdicts": [False, False, False], "class": "stable_fail"}
    assert "judge_stable_fail" in gate_reasons(Q(6), st)
    st["q7"] = {"verdicts": [True, True], "class": "stable_pass"}
    assert "too_few_judge_runs" in gate_reasons(Q(7), st, require_runs=3)
    assert "needs_two_papers" in gate_reasons(Q(8, "multi_hop", papers=("pA",)), st)
    assert gate_reasons(Q(9, "multi_hop", papers=("pA", "pB")), st) == []
    assert "too_few_gold_chunks" in gate_reasons(Q(10, "chain", chunks=["only"]), st)
    assert "chain_must_be_single_paper" in gate_reasons(Q(11, "chain", papers=("pA", "pB")), st)
    assert gate_reasons(Q(12, "chain", papers=("pA",)), st) == []
    assert "no_judge_model_recorded" in gate_reasons(Q(13, judge=None), st)
    assert "unknown_qtype" in gate_reasons(Q(14, "weird"), st)


def test_finalize_dedupes_and_reports_reasons():
    st = {f"q{i}": dict(GOOD) for i in range(6)}
    qs = [Q(0), Q(1, question="what is   quantity number 0 IN the study?"),       # same question, different spacing/case
          Q(2, chunks=["c0"]),                                                      # same gold set as q0
          Q(3, human=False), Q(4, status="rejected"), Q(5)]
    final, rej = finalize(qs, st)
    assert [q.id for q in final] == ["q0", "q5"]
    assert rej["q1"] == ["duplicate_question"] and rej["q2"] == ["duplicate_gold_set"]
    assert "no_human_review" in rej["q3"] and "not_accepted" in rej["q4"]
    assert norm_q("A  b!") == "a b"


def test_manifest_counts_and_self_judging_flag():
    st = {f"q{i}": dict(GOOD) for i in range(4)}
    qs = [Q(0, papers=("pA",)), Q(1, "multi_hop", ("pA", "pB")), Q(2, papers=("pA",), judge="gpt-oss-20b"), Q(3, "chain", ("pC",))]
    final, rej = finalize(qs, st)
    m = build_manifest("b1", final, rej, "hash", "chash", 3, "f.jsonl", "abc")
    assert m["n_questions"] == 4 and m["by_type"] == {"simple": 2, "multi_hop": 1, "chain": 1}
    assert m["n_distinct_papers"] == 3 and m["max_paper_share"] == 0.75           # q0, q1, q2 all start at paper pA: 3 of 4
    assert m["review_modes"] == {"human": 4}
    assert m["same_model_generated_and_judged"] is True                           # q2 was judged by its own generator
    assert m["judge_models"] == ["gpt-oss-120b", "gpt-oss-20b"]


def test_minimums():
    assert parse_minimums("simple=15, chain=10") == {"simple": 15, "chain": 10}
    assert check_minimums({"simple": 15, "chain": 3}, {"simple": 15, "chain": 10}) == ["chain: 3 < 10"]
    assert check_minimums({}, {}) == [] and parse_minimums("") == {}


def test_validation_run_and_new_files_need_no_baseline(tmp_path):
    qs = [Q(0), Q(1), Q(2, judge=None)]
    qs[1].validation = json.dumps({"ok": False, "judge_model": "m"})
    qs[2].validation = ""
    run = validation_run(qs)
    assert run == {"q0": True, "q1": False}                                       # missing/blank validation is simply absent
    old_baseline = {"some-old-id": True}                                          # an OLD run knows nothing about new ids
    assert collect(qs[:2], [], [old_baseline, run]) == {}                         # => mixing it in silently drops every new question
    v = collect(qs[:2], [], [run])
    assert classify(v) == {"q0": "stable_pass", "q1": "stable_fail"}


def test_cli_finalize_end_to_end_and_strict_exit_code(tmp_path):
    qs = [Q(i) for i in range(3)] + [Q(3, human=False)]
    src = tmp_path / "cand.jsonl"; save_questions(src, qs)
    stab = tmp_path / "stab.json"
    stab.write_text(json.dumps({"per_question": {f"q{i}": dict(GOOD) for i in range(4)}}))
    base = [sys.executable, str(ROOT / "scripts" / "finalize_benchmark.py"), "--file", str(src), "--stability", str(stab),
            "--benchmark-id", "t1", "--out-dir", str(tmp_path / "out"), "--corpus-manifest", str(tmp_path / "none.json")]
    r = subprocess.run(base + ["--min-per-type", "simple=2"], capture_output=True, text=True, cwd=ROOT,
                       env={"PYTHONPATH": str(ROOT / "src"), "PATH": "/usr/bin:/bin", "PYTHONUTF8": "1"})
    assert r.returncode == 0, r.stderr
    final = load_questions(tmp_path / "out" / "t1" / "questions_final.jsonl")
    assert [q.id for q in final] == ["q0", "q1", "q2"] and all(q.status == "accepted" for q in final)
    man = json.loads((tmp_path / "out" / "t1" / "benchmark_manifest.json").read_text())
    assert man["n_questions"] == 3 and man["rejected_by_reason"] == {"no_human_review": 1}
    r2 = subprocess.run(base + ["--min-per-type", "simple=5", "--strict"], capture_output=True, text=True, cwd=ROOT,
                        env={"PYTHONPATH": str(ROOT / "src"), "PATH": "/usr/bin:/bin", "PYTHONUTF8": "1"})
    assert r2.returncode == 3 and "simple: 3 < 5" in r2.stdout


def test_pilot_yield_summary(tmp_path):
    from atlasrag.bench.pilot_yield import load_last_run, summarize_run
    run = {"outcomes": {"attempt:multi_hop": 8, "survived:multi_hop": 1, "attempt:chain": 8, "survived:chain": 0,
                        "pair:multi_hop:no_shared_specific_signal": 40, "not_all_passages_needed": 3, "passed": 1},
           "llm": {"provider_prompt_tokens": 9000, "provider_completion_tokens": 3000, "provider_calls": 20, "rate_limit_errors": 2},
           "elapsed_s": 61.5, "model": "gen", "judge_model": "judge", "stopped": None}
    p = tmp_path / "r.jsonl"
    p.write_text(json.dumps({"outcomes": {}, "llm": {}}) + "\n" + json.dumps(run) + "\n")          # the LAST line is the run that counts
    s = summarize_run(load_last_run(p))
    assert s["per_type"]["multi_hop"] == {"attempts": 8, "survived": 1, "survival_rate": 0.125}
    assert s["per_type"]["chain"]["survived"] == 0 and s["total_survivors"] == 1
    assert s["tokens_per_survivor"] == 12000 and s["top_rejection_reasons"][0] == ("pair:multi_hop:no_shared_specific_signal", 40)
    empty = tmp_path / "e.jsonl"; empty.write_text("")
    with pytest.raises(ValueError):
        load_last_run(empty)
