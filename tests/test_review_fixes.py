"""One regression test per finding from the independent (Codex) review of PRs #3 and #4, plus the agent's own review notes."""
import json
import runpy
import sys
from pathlib import Path

import numpy as np
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def Qn(i, gen="gen-m", judge="judge-m", papers=("pA",), qtype="simple", prov=True):
    from atlasrag.bench.schema import Question
    from atlasrag.bench.review_meta import mark_review
    q = Question(id=f"q{i}", question=f"Distinct question number {i} about quantity {i}?", qtype=qtype, reference_answer="a",
                 gold_chunk_ids=[f"c{i}"] if qtype == "simple" else [f"c{i}a", f"c{i}b"], gold_paper_ids=list(papers),
                 status="accepted", split="test",
                 validation=json.dumps({"ok": True, "generator_model": gen, "judge_model": judge}) if prov else "")
    mark_review(q, "human")
    return q


GOOD = {"verdicts": [True, True, True], "class": "stable_pass"}


# ---- F1 (P1): PDF location comes from the active raw dir, and a partial corpus is never written silently ----
def test_resolve_pdf_prefers_the_active_raw_dir_over_a_stale_absolute_path(tmp_path):
    from atlasrag.ingest.corpus_build import resolve_pdf
    (tmp_path / "pdf").mkdir()
    (tmp_path / "pdf" / "p1.pdf").write_bytes(b"x")
    stale = {"id": "p1", "pdf_path": r"D:\Pratham\coding\projects\AtlasRAG\data\raw\pdf\p1.pdf"}
    assert resolve_pdf(stale, tmp_path) == tmp_path / "pdf" / "p1.pdf"
    elsewhere = tmp_path / "other.pdf"; elsewhere.write_bytes(b"y")
    assert resolve_pdf({"id": "p9", "pdf_path": str(elsewhere)}, tmp_path) == elsewhere           # explicit path still works as a fallback
    assert resolve_pdf({"id": "nope", "pdf_path": r"D:\gone.pdf"}, tmp_path) is None


def test_parse_records_reports_missing_pdfs_instead_of_skipping_them(tmp_path):
    from atlasrag.ingest.corpus_build import parse_records
    (tmp_path / "pdf").mkdir(); (tmp_path / "pdf" / "a.pdf").write_bytes(b"x")
    recs = [{"id": "a", "title": "A", "abstract": "abs " * 80, "pdf_path": r"D:\stale\a.pdf"},
            {"id": "b", "title": "B", "abstract": "abs " * 80, "pdf_path": r"D:\stale\b.pdf"}]
    cfg = {"max_chars": 1800, "overlap_chars": 200, "min_chars": 200}
    chunks, failed = parse_records(recs, tmp_path, cfg, extract=lambda p: "1 Introduction\n\nSome real body text. " * 30)
    assert {c["paper_id"] for c in chunks} == {"a"} and [f[0] for f in failed] == ["b"] and "refetch_pdfs" in failed[0][1]


@pytest.fixture
def mini_project(tmp_path, monkeypatch):
    raw = tmp_path / "raw"; (raw / "pdf").mkdir(parents=True)
    recs = [{"id": f"p{i}", "title": f"T{i}", "abstract": "abs " * 80, "published": "2024-01-01T00:00:00",
             "pdf_url": "u", "pdf_path": rf"D:\stale\p{i}.pdf"} for i in range(3)]
    (raw / "metadata.jsonl").write_text("\n".join(json.dumps(r) for r in recs) + "\n")
    for i in (0, 1):                                                                        # p2's PDF is MISSING
        (raw / "pdf" / f"p{i}.pdf").write_bytes(b"x")
    cfg = yaml.safe_load((ROOT / "configs" / "default.yaml").read_text(encoding="utf-8"))
    cfg["corpus"].update({"raw_dir": str(raw), "processed_dir": str(tmp_path / "proc")})
    cfg["retrieval"]["index_dir"] = str(tmp_path / "index")
    cfg["llm"]["cache_dir"] = str(tmp_path / "cache")
    (tmp_path / "cfg.yaml").write_text(yaml.safe_dump(cfg))
    monkeypatch.setenv("ATLAS_CONFIG", str(tmp_path / "cfg.yaml"))
    import atlasrag.ingest.pdf_parse as pp
    import atlasrag.retrieval.embedder as em
    monkeypatch.setattr(pp, "extract_text", lambda p: "1 Introduction\n\nSome real body text. " * 30)

    class FakeEmb:
        def __init__(self, *a, **k): pass
        def encode_docs(self, texts, batch_size=32): return np.zeros((len(texts), 4), dtype="float32")
    monkeypatch.setattr(em, "Embedder", FakeEmb)
    return tmp_path


