import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tqdm import tqdm
from atlasrag.config import load_config, resolve
from atlasrag.ingest.corpus_build import parse_records
from atlasrag.retrieval.embedder import Embedder
from atlasrag.retrieval.index import Index

ap = argparse.ArgumentParser()
ap.add_argument("--allow-missing", action="store_true",
                help="write chunks even if some PDFs are missing/unparseable (DANGEROUS: produces an incomplete corpus)")
a = ap.parse_args()

cfg = load_config()
raw = resolve(cfg["corpus"]["raw_dir"])
proc = resolve(cfg["corpus"]["processed_dir"])

records = [json.loads(l) for l in open(raw / "metadata.jsonl", encoding="utf-8") if l.strip()]
all_chunks, failed = parse_records(records, raw, cfg["chunking"], progress=lambda r: tqdm(r, desc="parsing"))
print(f"{len(records) - len(failed)} papers -> {len(all_chunks)} chunks ({len(failed)} failed)")
for pid, err in failed[:10]:
    print("  failed:", pid, err)
if failed and not a.allow_missing:
    sys.exit(f"ABORT: {len(failed)} of {len(records)} papers could not be parsed. NOTHING was written (existing chunks.jsonl and "
             f"index are untouched). Fix the cause (usually: python scripts\\refetch_pdfs.py), or pass --allow-missing if you really want a partial corpus.")

proc.mkdir(parents=True, exist_ok=True)
with open(proc / "chunks.jsonl", "w", encoding="utf-8") as f:
    for c in all_chunks:
        f.write(json.dumps(c) + "\n")

emb = Embedder(cfg["embedding"]["model"], cfg["embedding"]["query_prefix"])
Index.build(all_chunks, emb, resolve(cfg["retrieval"]["index_dir"]))
print("index written to", resolve(cfg["retrieval"]["index_dir"]))
