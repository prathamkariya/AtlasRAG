"""One pipeline for ALL experiments. The router picks a strategy label; the
strategy table in the config decides what actually runs. Nothing else differs
between experiments A-E."""
from __future__ import annotations
import json
import re
import time
from dataclasses import asdict

from .retrieval.fusion import rrf

DECOMPOSE_PROMPT = ("Break the question into at most 3 standalone sub-questions that together "
                    "answer it, each searchable on its own. Reply with a JSON array of strings only.")
ANSWER_PROMPT = ("Answer the question using ONLY the numbered context passages from scientific papers. "
                 "Cite passages inline like [1] or [2][3]. If the passages do not contain enough "
                 "evidence, say so instead of guessing. If papers disagree, say that they disagree. Be concise.")


class Pipeline:
    def __init__(self, cfg: dict, index, embedder, llm, reranker=None):
        self.cfg, self.index, self.embedder, self.llm, self.reranker = cfg, index, embedder, llm, reranker

    # ---- steps ----
    def _decompose(self, query: str) -> list[str]:
        out = self.llm.chat([{"role": "system", "content": DECOMPOSE_PROMPT},
                             {"role": "user", "content": query}], max_tokens=200)
        m = re.search(r"\[.*\]", out, re.S)
        try:
            subs = [s for s in json.loads(m.group(0)) if isinstance(s, str) and s.strip()] if m else []
        except json.JSONDecodeError:
            subs = []
        return subs[:3] or [query]

    def _retrieve(self, queries: list[str], strat: dict, original: str) -> list[dict]:
        r = self.cfg["retrieval"]
        pool: dict[int, None] = {}
        for q in queries:
            dense = [i for i, _ in self.index.dense(self.embedder.encode_query(q), r["dense_k"])]
            if strat["use_hybrid"]:
                bm = [i for i, _ in self.index.bm25(q, r["bm25_k"])]
                dense = [i for i, _ in rrf([dense, bm], r["rrf_k"])][: r["dense_k"]]
            for i in dense:
                pool.setdefault(i, None)
        cands = [self.index.chunks[i] for i in pool]
        if strat["rerank"]:
            if self.reranker is None:
                raise RuntimeError("strategy requires a reranker but none was provided")
            return self.reranker.rerank(original, cands, strat["final_k"])
        return cands[: strat["final_k"]]

    def _generate(self, query: str, chunks: list[dict]) -> str:
        ctx = "\n\n".join(f'[{n}] ({c["title"]} - {c["section"]})\n{c["text"]}'
                          for n, c in enumerate(chunks, 1))
        return self.llm.chat([{"role": "system", "content": ANSWER_PROMPT},
                              {"role": "user", "content": f"Context:\n{ctx}\n\nQuestion: {query}"}],
                             max_tokens=500)

    # ---- entry points ----
    def _plan_and_retrieve(self, query: str, route):
        """route: a Router, or a strategy-label string (used by oracle labelling)."""
        from .routers.base import RouteDecision
        t0, s0 = time.perf_counter(), self.llm.snapshot()
        decision = RouteDecision(route, 1.0, "label") if isinstance(route, str) else route.route(query)
        if decision.label not in self.cfg["strategies"]:
            raise KeyError(f"router returned unknown strategy {decision.label!r}")
        strat = self.cfg["strategies"][decision.label]
        subqs = self._decompose(query) if strat["decompose"] else [query]
        chunks = self._retrieve(subqs, strat, query)
        return decision, subqs, chunks, t0, s0

    def _metrics(self, t0, s0) -> dict:
        s1 = self.llm.snapshot()
        return {
            "latency_s": round(time.perf_counter() - t0, 3),
            "llm_calls": s1["calls"] - s0["calls"],
            "prompt_tokens": s1["prompt_tokens"] - s0["prompt_tokens"],
            "completion_tokens": s1["completion_tokens"] - s0["completion_tokens"],
        }

    @staticmethod
    def _cites(chunks):
        return [{"n": n, "chunk_id": c["chunk_id"], "paper_id": c["paper_id"],
                 "title": c["title"], "section": c["section"]} for n, c in enumerate(chunks, 1)]

    def retrieve_only(self, query: str, route) -> dict:
        """Routing + retrieval, no answer generation. Cheap: used for oracle
        labelling and retrieval-side comparisons."""
        decision, subqs, chunks, t0, s0 = self._plan_and_retrieve(query, route)
        return {"question": query, "route": asdict(decision), "subqueries": subqs,
                "chunks": chunks, "citations": self._cites(chunks),
                "metrics": self._metrics(t0, s0)}

    def answer(self, query: str, router) -> dict:
        decision, subqs, chunks, t0, s0 = self._plan_and_retrieve(query, router)
        text = self._generate(query, chunks)
        return {"question": query, "answer": text, "route": asdict(decision),
                "subqueries": subqs, "citations": self._cites(chunks),
                "metrics": self._metrics(t0, s0)}
