import numpy as np
import pytest

pytest.importorskip("rank_bm25")
from atlasrag.config import load_config
from atlasrag.pipeline import Pipeline
from atlasrag.retrieval.index import Index
from atlasrag.routers import build_router


class FakeEmbedder:
    def encode_query(self, q):
        v = np.zeros(4, dtype="float32")
        v[hash(q) % 4] = 1.0
        return v


class FakeReranker:
    def rerank(self, q, chunks, top_k):
        return list(reversed(chunks))[:top_k]


class FakeLLM:
    def __init__(self):
        self.stats = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "cache_hits": 0}

    def snapshot(self):
        return dict(self.stats)

    def chat(self, messages, **kw):
        self.stats["calls"] += 1
        self.stats["prompt_tokens"] += 100
        self.stats["completion_tokens"] += 10
        sysmsg = messages[0]["content"]
        if "sub-questions" in sysmsg:
            return '["sub one", "sub two"]'
        if "route questions" in sysmsg:
            return '{"label": "MULTI_HOP", "confidence": 0.9}'
        return "An answer [1]."


def make_pipeline():
    cfg = load_config()
    chunks = [{"chunk_id": f"p::{i}", "paper_id": "p", "title": "T", "section": "S",
               "text": f"chunk number {i} about cosmology"} for i in range(30)]
    emb = np.random.RandomState(0).rand(30, 4).astype("float32")
    return Pipeline(cfg, Index(chunks, emb), FakeEmbedder(), FakeLLM(), FakeReranker()), cfg


def test_strategies_take_different_paths():
    pipe, cfg = make_pipeline()
    q = "Compare the studies."
    a = pipe.answer(q, build_router("vanilla", cfg))
    b = pipe.answer(q, build_router("static", cfg))
    h = pipe.answer(q, build_router("heuristic", cfg))
    c = pipe.answer(q, build_router("llm", cfg, llm=pipe.llm))
    assert a["metrics"]["llm_calls"] == 1 and len(a["citations"]) == 5      # dense only
    assert b["metrics"]["llm_calls"] == 1 and len(b["citations"]) == 8      # hybrid + rerank
    assert h["route"]["label"] == "MULTI_HOP" and h["metrics"]["llm_calls"] == 2   # decompose + answer
    assert c["metrics"]["llm_calls"] == 3                                   # route + decompose + answer
    assert c["subqueries"] == ["sub one", "sub two"]


def test_unknown_strategy_is_a_loud_error():
    pipe, cfg = make_pipeline()

    class Bad:
        name = "bad"
        def route(self, q):
            from atlasrag.routers.base import RouteDecision
            return RouteDecision("NOPE")
    with pytest.raises(KeyError):
        pipe.answer("q", Bad())
