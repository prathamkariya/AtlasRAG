"""End-to-end runs of scripts/gen_questions_v2.py with a fake LLM: budget stop, exit codes, run summaries, per-resume seeds."""
import json
import runpy
import sys
from pathlib import Path

import numpy as np
import pytest
import yaml

pytest.importorskip("rank_bm25")
pytest.importorskip("openai")
pytest.importorskip("tqdm")
from atlasrag.bench.budget import over_budget, tokens_used

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "gen_questions_v2.py"


def test_budget_functions():
    assert tokens_used({}) == 0 and tokens_used({"provider_prompt_tokens": 7, "provider_completion_tokens": 3}) == 10
    s = {"provider_prompt_tokens": 600, "provider_completion_tokens": 400}
    assert over_budget(s, 1000) and not over_budget(s, 1001) and not over_budget(s, 0) and not over_budget(s, -5)


class FakeEmbedder:
    def encode_docs(self, texts, batch_size=32):
        return np.random.RandomState(7).rand(len(texts), 4).astype("float32")


@pytest.fixture
def project(tmp_path, monkeypatch):
    from atlasrag.retrieval.index import Index
    import atlasrag.llm as L
    chunks = []
    for i in range(40):
        chunks.append({"chunk_id": f"p{i}::0", "paper_id": f"p{i}", "title": "T", "section": "Abstract",
                       "text": f"Hubble tension CMB LCDM H0 measurement abstract{i}alpha abstract{i}beta abstract{i}gamma " * 20})
        chunks.append({"chunk_id": f"p{i}::1", "paper_id": f"p{i}", "title": "T", "section": "Results",
                       "text": f"Hubble tension CMB LCDM H0 BAO DESI constraints results{i}delta results{i}epsilon results{i}zeta " * 15})
    Index.build(chunks, FakeEmbedder(), tmp_path / "index")
    (tmp_path / "raw").mkdir()
    cfg = yaml.safe_load((ROOT / "configs" / "default.yaml").read_text(encoding="utf-8"))
    cfg["corpus"]["raw_dir"] = str(tmp_path / "raw")
    cfg["retrieval"]["index_dir"] = str(tmp_path / "index")
    cfg["llm"]["cache_dir"] = str(tmp_path / "cache")
    (tmp_path / "cfg.yaml").write_text(yaml.safe_dump(cfg))
    monkeypatch.setenv("ATLAS_CONFIG", str(tmp_path / "cfg.yaml"))
    monkeypatch.setenv("GROQ_API_KEY", "x")
    monkeypatch.delenv("ATLAS_LLM_MODEL", raising=False)
    calls = {"n": 0}

    def fake_chat(self, messages, **kw):
        calls["n"] += 1
        for k, v in (("calls", 1), ("provider_calls", 1), ("cache_misses", 1),
                     ("provider_prompt_tokens", 600), ("provider_completion_tokens", 400)):
            self.stats[k] += v
        if "audit evaluation questions" in messages[0]["content"]:
            return json.dumps({"answer_supported": True, "needs_all_passages": True, "quantities_comparable": None,
                               "same_quantity": True, "passage_1_contribution": "A", "passage_2_contribution": "B", "joint_reason": "r"})
        return json.dumps({"question": f"What is the measured quantity number {calls['n']} reported in the study?",
                           "reference_answer": "It is X."})
    monkeypatch.setattr(L.LLMClient, "chat", fake_chat)
    return tmp_path


def run(monkeypatch, tmp, *extra):
    out = tmp / "q.jsonl"
    monkeypatch.setattr(sys, "argv", ["gen_questions_v2.py", "--split", "test", "--types", "simple", "--out", str(out), *extra])
    code = 0
    try:
        runpy.run_path(str(SCRIPT), run_name="__main__")
    except SystemExit as e:
        code = e.code or 0
    runs = [json.loads(l) for l in open(out.with_suffix(".runs.jsonl"), encoding="utf-8")]
    return code, runs, out


def test_normal_run_saves_questions_with_provenance_and_exits_zero(project, monkeypatch):
    code, runs, out = run(monkeypatch, project, "--per-type", "3", "--attempts", "5", "--model", "gen-m", "--judge-model", "judge-m")
    assert code == 0 and runs[-1]["stopped"] is None
    qs = [json.loads(l) for l in open(out, encoding="utf-8")]
    assert len(qs) == 3 and all(json.loads(q["validation"])["judge_model"] == "judge-m" for q in qs)
    assert runs[-1]["judge_model"] == "judge-m" and runs[-1]["seed_used"] == 1


def test_token_budget_stops_the_run_with_exit_code_4(project, monkeypatch):
    code, runs, out = run(monkeypatch, project, "--per-type", "20", "--attempts", "5", "--max-provider-tokens", "5000")
    assert code == 4
    r = runs[-1]
    assert r["stopped"]["reason"] == "token_budget" and 5000 <= r["stopped"]["tokens_used"] < 5000 + 2000   # at most one attempt over
    assert 0 < len([1 for _ in open(out)]) < 20                                                              # partial work was saved


def test_each_resume_gets_a_new_seed_so_attempts_are_not_replayed(project, monkeypatch):
    c1, r1, out = run(monkeypatch, project, "--per-type", "2", "--attempts", "5")
    c2, r2, _ = run(monkeypatch, project, "--per-type", "4", "--attempts", "5")
    assert (c1, c2) == (0, 0)
    assert r2[0]["seed_used"] == 1 and r2[1]["seed_used"] == 2                          # seed + number of earlier runs
    ids = [json.loads(l)["id"] for l in open(out, encoding="utf-8")]
    assert len(ids) == 4 and len(set(ids)) == 4                                          # the second run added NEW questions
