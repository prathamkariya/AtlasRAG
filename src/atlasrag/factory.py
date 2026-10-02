"""Build a ready Pipeline from config (used by scripts)."""
from __future__ import annotations
from .config import resolve


def build_pipeline(cfg: dict):
    from .llm import LLMClient
    from .pipeline import Pipeline
    from .retrieval.embedder import Embedder
    from .retrieval.index import Index
    from .retrieval.reranker import Reranker
    index = Index.load(resolve(cfg["retrieval"]["index_dir"]))
    llm = LLMClient(cfg["llm"], cache_root=resolve(cfg["llm"]["cache_dir"]))
    pipe = Pipeline(cfg, index,
                    Embedder(cfg["embedding"]["model"], cfg["embedding"]["query_prefix"]),
                    llm, Reranker(cfg["reranker"]["model"]))
    return pipe, llm
