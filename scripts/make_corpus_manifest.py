r"""Write or verify a corpus manifest.
  $env:ATLAS_CONFIG = "configs\corpus_v2.yaml"
  python scripts\make_corpus_manifest.py --id atlasrag-corpus-v2          # writes corpus\manifests\atlasrag-corpus-v2.json
  python scripts\make_corpus_manifest.py --verify corpus\manifests\atlasrag-corpus-v2.json
--verify exits 1 if metadata.jsonl or chunks.jsonl drifted from the manifest; missing PDFs are only a warning."""
import argparse, json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from atlasrag.config import load_config, resolve
from atlasrag.corpus_manifest import build_manifest, verify_manifest

ap = argparse.ArgumentParser()
ap.add_argument("--id", help="corpus id to write a manifest for")
ap.add_argument("--verify", help="manifest JSON to verify against the active config's files")
a = ap.parse_args()
cfg = load_config()
meta = resolve(cfg["corpus"]["raw_dir"]) / "metadata.jsonl"
chunks = resolve(cfg["corpus"]["processed_dir"]) / "chunks.jsonl"
pdfs = resolve(cfg["corpus"]["raw_dir"]) / "pdf"
if a.verify:
    res = verify_manifest(json.loads(Path(a.verify).read_text(encoding="utf-8")), meta, chunks, pdfs)
    for w in res["warnings"]: print("warning:", w)
    for e in res["errors"]: print("ERROR:", e)
    print("manifest OK" if not res["errors"] else "manifest DRIFT")
    sys.exit(1 if res["errors"] else 0)
if not a.id:
    sys.exit("pass --id <corpus id> or --verify <manifest>")
try:
    commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
except Exception:
    commit = "unknown"
m = build_manifest(a.id, meta, chunks, pdfs, cfg, commit)
out = resolve("corpus/manifests") / f"{a.id}.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(m, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"wrote {out}: {m['n_papers']} papers, {m['n_chunks']} chunks, "
      f"{sum(p['pdf_sha256'] is not None for p in m['papers'])} PDFs hashed")
