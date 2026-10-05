"""Deterministic benchmark cleanup from recorded support-audit decisions."""
from __future__ import annotations

from copy import deepcopy


def reject_audit_failures(questions, audit_rows):
    """Return a copy with failed accepted questions rejected and documented.

    The source benchmark and all existing gold/routing fields remain intact; an
    already-recorded audit decision is applied only to a new artifact.
    """
    clean = deepcopy(questions)
    by_id = {q.id: q for q in clean}
    rejected, ignored = [], []
    for row in audit_rows:
        if row.get("ok") is not False or row.get("id") not in by_id:
            continue
        question = by_id[row["id"]]
        if question.status != "accepted":
            ignored.append(question.id)
            continue
        reasons = ", ".join(row.get("reasons") or ["audit failure"])
        question.status = "rejected"
        question.notes = f"Rejected during benchmark audit: {reasons}."
        rejected.append(question.id)
    return clean, {"rejected": rejected, "ignored": ignored}
