from atlasrag.bench.cleanup import reject_audit_failures
from atlasrag.bench.schema import Question


def question(question_id, status="accepted"):
    return Question(
        id=question_id,
        question="Q?",
        qtype="multi_hop",
        reference_answer="A.",
        gold_chunk_ids=["p::0", "p::1"],
        gold_paper_ids=["p"],
        status=status,
    )


def test_cleanup_rejects_only_accepted_questions_flagged_by_the_audit():
    accepted = question("bad")
    already_rejected = question("old", "rejected")
    clean, summary = reject_audit_failures(
        [accepted, already_rejected],
        [{"id": "bad", "ok": False, "reasons": ["not_all_passages_needed"]}],
    )
    assert accepted.status == "accepted"          # input is preserved for reproducibility
    assert clean[0].status == "rejected"
    assert clean[0].notes == "Rejected during benchmark audit: not_all_passages_needed."
    assert clean[1].status == "rejected"
    assert summary == {"rejected": ["bad"], "ignored": []}


def test_cleanup_ignores_audit_rows_for_nonaccepted_questions_and_passes():
    candidate = question("candidate", "candidate")
    clean, summary = reject_audit_failures(
        [candidate],
        [{"id": "candidate", "ok": False, "reasons": ["answer_not_supported"]},
         {"id": "missing", "ok": True, "reasons": []}],
    )
    assert clean[0].status == "candidate"
    assert summary == {"rejected": [], "ignored": ["candidate"]}
