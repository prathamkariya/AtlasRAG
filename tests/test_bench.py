import json
import math

import numpy as np
import pytest

pytest.importorskip("rank_bm25")
from atlasrag.bench.schema import Question, paper_split, load_questions, save_questions
from atlasrag.bench.metrics import evidence_recall, paper_recall, percentile
from atlasrag.bench.oracle import derive_oracle
from atlasrag.bench.runner import run_experiment
from atlasrag.bench.report import build_rows, bootstrap_ci, compare_groups, to_markdown
from atlasrag.bench.generate import Generator, parse_qa
from atlasrag.retrieval.index import Index
from atlasrag.routers import FixedRouter


def Q(i, qtype="simple", gold=("p1::0",), route=None):
    return Question(id=f"q{i}", question=f"question {i}?", qtype=qtype, reference_answer="a",
                    gold_chunk_ids=list(gold), gold_paper_ids=["p1"], status="accepted", gold_route=route)


def test_schema_roundtrip_and_filters(tmp_path):
    p = tmp_path / "q.jsonl"
    a, b = Q(1), Q(2)
    b.status, b.split = "rejected", "train"
    save_questions(p, [a, b])
    assert [q.id for q in load_questions(p)] == ["q1", "q2"]
    assert [q.id for q in load_questions(p, status="accepted")] == ["q1"]
    assert [q.id for q in load_questions(p, split="train")] == ["q2"]
    assert load_questions(tmp_path / "missing.jsonl") == []


def test_paper_split_deterministic_and_roughly_30pct():
    assert paper_split("2301.00001") == paper_split("2301.00001")
    frac = np.mean([paper_split(f"p{i}") == "test" for i in range(2000)])
    assert 0.25 < frac < 0.35


def test_metrics():
    assert evidence_recall(["a", "b"], ["a", "c"]) == 0.5
    assert math.isnan(evidence_recall([], ["a"]))
    assert paper_recall(["p"], ["p", "q"]) == 1.0
    assert percentile([1, 2, 3, 4], 50) == 2.5


class FakePipe:
    """SIMPLE retrieves the wrong chunk, MULTI_HOP the right one."""
    def __init__(self):
        self.llm = type("L", (), {"stats": {}})()

    def _res(self, q, label, calls):
        cid = "p1::0" if label != "SIMPLE" else "p1::9"
        return {"question": q, "route": {"label": label, "confidence": 1.0, "escalated": False},
                "subqueries": [q], "chunks": [{"chunk_id": cid}],
                "citations": [{"chunk_id": cid, "paper_id": "p1"}],
                "answer": "ans", "metrics": {"latency_s": 0.1, "llm_calls": calls,
                                              "prompt_tokens": 10, "completion_tokens": 5}}

    def retrieve_only(self, q, route):
        label = route if isinstance(route, str) else route.route(q).label
        return self._res(q, label, 1 if label != "SIMPLE" else 0)

    def answer(self, q, router):
        return self.retrieve_only(q, router)


def test_oracle_picks_cheapest_sufficient():
    qs = [Q(1)]
    out = derive_oracle(FakePipe(), qs)
    assert qs[0].gold_route == "MULTI_HOP" and qs[0].oracle_sufficient is True
    assert out["counts"]["MULTI_HOP"] == 1
    bad = [Q(2, gold=("zzz",))]
    derive_oracle(FakePipe(), bad)
    assert bad[0].gold_route == "UNCERTAIN" and bad[0].oracle_sufficient is False


def test_runner_resume_and_report(tmp_path):
    qs = [Q(1, "simple", route="MULTI_HOP"), Q(2, "multi_hop", route="MULTI_HOP")]
    out = tmp_path / "run1" / "B_static.jsonl"
    r1 = run_experiment(FakePipe(), FixedRouter("STATIC"), qs[:1], out)
    r2 = run_experiment(FakePipe(), FixedRouter("STATIC"), qs, out)
    assert r1["ran"] == 1 and r2["ran"] == 1 and r2["skipped"] == 1
    assert out.with_suffix(".meta.json").exists()
    rows = build_rows(tmp_path / "run1", qs)
    allrow = [r for r in rows if r["qtype"] == "ALL"][0]
    assert allrow["n"] == 2 and allrow["recall"] == 1.0
    assert "evidence recall" in to_markdown(rows)


def test_report_filters_result_rows_to_the_requested_benchmark_population(tmp_path):
    out = tmp_path / "run" / "A.jsonl"
    out.parent.mkdir()
    rows = [
        {"id": "keep", "qtype": "simple", "evidence_recall": 1.0,
         "route": {"label": "SIMPLE", "source": "x"},
         "metrics": {"latency_s": 0.1, "llm_calls": 0, "prompt_tokens": 0, "completion_tokens": 0}},
        {"id": "removed", "qtype": "simple", "evidence_recall": 0.0,
         "route": {"label": "SIMPLE", "source": "x"},
         "metrics": {"latency_s": 0.1, "llm_calls": 0, "prompt_tokens": 0, "completion_tokens": 0}},
    ]
    out.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    q = Q(1); q.id = "keep"
    report_row = build_rows(out.parent, [q])[0]
    assert report_row["n"] == 1 and report_row["recall"] == 1.0


def test_paired_report_filters_result_rows_to_the_requested_benchmark_population(tmp_path):
    from atlasrag.bench.report import paired_vs

    d = tmp_path / "run"
    d.mkdir()
    def row(question_id, recall):
        return json.dumps({"id": question_id, "qtype": "simple", "evidence_recall": recall,
                           "route": {"label": "SIMPLE", "source": "x"},
                           "metrics": {"latency_s": 0.1, "llm_calls": 0, "prompt_tokens": 0,
                                       "completion_tokens": 0}})
    (d / "F.jsonl").write_text(row("keep", 1.0) + "\n" + row("removed", 0.0) + "\n")
    (d / "A.jsonl").write_text(row("keep", 0.0) + "\n" + row("removed", 1.0) + "\n")
    q = Q(1); q.id = "keep"
    comparison = paired_vs(d, "F", questions=[q])
    assert comparison[0]["n"] == 1 and comparison[0]["mean_diff"] == -1.0


