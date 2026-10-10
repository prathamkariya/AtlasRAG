"""Re-download the exact PDFs listed in a corpus's metadata.jsonl (by their stored pdf_url), so PDFs never need to live in Git."""
from __future__ import annotations
import json
import time
from pathlib import Path

import requests


def refetch_pdfs(metadata_path, pdf_dir, delay: float = 3.0, limit: int | None = None, dry_run: bool = False,
                 log=print) -> dict:
    meta = [json.loads(l) for l in open(metadata_path, encoding="utf-8") if l.strip()]
    pdf_dir = Path(pdf_dir)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    todo = [r for r in meta if not (pdf_dir / f"{r['id']}.pdf").exists()]
    if limit is not None:
        todo = todo[:limit]
    out = {"present": len(meta) - len([r for r in meta if not (pdf_dir / f"{r['id']}.pdf").exists()]),
           "to_download": len(todo), "downloaded": 0, "failed": []}
    if dry_run:
        return out
    for r in todo:
        resp = requests.get(r["pdf_url"], timeout=90, headers={"User-Agent": "atlasrag-research/0.1 (student project)"})
        if resp.status_code != 200:
            out["failed"].append({"id": r["id"], "status": resp.status_code})
            log(f"skip {r['id']}: HTTP {resp.status_code}")
        else:
            (pdf_dir / f"{r['id']}.pdf").write_bytes(resp.content)
            out["downloaded"] += 1
            log(f"[{out['downloaded']}/{len(todo)}] {r['id']}")
        time.sleep(delay)
    return out
