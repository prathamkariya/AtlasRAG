from __future__ import annotations
import re


def _hard_split(par: str, max_chars: int, overlap: int) -> list[str]:
    out, start = [], 0
    while start < len(par):
        end = min(start + max_chars, len(par))
        if end < len(par):
            sp = par.rfind(" ", start + max_chars // 2, end)
            if sp != -1:
                end = sp
        out.append(par[start:end].strip())
        if end >= len(par):
            break
        start = max(end - overlap, start + 1)
    return [o for o in out if o]


def chunk_section(text:str,max_chars=1800,overlap_chars=200,min_chars=200)->list[str]:
    pars=[p.strip() for p in re.split(r"\n{2,}",text) if p.strip()]
    chunks,cur=[], ""

    for p in pars:
        pieces=_hard_split(p,max_chars,overlap_chars) if len(p)>max_chars else [p]

        for piece in pieces:
            if cur and len(cur)+len(piece)+2>max_chars:
                chunks.append(cur)
                cur=piece
            else:
                cur=f"{cur}\n\n{piece}" if cur else piece

    if cur:
        chunks.append(cur)

    if len(chunks)>1 and len(chunks[-1])<min_chars:
        last=chunks.pop()
        chunks[-1]+="\n\n"+last

    return chunks


def build_chunks(paper_id: str, title: str, sections, cfg: dict) -> list[dict]:
    out = []
    for sec_name, sec_text in sections:
        for c in chunk_section(sec_text, cfg["max_chars"], cfg["overlap_chars"], cfg["min_chars"]):
            out.append({"chunk_id": f"{paper_id}::{len(out)}", "paper_id": paper_id,
                        "title": title, "section": sec_name, "text": c})
    return out
