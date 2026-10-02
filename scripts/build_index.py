import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tqdm import tqdm
from atlasrag.config import load_config, resolve
from atlasrag.ingest.pdf_parse import extract_text, split_sections
from atlasrag.ingest.chunking import build_chunks
from atlasrag.retrieval.embedder import Embedder
from atlasrag.retrieval.index import Index

cfg = load_config()
raw = resolve(cfg["corpus"]["raw_dir"])
proc = resolve(cfg["corpus"]["processed_dir"])
proc.mkdir(parents=True, exist_ok=True)

records = [json.loads(l) for l in open(raw / "metadata.jsonl", encoding="utf-8") if l.strip()]
all_chunks, failed = [], []
for rec in tqdm(records, desc="parsing"):
    try:
        sections = split_sections(extract_text(rec["pdf_path"]))
    except Exception as e:                      # corrupt/odd PDFs happen
        failed.append((rec["id"], str(e)))
        continue
    # trust the metadata abstract over the PDF front matter (title/affiliation noise)
    sections = [("Abstract", rec["abstract"])] + [s for s in sections if s[0] not in ("Front matter", "Abstract")]
    all_chunks += build_chunks(rec["id"], rec["title"], sections, cfg["chunking"])

with open(proc / "chunks.jsonl", "w", encoding="utf-8") as f:
    for c in all_chunks:
        f.write(json.dumps(c) + "\n")
print(f"{len(records)-len(failed)} papers -> {len(all_chunks)} chunks ({len(failed)} failed)")
for pid, err in failed[:10]:
    print("  failed:", pid, err)

emb = Embedder(cfg["embedding"]["model"], cfg["embedding"]["query_prefix"])
Index.build(all_chunks, emb, resolve(cfg["retrieval"]["index_dir"]))
print("index written to", resolve(cfg["retrieval"]["index_dir"]))