def run_build(monkeypatch, *extra):
    pytest.importorskip("tqdm"); pytest.importorskip("rank_bm25")
    monkeypatch.setattr(sys, "argv", ["build_index.py", *extra])
    try:
        runpy.run_path(str(ROOT / "scripts" / "build_index.py"), run_name="__main__")
        return 0
    except SystemExit as e:
        return e.code


def test_build_index_aborts_without_writing_when_a_pdf_is_missing(mini_project, monkeypatch):
    out = run_build(monkeypatch)
    assert isinstance(out, str) and "ABORT" in out and "NOTHING was written" in out
    assert not (mini_project / "proc" / "chunks.jsonl").exists() and not (mini_project / "index").exists()


def test_build_index_allow_missing_writes_a_partial_corpus_on_request(mini_project, monkeypatch):
    assert run_build(monkeypatch, "--allow-missing") == 0
    ids = {json.loads(l)["paper_id"] for l in open(mini_project / "proc" / "chunks.jsonl")}
    assert ids == {"p0", "p1"}


# ---- F2 (P2) + agent finding 1: chunk text from committed chunks when the index is absent, across corpora ----
def test_chunk_text_falls_back_to_processed_chunks_and_prefers_the_active_corpus(tmp_path):
    from atlasrag.chunk_text import chunk_files, load_chunk_records
    for d, text in (("processed", "v1 text"), ("processed_v2", "v2 text")):
        (tmp_path / "data" / d).mkdir(parents=True)
        (tmp_path / "data" / d / "chunks.jsonl").write_text(json.dumps({"chunk_id": "p::0", "title": "T", "section": "S", "text": text}) + "\n")
    (tmp_path / "data" / "processed_v2" / "chunks.jsonl").open("a").write(json.dumps({"chunk_id": "only_v2::0", "title": "T", "section": "S", "text": "z"}) + "\n")
    files = chunk_files(tmp_path / "data" / "index_v2",                     # the index folder does not exist (clean checkout)
                        tmp_path / "data" / "processed_v2", tmp_path)
    assert [f.parent.name for f in files] == ["processed_v2", "processed"]
    recs = load_chunk_records(files)
    assert recs["p::0"]["text"] == "v2 text" and "only_v2::0" in recs        # active corpus wins; ids from the other corpus still resolve
    assert load_chunk_records(chunk_files(tmp_path / "nope", tmp_path / "nope2", tmp_path / "empty")) == {}


# ---- F3 (P1): the stability repetitions must not be judged by the generator ----
def test_self_judge_conflicts_detects_the_generator_as_judge():
    from atlasrag.bench.audit_stability import self_judge_conflicts
    qs = [Qn(0, gen="gpt-oss-20b"), Qn(1, gen="gpt-oss-120b"), Qn(2, prov=False)]
    assert self_judge_conflicts(qs, "gpt-oss-20b") == ["q0"]
    assert self_judge_conflicts(qs, "other") == []


