"""Oracle v2: cheapest strategy that achieves the BEST recall on the ladder.

v1 problem: when no strategy reached recall 1.0, v1 labelled the question with the
top strategy, so 'insufficient' retrieval failures became 'UNCERTAIN' and a router
trained on them learns to spend the most on questions that fail anyway.
v2: best = max recall over the ladder; label = cheapest strategy within epsilon of
best. For fully-covered questions v2 == v1. Stores every ladder recall so label
schemes can be changed without re-running retrieval."""
from __future__ import annotations
from collections import Counter

from .metrics import evidence_recall
from .oracle import LADDER


def derive_oracle_v2(pipeline, questions, ladder=LADDER, eps: float = 1e-9, progress=None) -> dict:
    counts, insufficient, differs = Counter(), 0, 0
    it = progress(questions) if progress else questions
    for q in it:
        recs = {}
        for lab in ladder:
            out = pipeline.retrieve_only(q.question, lab)
            recs[lab] = evidence_recall(q.gold_chunk_ids, [c["chunk_id"] for c in out["chunks"]])
        best = max(recs.values())
        q.ladder_recalls = recs
        q.gold_route_v2 = next(l for l in ladder if recs[l] >= best - eps)
        q.oracle_sufficient = best >= 1.0 - eps
        counts[q.gold_route_v2] += 1
        insufficient += not q.oracle_sufficient
        differs += bool(q.gold_route) and q.gold_route != q.gold_route_v2
    return {"counts": dict(counts), "insufficient": insufficient, "n": len(questions),
            "differs_from_v1": differs}


def training_pairs(questions, scheme: str = "v2"):
    """(question_text, label) pairs for Compass. Schemes:
      v2          : oracle v2 labels, insufficient questions kept (their label is the cheapest best-effort strategy)
      v2_sufficient: only questions retrieval can fully cover (cleanest signal)
      v1          : original labels (insufficient -> UNCERTAIN); kept for comparison
    Never put gold evidence or answer text in the model input; the input is the question only."""
    out = []
    for q in questions:
        if scheme == "v1":
            lab = q.gold_route
        else:
            lab = q.gold_route_v2
            if scheme == "v2_sufficient" and not q.oracle_sufficient:
                continue
        if lab:
            out.append((q.question, lab))
    return out
