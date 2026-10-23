"""Find chunk text by chunk id across every available chunks.jsonl, active corpus first. A clean checkout has the committed
data/processed*/chunks.jsonl but NOT the generated data/index*/ folders; scripts that only need text must not require the index."""
from __future__ import annotations
import json
from pathlib import Path


def chunk_files(index_dir, processed_dir, root) -> list[Path]:
    cands = [Path(index_dir) / "chunks.jsonl", Path(processed_dir) / "chunks.jsonl",
             *sorted(Path(root).glob("data/processed*/chunks.jsonl"))]
    out, seen = [], set()
    for p in cands:
        if p.exists() and p.resolve() not in seen:
            out.append(p); seen.add(p.resolve())
    return out


def load_chunk_records(files) -> dict:
    """chunk_id -> record. The first file wins for a duplicated id, so list the active corpus first."""
    recs = {}
    for f in files:
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    c = json.loads(line)
                    recs.setdefault(c["chunk_id"], c)
    return recs
