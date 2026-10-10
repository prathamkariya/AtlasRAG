"""A corpus manifest pins WHAT the corpus is, so PDFs and embeddings can stay out of Git and still be re-created
and checked. Text artifacts (metadata, chunks) are hashed line-ending-normalized so Windows/Linux agree; PDFs are
hashed as raw bytes when present locally."""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path


def sha_text(path) -> str:
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def sha_bytes(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_jsonl(path) -> list[dict]:
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def build_manifest(corpus_id: str, metadata_path, chunks_path, pdf_dir, cfg: dict | None = None,
                   git_commit: str = "unknown") -> dict:
    meta = read_jsonl(metadata_path)
    pdf_dir = Path(pdf_dir)
    papers = []
    for r in sorted(meta, key=lambda r: r["id"]):
        pdf = pdf_dir / f"{r['id']}.pdf"
        papers.append({"id": r["id"], "published": str(r.get("published", ""))[:10], "title": r.get("title", ""),
                       "pdf_url": r.get("pdf_url", ""),
                       "pdf_sha256": sha_bytes(pdf) if pdf.exists() else None,
                       "pdf_bytes": pdf.stat().st_size if pdf.exists() else None})
    n_chunks = len(read_jsonl(chunks_path))
    cfg = cfg or {}
    return {"corpus_id": corpus_id, "created": time.strftime("%Y-%m-%dT%H:%M:%S"), "git_commit": git_commit,
            "n_papers": len(papers), "n_chunks": n_chunks,
            "metadata_sha256": sha_text(metadata_path), "chunks_sha256": sha_text(chunks_path),
            "embedding_model": (cfg.get("embedding") or {}).get("model"),
            "chunking": cfg.get("chunking"), "papers": papers}


def verify_manifest(manifest: dict, metadata_path, chunks_path, pdf_dir=None) -> dict:
    """Returns {'errors': [...], 'warnings': [...]}. Errors = text artifacts drifted. Warnings = PDFs missing or differ."""
    errors, warnings = [], []
    if sha_text(metadata_path) != manifest["metadata_sha256"]:
        errors.append("metadata.jsonl does not match the manifest")
    if sha_text(chunks_path) != manifest["chunks_sha256"]:
        errors.append("chunks.jsonl does not match the manifest")
    ids = {r["id"] for r in read_jsonl(metadata_path)}
    want = {p["id"] for p in manifest["papers"]}
    if ids != want:
        errors.append(f"paper ids differ: {len(ids - want)} extra, {len(want - ids)} missing")
    if pdf_dir is not None:
        missing = diffs = 0
        for p in manifest["papers"]:
            f = Path(pdf_dir) / f"{p['id']}.pdf"
            if not f.exists():
                missing += 1
            elif p["pdf_sha256"] and sha_bytes(f) != p["pdf_sha256"]:
                diffs += 1
        if missing:
            warnings.append(f"{missing} PDFs not present locally (run scripts/refetch_pdfs.py)")
        if diffs:
            warnings.append(f"{diffs} PDFs differ from the manifest hash")
    return {"errors": errors, "warnings": warnings}