def test_audit_stability_cli_refuses_to_self_judge_and_records_the_judge_model(tmp_path, monkeypatch):
    pytest.importorskip("tqdm"); pytest.importorskip("openai")
    from atlasrag.bench.schema import save_questions
    import atlasrag.llm as L
    (tmp_path / "data").mkdir()
    (tmp_path / "idx").mkdir()
    chunks = [{"chunk_id": f"c0{s}", "paper_id": "pA", "title": "T", "section": "Results", "text": "text " * 50} for s in "ab"]
    (tmp_path / "idx" / "chunks.jsonl").write_text("\n".join(json.dumps(c) for c in chunks) + "\n")
    q = Qn(0, gen="openai/gpt-oss-20b", judge="openai/gpt-oss-120b", papers=("pA", "pB"), qtype="multi_hop")
    q.gold_chunk_ids = ["c0a", "c0b"]
    save_questions(tmp_path / "q.jsonl", [q])
    cfg = yaml.safe_load((ROOT / "configs" / "default.yaml").read_text(encoding="utf-8"))
    cfg["retrieval"]["index_dir"] = str(tmp_path / "idx"); cfg["corpus"]["processed_dir"] = str(tmp_path / "none")
    cfg["llm"]["cache_dir"] = str(tmp_path / "cache")
    (tmp_path / "cfg.yaml").write_text(yaml.safe_dump(cfg))
    monkeypatch.setenv("ATLAS_CONFIG", str(tmp_path / "cfg.yaml")); monkeypatch.setenv("GROQ_API_KEY", "x")
    monkeypatch.setattr(L.LLMClient, "chat", lambda self, m, **k: json.dumps(
        {"answer_supported": True, "needs_all_passages": True, "same_quantity": True, "quantities_comparable": None,
         "passage_1_contribution": "A", "passage_2_contribution": "B", "joint_reason": "r"}))
    base = ["audit_stability.py", "--file", str(tmp_path / "q.jsonl"), "--status", "accepted", "--all", "--no-baseline",
            "--include-validation", "--reps", "2", "--out-dir", str(tmp_path / "out")]
    monkeypatch.setattr(sys, "argv", base)                                             # no --model => config default = the generator
    with pytest.raises(SystemExit) as e:
        runpy.run_path(str(ROOT / "scripts" / "audit_stability.py"), run_name="__main__")
    assert "REFUSING" in str(e.value) and "openai/gpt-oss-20b" in str(e.value)
    monkeypatch.setattr(sys, "argv", base + ["--model", "openai/gpt-oss-120b"])
    runpy.run_path(str(ROOT / "scripts" / "audit_stability.py"), run_name="__main__")
    doc = json.loads((tmp_path / "out" / "audit_stability.json").read_text())
    assert doc["judge_model"] == "openai/gpt-oss-120b" and doc["questions"] == 1


def test_finalize_blocks_questions_whose_stability_judge_was_their_generator():
    from atlasrag.bench.finalize import finalize, build_manifest
    st = {f"q{i}": dict(GOOD) for i in range(2)}
    qs = [Qn(0, gen="gpt-oss-20b"), Qn(1, gen="gpt-oss-120b")]
    final, rej = finalize(qs, st, stability_model="gpt-oss-20b")
    assert [q.id for q in final] == ["q1"] and rej["q0"] == ["stability_self_judged"]
    assert build_manifest("b", final, rej, "h", stability_model="gpt-oss-20b")["stability_judge_model"] == "gpt-oss-20b"
    assert [q.id for q in finalize(qs, st)[0]] == ["q0", "q1"]                          # old stability files (no model recorded) still work


# ---- F5 (P2): concentration counts a paper in ANY position ----
def test_max_paper_share_counts_every_membership_not_just_the_first_paper():
    from atlasrag.bench.finalize import finalize, build_manifest
    qs = [Qn(i, papers=(f"first{i}", "common"), qtype="multi_hop") for i in range(5)]
    final, rej = finalize(qs, {q.id: dict(GOOD) for q in qs})
    m = build_manifest("b", final, rej, "h")
    assert m["max_paper_share"] == 1.0                      # every question involves 'common'
    assert m["max_paper_share_first_paper"] == 0.2          # the old, bypassable definition


# ---- F6 (P2): self-judging is decided per question ----
def test_self_judging_is_per_question_not_set_overlap():
    from atlasrag.bench.finalize import finalize, build_manifest
    qs = [Qn(0, gen="A", judge="B"), Qn(1, gen="B", judge="C")]                          # nobody judged their own question
    final, rej = finalize(qs, {q.id: dict(GOOD) for q in qs})
    m = build_manifest("b", final, rej, "h")
    assert m["same_model_generated_and_judged"] is False and m["self_judged_questions"] == 0
    qs2 = qs + [Qn(2, gen="X", judge="X")]
    final2, rej2 = finalize(qs2, {q.id: dict(GOOD) for q in qs2})
    m2 = build_manifest("b", final2, rej2, "h")
    assert m2["same_model_generated_and_judged"] is True and m2["self_judged_questions"] == 1


