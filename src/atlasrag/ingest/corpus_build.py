"""Parse a corpus's PDFs into chunks. The PDF location comes from the ACTIVE raw directory, not from the absolute
`pdf_path` stored in metadata (the first 30 v2 records carry an author-specific path that does not exist on any other
machine, so trusting it silently dropped 30 papers)."""
from __future__ import annotations
from pathlib import Path

from .chunking import build_chunks


def resolve_pdf(rec: dict, raw_dir) -> Path | None:
    raw = Path(raw_dir)
    candidates = [raw / "pdf" / f"{rec['id']}.pdf"]
    if rec.get("pdf_path"):
        candidates.append(Path(rec["pdf_path"]))
    for c in candidates:
        if c.exists():
            return c
    return None


def parse_records(records, raw_dir, chunk_cfg, extract=None, split=None, progress=None):
    """Returns (chunks, failed[(id, reason)]). A missing PDF is a failure, never a silent skip."""
    from . import pdf_parse
    extract = extract or pdf_parse.extract_text
    split = split or pdf_parse.split_sections
    chunks, failed = [], []
    for rec in (progress(records) if progress else records):
        pdf = resolve_pdf(rec, raw_dir)
        if pdf is None:
            failed.append((rec["id"], f"PDF not found under {Path(raw_dir) / 'pdf'} (run scripts/refetch_pdfs.py)"))
            continue
        try:
            sections = split(extract(pdf))
        except Exception as e:                       # corrupt/odd PDFs happen
            failed.append((rec["id"], str(e)))
            continue
        sections = [("Abstract", rec["abstract"])] + [s for s in sections if s[0] not in ("Front matter", "Abstract")]
        chunks += build_chunks(rec["id"], rec["title"], sections, chunk_cfg)
    return chunks, failed