def test_bootstrap_and_stability(tmp_path):
    assert bootstrap_ci([0.5] * 10) == (0.5, 0.5, 0.5)
    assert all(math.isnan(x) for x in bootstrap_ci([]))
    for g, vals in (("g1", (1.0, 0.5)), ("g2", (0.9, 0.6))):
        for exp, v in zip(("A_x", "B_y"), vals):
            d = tmp_path / g
            d.mkdir(exist_ok=True)
            (d / f"{exp}.jsonl").write_text(json.dumps({"evidence_recall": v}) + "\n")
    cmp = compare_groups(tmp_path / "g1", tmp_path / "g2")
    assert cmp["ranking_stable"] is True
    (tmp_path / "g2" / "A_x.jsonl").write_text(json.dumps({"evidence_recall": 0.1}) + "\n")
    assert compare_groups(tmp_path / "g1", tmp_path / "g2")["ranking_stable"] is False


def test_parse_qa():
    assert parse_qa('{"question": "What is the Hubble constant value?", "reference_answer": "About 70."}')
    assert parse_qa('{"question": "NONE"}') is None
    assert parse_qa("garbage") is None


class GenLLM:
    def chat(self, messages, **kw):
        return json.dumps({"question": "How do the two measurements of the expansion rate compare?",
                           "reference_answer": "They differ."})


def test_generator_produces_split_consistent_questions():
    pids = [f"p{i}" for i in range(60)]
    chunks = [{"chunk_id": f"{p}::{k}", "paper_id": p, "title": "T",
               "section": "Abstract" if k == 0 else "Results", "text": "x " * 400}
              for p in pids for k in range(2)]
    emb = np.random.RandomState(0).rand(len(chunks), 8).astype("float32")
    meta = {p: {"published": f"2023-{1 + i % 12:02d}-01"} for i, p in enumerate(pids)}
    g = Generator(Index(chunks, emb), GenLLM(), meta, seed=1)
    for qt in ("simple", "multi_hop", "conflicting", "temporal", "chain"):
        for split in ("test", "train"):
            made = [q for q in (g.make(qt, split) for _ in range(40)) if q]
            assert made, (qt, split)
            for q in made:
                assert all(paper_split(p) == split for p in q.gold_paper_ids)
                assert q.status == "candidate" and q.gold_chunk_ids
                if qt in ("multi_hop", "conflicting", "temporal"):
                    assert len(q.gold_paper_ids) == 2
                if qt == "chain":
                    assert len(q.gold_paper_ids) == 1 and q.gold_chunk_ids[0].endswith("::0")


def test_paired_vs_and_fixed_routers_excluded_from_route_acc(tmp_path):
    from atlasrag.bench.report import paired_vs, paired_markdown
    d = tmp_path / "g"
    d.mkdir()
    def row(i, rec, src="x"):
        return json.dumps({"id": f"q{i}", "qtype": "simple", "evidence_recall": rec,
                           "route": {"label": "SIMPLE", "source": src},
                           "metrics": {"latency_s": 0.1, "llm_calls": 0, "prompt_tokens": 0, "completion_tokens": 0}})
    (d / "B_static.jsonl").write_text("\n".join(row(i, 0.5) for i in range(10)) + "\n")
    (d / "F_always.jsonl").write_text("\n".join(row(i, 1.0 if i < 6 else 0.5, "fixed:UNCERTAIN") for i in range(10)) + "\n")
    out = paired_vs(d, "B")
    assert len(out) == 1 and out[0]["wins"] == 6 and out[0]["ties"] == 4 and out[0]["losses"] == 0
    assert out[0]["lo"] > 0 and "yes" in paired_markdown(out)
    qs = [Q(i, route="SIMPLE") for i in range(10)]
    for q in qs:
        q.id = f"q{qs.index(q)}"
    rows = build_rows(d, qs)
    f_all = [r for r in rows if r["experiment"] == "F_always" and r["qtype"] == "ALL"][0]
    assert math.isnan(f_all["route_acc"])        # fixed routers never get a route accuracy


def test_control_routers_and_codes():
    from atlasrag.routers import build_router
    from atlasrag.bench.experiments import CODES, NAMES
    assert build_router("strongest", {}).route("q").label == "UNCERTAIN"
    assert build_router("multihop", {}).route("q").label == "MULTI_HOP"
    assert build_router("static_k10", {}).route("q").label == "STATIC_K10"
    assert set(CODES) == set(NAMES) >= {"F", "G", "K"}


def test_chunking_tail_merge_regression():
    """Original bug: chunks[-2] += chunks.pop() raised IndexError for 2 chunks and
    silently overwrote the wrong chunk for 3+."""
    from atlasrag.ingest.chunking import chunk_section
    big = "word " * 90                       # ~450 chars each
    text = "\n\n".join([big, big, "tiny tail"])
    out = chunk_section(text, max_chars=500, overlap_chars=50, min_chars=200)
    assert out[-1].endswith("tiny tail") and len(out) == 2
    assert out[0].strip() == big.strip()    # first chunk untouched
    out2 = chunk_section("\n\n".join([big, "tiny tail"]), max_chars=500, overlap_chars=50, min_chars=200)
    assert len(out2) == 1 and "tiny tail" in out2[0]