# ---- F7 (P2): a token-budget stop is not a rate-limit stop ----
def test_pilot_summary_separates_rate_limit_and_token_budget_stops():
    from atlasrag.bench.pilot_yield import summarize_pilot
    runs = [{"stopped": {"reason": "rate_limited"}}, {"stopped": {"reason": "token_budget"}}, {"stopped": None}, {}]
    s = summarize_pilot(runs, [])
    assert s["runs_stopped_by_rate_limit"] == 1 and s["runs_stopped_by_token_budget"] == 1


# ---- F8 (P2): record the ACTUAL model names, never a placeholder ----
class _LLM:
    model = "openai/gpt-oss-20b"                              # what LLMClient exposes: the configured model

    def chat(self, messages, **kw):
        if "audit evaluation questions" in messages[0]["content"]:
            return json.dumps({"answer_supported": True})
        return json.dumps({"question": "What quantity does the study report for the expansion rate?", "reference_answer": "X."})


def test_provenance_records_the_configured_model_when_model_is_omitted():
    from atlasrag.bench.generate_v2 import ValidatedGenerator
    from atlasrag.retrieval.index import Index
    chunks = [{"chunk_id": f"p{i}::0", "paper_id": f"p{i}", "title": "T", "section": "Abstract", "text": f"word{i} " * 200} for i in range(40)]
    ix = Index(chunks, np.random.RandomState(0).rand(len(chunks), 4).astype("float32"))
    g = ValidatedGenerator(ix, _LLM(), {}, seed=1)                                      # no model=, no judge_model=
    q = next(x for x in (g.make("simple", "test") for _ in range(40)) if x)
    v = json.loads(q.validation)
    assert v["generator_model"] == "openai/gpt-oss-20b" and v["judge_model"] == "openai/gpt-oss-20b"
    g2 = ValidatedGenerator(ix, _LLM(), {}, seed=1, judge_model="openai/gpt-oss-120b")
    q2 = next(x for x in (g2.make("simple", "test") for _ in range(40)) if x)
    assert json.loads(q2.validation)["judge_model"] == "openai/gpt-oss-120b"


def test_placeholder_model_names_do_not_count_as_provenance():
    from atlasrag.bench.finalize import gate_reasons
    for bad in ("config-default", "unknown", ""):
        q = Qn(0, judge=bad)
        assert "no_judge_model_recorded" in gate_reasons(q, {"q0": dict(GOOD)}), bad
    assert "no_judge_model_recorded" not in gate_reasons(Qn(0), {"q0": dict(GOOD)})


# ---- the human review step must SHOW the evidence, from committed chunks, whatever config is active ----
def test_interactive_review_shows_passages_without_an_index_and_records_a_human_decision(tmp_path, monkeypatch, capsys):
    import builtins
    from atlasrag.bench.schema import Question, save_questions, load_questions
    proc = tmp_path / "proc"; proc.mkdir()
    (proc / "chunks.jsonl").write_text(json.dumps({"chunk_id": "c0", "paper_id": "pA", "title": "A Paper", "section": "Results",
                                                   "text": "UNIQUE-PASSAGE-TEXT about the expansion rate " * 5}) + "\n")
    q = Question(id="q0", question="What does the paper measure about the expansion rate?", qtype="simple", reference_answer="X",
                 gold_chunk_ids=["c0"], gold_paper_ids=["pA"], status="candidate", split="test")
    q2 = Question(id="q1", question="A question whose evidence chunk is missing entirely?", qtype="simple", reference_answer="Y",
                  gold_chunk_ids=["missing-chunk"], gold_paper_ids=["pB"], status="candidate", split="test")
    save_questions(tmp_path / "q.jsonl", [q, q2])
    cfg = yaml.safe_load((ROOT / "configs" / "default.yaml").read_text(encoding="utf-8"))
    cfg["retrieval"]["index_dir"] = str(tmp_path / "no_index_here")            # a clean checkout has no index folder
    cfg["corpus"]["processed_dir"] = str(proc)
    (tmp_path / "cfg.yaml").write_text(yaml.safe_dump(cfg))
    monkeypatch.setenv("ATLAS_CONFIG", str(tmp_path / "cfg.yaml"))
    answers = iter(["a", "r"])
    monkeypatch.setattr(builtins, "input", lambda *a, **k: next(answers))
    monkeypatch.setattr(sys, "argv", ["review_questions.py", "--config", str(tmp_path / "cfg.yaml"),
                                        "--file", str(tmp_path / "q.jsonl"), "--split", "test"])
    try:
        runpy.run_path(str(ROOT / "scripts" / "review_questions.py"), run_name="__main__")
    except SystemExit:
        pass
    out = capsys.readouterr().out
    assert "UNIQUE-PASSAGE-TEXT" in out                                           # the reviewer can actually read the evidence
    assert "passage text for missing-chunk was NOT FOUND" in out                  # and is warned loudly when it is not there
    done = {x.id: x for x in load_questions(tmp_path / "q.jsonl")}
    assert done["q0"].status == "accepted" and "review:human" in done["q0"].notes
    assert done["q1"].status == "rejected" and "review:human" in done["q1"].notes


