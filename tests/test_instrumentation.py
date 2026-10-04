"""Provider-quota counters and per-type generation funnel. Uses the real LLMClient / LLMRateLimitExceeded
and real openai exception types; no network."""
import json
import types

import httpx
import numpy as np
import pytest

openai = pytest.importorskip("openai")
pytest.importorskip("rank_bm25")
from atlasrag.llm import LLMClient, LLMRateLimitExceeded
from atlasrag.bench.generate_v2 import ValidatedGenerator
from atlasrag.retrieval.index import Index

REQ = httpx.Request("POST", "http://x")


def rate_limit_error():
    return openai.RateLimitError("429 TPM", response=httpx.Response(429, request=REQ), body=None)


def conn_error():
    return openai.APIConnectionError(request=REQ)


def resp(text="hello", pt=7, ct=3, finish="stop"):
    return types.SimpleNamespace(
        choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=text), finish_reason=finish)],
        usage=types.SimpleNamespace(prompt_tokens=pt, completion_tokens=ct))


class ScriptedAPI:
    """Pops one scripted outcome per create(): an Exception instance is raised, anything else returned."""
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.chat = types.SimpleNamespace(completions=types.SimpleNamespace(create=self.create))

    def create(self, **kw):
        o = self.outcomes.pop(0)
        if isinstance(o, Exception):
            raise o
        return o


def make(tmp_path, monkeypatch, outcomes, **over):
    monkeypatch.setenv("GROQ_API_KEY", "x")
    cfg = {"base_url": "http://x", "model": "m", "reasoning_effort": "low", "token_headroom": 400,
           "cache_namespace": "t", "max_retries": 2, "retry_base_seconds": 0.0, "retry_max_seconds": 0.0}
    cfg.update(over)
    llm = LLMClient(cfg, cache_root=tmp_path)
    llm.client = ScriptedAPI(outcomes)
    return llm


M = [{"role": "user", "content": "hi"}]


def test_success_counts_provider_quota_and_keeps_logical_accounting(tmp_path, monkeypatch):
    llm = make(tmp_path, monkeypatch, [resp()])
    assert llm.chat(M) == "hello"
    s = llm.stats
    assert (s["calls"], s["prompt_tokens"], s["completion_tokens"]) == (1, 7, 3)          # logical: unchanged semantics
    assert (s["provider_calls"], s["cache_misses"], s["cache_hits"], s["retry_attempts"]) == (1, 1, 0, 0)
    assert (s["provider_prompt_tokens"], s["provider_completion_tokens"]) == (7, 3)


def test_cache_hit_spends_no_provider_quota(tmp_path, monkeypatch):
    llm = make(tmp_path, monkeypatch, [resp()])
    llm.chat(M); llm.chat(M)
    s = llm.stats
    assert (s["calls"], s["cache_hits"], s["cache_misses"], s["provider_calls"]) == (2, 1, 1, 1)
    assert s["prompt_tokens"] == 14 and s["provider_prompt_tokens"] == 7                  # logical doubles, quota does not


def test_rate_limit_then_success_counts_retries(tmp_path, monkeypatch):
    llm = make(tmp_path, monkeypatch, [rate_limit_error(), rate_limit_error(), resp()])
    assert llm.chat(M) == "hello"
    s = llm.stats
    assert (s["provider_calls"], s["retry_attempts"], s["rate_limit_errors"], s["rate_limit_stops"]) == (3, 2, 2, 0)
    assert s["cache_misses"] == 1


def test_exhausted_rate_limit_is_counted_as_a_stop(tmp_path, monkeypatch):
    llm = make(tmp_path, monkeypatch, [rate_limit_error()] * 3)
    with pytest.raises(LLMRateLimitExceeded):
        llm.chat(M)
    s = llm.stats
    assert (s["provider_calls"], s["rate_limit_errors"], s["retry_attempts"], s["rate_limit_stops"]) == (3, 3, 2, 1)
    assert s["provider_prompt_tokens"] == 0 and s["prompt_tokens"] == 0                    # nothing was consumed


