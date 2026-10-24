import argparse, json, os, sys, tempfile
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

# Build/validate the new retrieval index before publishing processed chunks.
# If embedding or index validation fails, leave the previous processed chunks intact.
emb = Embedder(cfg["embedding"]["model"], cfg["embedding"]["query_prefix"])
Index.build(all_chunks, emb, resolve(cfg["retrieval"]["index_dir"]))

proc.mkdir(parents=True, exist_ok=True)
fd, temp_name = tempfile.mkstemp(prefix=".chunks.jsonl.", suffix=".tmp", dir=proc)
try:
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp_name, proc / "chunks.jsonl")
except BaseException:
    try:
        os.unlink(temp_name)
    except OSError:
        pass
    raise

print("index written to", resolve(cfg["retrieval"]["index_dir"]))
