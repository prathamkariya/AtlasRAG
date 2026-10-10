r"""Rebuild embeddings (emb.npy) from the committed chunks.jsonl. No PDFs needed.
  $env:ATLAS_CONFIG = "configs\corpus_v2.yaml"
  python scripts\rebuild_index_from_chunks.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from atlasrag.config import load_config, resolve
from atlasrag.retrieval.embedder import Embedder
from atlasrag.retrieval.rebuild import rebuild_index

cfg = load_config()
chunks = resolve(cfg["corpus"]["processed_dir"]) / "chunks.jsonl"
ix = rebuild_index(chunks, resolve(cfg["retrieval"]["index_dir"]), Embedder(cfg["embedding"]["model"], cfg["embedding"]["query_prefix"]))
print(f"rebuilt {len(ix.chunks)} chunks -> {resolve(cfg['retrieval']['index_dir'])} (model {cfg['embedding']['model']})")