def test_connection_errors_counted_separately_and_not_as_rate_limit_stop(tmp_path, monkeypatch):
    llm = make(tmp_path, monkeypatch, [conn_error()] * 3)
    with pytest.raises(openai.APIConnectionError):
        llm.chat(M)
    s = llm.stats
    assert (s["connection_errors"], s["rate_limit_errors"], s["rate_limit_stops"]) == (3, 0, 0)


def test_empty_completion_still_counts_provider_tokens_but_not_logical(tmp_path, monkeypatch):
    llm = make(tmp_path, monkeypatch, [resp(text="", pt=9, ct=400, finish="length")])
    with pytest.raises(RuntimeError, match="token_headroom"):
        llm.chat(M)
    s = llm.stats
    assert s["empty_completions"] == 1
    assert (s["provider_prompt_tokens"], s["provider_completion_tokens"]) == (9, 400)       # the quota WAS spent
    assert (s["prompt_tokens"], s["completion_tokens"]) == (0, 0)                           # legacy behaviour preserved


def test_snapshot_exposes_new_counters_but_pipeline_deltas_use_only_legacy_keys(tmp_path, monkeypatch):
    llm = make(tmp_path, monkeypatch, [resp()])
    llm.chat(M)
    snap = llm.snapshot()
    assert {"provider_calls", "cache_misses", "rate_limit_errors"} <= set(snap)
    assert {"calls", "prompt_tokens", "completion_tokens", "cache_hits"} <= set(snap)


# ---------------- generator funnel ----------------
class JsonLLM:
    def chat(self, messages, **kw):
        if "audit evaluation questions" in messages[0]["content"]:
            return json.dumps({"answer_supported": True, "needs_all_passages": True,
                               "quantities_comparable": None, "same_quantity": True})
        return json.dumps({"question": "How do the two measurements of the expansion rate compare overall?",
                           "reference_answer": "They differ.", "passage_1_contribution": "fact from A",
                           "passage_2_contribution": "fact from B", "joint_reason": "both are needed",
                           "same_quantity": True})


def index_of(texts_by_paper):
    chunks = []
    for p, secs in texts_by_paper.items():
        for k, (sec, text) in enumerate(secs):
            chunks.append({"chunk_id": f"{p}::{k}", "paper_id": p, "title": "T", "section": sec, "text": text})
    return Index(chunks, np.random.RandomState(0).rand(len(chunks), 8).astype("float32"))


def test_funnel_counters_are_attributable_per_type():
    # unrelated vocabularies => cross-paper pairs die at the deterministic gate; chain pairs die at the section gate
    ix = index_of({f"p{i}": [("Abstract", f"alphaone{i} betatwo{i} " * 80), ("Introduction", f"gammathree{i} deltafour{i} " * 80)]
                   for i in range(40)})
    g = ValidatedGenerator(ix, JsonLLM(), {}, seed=1)
    n = 8
    for _ in range(n):
        g.make("multi_hop", "test")
    for _ in range(n):
        g.make("chain", "test")
    v = g.vstats
    assert v["attempt:multi_hop"] == n and v["attempt:chain"] == n
    assert v["survived:multi_hop"] == 0 and v["survived:chain"] == 0
    assert v["pair:multi_hop:no_shared_scientific_signal"] > 0
    assert v["pair:chain:no_evidence_section"] > 0
    assert "pair:multi_hop:no_evidence_section" not in v                                    # no cross-attribution
    # legacy mixed key still present, equal to the sum of the attributable ones for the same reason
    assert v["pair_no_shared_scientific_signal"] >= v["pair:multi_hop:no_shared_scientific_signal"]


def test_survivors_are_counted_per_type():
    ix = index_of({f"p{i}": [("Abstract", "Hubble tension CMB LCDM H0 measurement " * 40),
                              ("Results", "Hubble tension CMB LCDM H0 BAO DESI constraints " * 40)] for i in range(40)})
    g = ValidatedGenerator(ix, JsonLLM(), {}, seed=1)
    made = [q for q in (g.make("multi_hop", "test") for _ in range(12)) if q]
    assert g.vstats["attempt:multi_hop"] == 12 and g.vstats["survived:multi_hop"] == len(made) == g.vstats["passed"]
