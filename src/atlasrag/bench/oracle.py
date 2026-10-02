"""Oracle routing labels.

Definition: for each question, the CHEAPEST strategy on the ladder whose
retrieved evidence covers the gold evidence (recall >= min_recall). If none
does, the label is the top of the ladder and oracle_sufficient=False (these
are retrieval-failure cases, useful later for V3).

Caveats to report: Experiment E is an upper bound for routing among these
strategies ON THIS METRIC, by construction. The same procedure on the 'train'
split produces Compass's training labels (Week 3)."""
from __future__ import annotations
from .metrics import evidence_recall

LADDER = ["SIMPLE", "MULTI_HOP", "UNCERTAIN"]


def derive_oracle(pipeline, questions, min_recall: float = 1.0, ladder=LADDER, progress=None) -> dict:
    counts = {l: 0 for l in ladder}
    insufficient = 0
    it = progress(questions) if progress else questions
    for q in it:
        label = None
        for lab in ladder:
            out = pipeline.retrieve_only(q.question, lab)
            rec = evidence_recall(q.gold_chunk_ids, [c["chunk_id"] for c in out["chunks"]])
            if rec >= min_recall:
                label = lab
                break
        q.oracle_sufficient = label is not None
        q.gold_route = label or ladder[-1]
        counts[q.gold_route] += 1
        insufficient += label is None
    return {"counts": counts, "insufficient": insufficient, "n": len(questions)}