# ---- the human-review step must show the passages even with the default config and no index folder ----
def _review_project(tmp_path, monkeypatch, with_chunks=True):
    from atlasrag.bench.schema import Question, save_questions
    (tmp_path / "proc").mkdir()
    if with_chunks:
        (tmp_path / "proc" / "chunks.jsonl").write_text(json.dumps(
            {"chunk_id": "c0", "paper_id": "pA", "title": "A Title", "section": "Results", "text": "UNIQUE-PASSAGE-TEXT about H0."}) + "\n")
    q = Question(id="q0", question="What does the study report about the expansion rate?", qtype="simple", reference_answer="X.",
                 gold_chunk_ids=["c0"], gold_paper_ids=["pA"], status="candidate", split="test")
    save_questions(tmp_path / "q.jsonl", [q])
    cfg = yaml.safe_load((ROOT / "configs" / "default.yaml").read_text(encoding="utf-8"))
    cfg["retrieval"]["index_dir"] = str(tmp_path / "no_index_here")
    cfg["corpus"]["processed_dir"] = str(tmp_path / "proc")
    (tmp_path / "cfg.yaml").write_text(yaml.safe_dump(cfg))
    monkeypatch.setenv("ATLAS_CONFIG", str(tmp_path / "cfg.yaml"))
    answers = iter(["a", "q", "q"])
    monkeypatch.setattr("builtins.input", lambda *a, **k: next(answers))
    monkeypatch.setattr(sys, "argv", ["review_questions.py", "--file", str(tmp_path / "q.jsonl"), "--split", "test"])


def test_review_shows_passages_from_committed_chunks_when_the_index_is_absent(tmp_path, monkeypatch, capsys):
    from atlasrag.bench.schema import load_questions
    _review_project(tmp_path, monkeypatch)
    try:
        runpy.run_path(str(ROOT / "scripts" / "review_questions.py"), run_name="__main__")
    except SystemExit:
        pass
    out = capsys.readouterr().out
    assert "UNIQUE-PASSAGE-TEXT" in out and "WARNING" not in out
    q = load_questions(tmp_path / "q.jsonl")[0]
    assert q.status == "accepted" and "review:human" in q.notes              # an interactive decision is recorded as human


def test_review_warns_loudly_when_a_passage_cannot_be_found(tmp_path, monkeypatch, capsys):
    """The repo's own committed data/processed*/chunks.jsonl are always searched, so 'no chunks at all' cannot happen in a checkout;
    the real risk is a chunk id that exists in NO file. The reviewer must be told, not shown a blank."""
    _review_project(tmp_path, monkeypatch, with_chunks=False)
    try:
        runpy.run_path(str(ROOT / "scripts" / "review_questions.py"), run_name="__main__")
    except SystemExit:
        pass
    out = capsys.readouterr().out
    assert "WARNING" in out and "NOT FOUND" in out and "c0" in out
