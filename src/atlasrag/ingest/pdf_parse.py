"""PDF -> (section, text) pairs.

Heuristic by design: good enough for Week 1. Known limits: two-column reading
order can interleave, equations/tables come out as plain text. A cleaner
upgrade later is parsing arXiv LaTeX source instead of PDFs."""
from __future__ import annotations
import re

HEADING_RE = re.compile(r"^(?:\d{1,2}(?:\.\d{1,2}){0,2}\.?|[IVX]{1,4}\.)\s+[A-Z][\w\s,:\-–()/']{3,80}$")
NAMED = {"abstract", "introduction", "methods", "method", "data", "observations",
         "results", "discussion", "conclusions", "conclusion", "summary",
         "acknowledgements", "acknowledgments", "references", "bibliography", "appendix"}
STOP = {"references", "bibliography", "acknowledgements", "acknowledgments"}


def extract_text(pdf_path) -> str:
    try:
        import pymupdf as fitz  # PyMuPDF >= 1.24.3, lazy import
    except ImportError:
        import fitz
    paras = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            for b in page.get_text("blocks"):
                if b[6] != 0:          # skip image blocks
                    continue
                t = b[4].strip()
                if not t:
                    continue
                t = re.sub(r"-\n(?=[a-z])", "", t)
                t = re.sub(r"\s*\n\s*", " ", t)
                paras.append(t)
    return "\n\n".join(paras)


_NUM_PREFIX = re.compile(r"^(?:\d{1,2}(?:\.\d{1,2}){0,2}\.?|[IVX]{1,4}\.)\s+")


def _clean_name(p: str) -> str:
    return _NUM_PREFIX.sub("", p.strip(), count=1).strip(". :").strip()


def is_heading(p: str) -> bool:
    if "\n" in p or len(p) > 90:
        return False
    if _clean_name(p).lower() in NAMED:
        return True
    return bool(HEADING_RE.match(p))


def split_sections(text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, list[str]]] = [("Front matter", [])]
    for p in re.split(r"\n{2,}", text):
        p = p.strip()
        if not p:
            continue
        if is_heading(p):
            name = _clean_name(p) or p
            if name.lower() in STOP:
                break
            sections.append((name, []))
        else:
            sections[-1][1].append(p)
    return [(n, "\n\n".join(ps)) for n, ps in sections if ps]
