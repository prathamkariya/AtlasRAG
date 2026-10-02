from __future__ import annotations
import json
import re
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi

_tok = re.compile(r"\w+")


def tokenize(t: str) -> list[str]:
    return _tok.findall(t.lower())


def _topk(scores: np.ndarray, k: int) -> list[tuple[int, float]]:
    k = min(k, len(scores))
    top = np.argpartition(-scores, k - 1)[:k]
    top = top[np.argsort(-scores[top])]
    return [(int(i), float(scores[i])) for i in top]


class Index:
    """Dense (numpy cosine) + BM25 over chunks. Plenty for ~10^5 chunks and
    keeps Week 1 dependency-light; swap for pgvector later if needed."""

    def __init__(self, chunks: list[dict], emb: np.ndarray):
        self.chunks, self.emb = chunks, emb
        self._bm25 = BM25Okapi([tokenize(c["text"]) for c in chunks])

    @classmethod
    def build(cls, chunks, embedder, index_dir) -> "Index":
        index_dir = Path(index_dir)
        index_dir.mkdir(parents=True, exist_ok=True)
        texts = [f'{c["title"]} - {c["section"]}\n{c["text"]}' for c in chunks]
        emb = embedder.encode_docs(texts)
        np.save(index_dir / "emb.npy", emb)
        with open(index_dir / "chunks.jsonl", "w", encoding="utf-8") as f:
            for c in chunks:
                f.write(json.dumps(c) + "\n")
        return cls(chunks, emb)

    @classmethod
    def load(cls, index_dir) -> "Index":
        index_dir = Path(index_dir)
        emb = np.load(index_dir / "emb.npy")
        with open(index_dir / "chunks.jsonl", encoding="utf-8") as f:
            chunks = [json.loads(l) for l in f if l.strip()]
        return cls(chunks, emb)

    def dense(self, qvec: np.ndarray, k: int):
        return _topk(self.emb @ qvec, k)

    def bm25(self, query: str, k: int):
        return _topk(np.asarray(self._bm25.get_scores(tokenize(query))), k)
