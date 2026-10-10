r"""Re-download PDFs listed in the active corpus's metadata.jsonl (PDFs are not stored in Git).
  $env:ATLAS_CONFIG = "configs\corpus_v2.yaml"
  python scripts\refetch_pdfs.py --dry-run
  python scripts\refetch_pdfs.py          # about 3s per missing PDF (arXiv politeness)"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from atlasrag.config import load_config, resolve
from atlasrag.ingest.refetch import refetch_pdfs

ap = argparse.ArgumentParser()
ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--limit", type=int)
a = ap.parse_args()
cfg = load_config(); raw = resolve(cfg["corpus"]["raw_dir"])
print(refetch_pdfs(raw / "metadata.jsonl", raw / "pdf", cfg["corpus"].get("request_delay_s", 3.0), a.limit, a.dry_run))
