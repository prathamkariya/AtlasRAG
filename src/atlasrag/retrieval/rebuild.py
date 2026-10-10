"""Rebuild the embedding index from the committed chunks.jsonl, with NO PDFs needed."""
from __future__ import annotations
import json
from pathlib import Path

from .index import Index


def rebuild_index(chunks_path, index_dir, embedder) -> Index:
    chunks = [json.loads(l) for l in open(chunks_path, encoding="utf-8") if l.strip()]
    if not chunks:
        raise ValueError(f"{chunks_path} is empty")
    ids = [c["chunk_id"] for c in chunks]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate chunk ids in chunks.jsonl")
    return Index.build(chunks, embedder, Path(index_dir))
