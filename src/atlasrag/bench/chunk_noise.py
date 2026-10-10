"""PDF text extraction leaves figure-axis debris ('0.0 0.5 1.0 1.5 2.0 z 60 90 120 ...') inside passages. Both the retriever
and the LLM judge have to read it. This measures how much of a chunk is bare numbers."""
from __future__ import annotations
import re

_NUM = re.compile(r"[-+\u2212]?[\d.,]+%?")


def numeric_fraction(text: str) -> float:
    toks = text.split()
    return sum(bool(_NUM.fullmatch(t)) for t in toks) / max(1, len(toks))
