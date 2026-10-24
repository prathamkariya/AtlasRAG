import json

from scripts.auto_gen_questions import existing_counts, is_rate_limit_stop


def test_existing_counts_counts_candidates_and_accepted_rows_but_not_rejected_rows(tmp_path):
    out = tmp_path / "questions.jsonl"
    rows = [
        {"id": "a", "qtype": "simple", "split": "test", "status": "candidate"},
        {"id": "b", "qtype": "simple", "split": "test", "status": "rejected"},
        {"id": "c", "qtype": "simple", "split": "test", "status": "accepted"},
        {"id": "d", "qtype": "multi_hop", "split": "train", "status": "candidate"},
    ]
    out.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    assert existing_counts(out, "test", ["simple", "multi_hop"]) == {"simple": 2, "multi_hop": 0}


def test_exit_code_two_is_rate_limit_only_with_a_new_rate_limit_summary(tmp_path):
    summary = tmp_path / "run.runs.jsonl"
    old = {"stopped": {"reason": "rate_limited"}}
    summary.write_text(json.dumps(old) + "\n", encoding="utf-8")
    assert not is_rate_limit_stop(2, 1, summary)
    assert not is_rate_limit_stop(2, 0, tmp_path / "missing.jsonl")
    summary.write_text(
        json.dumps(old) + "\n" +
        json.dumps({"stopped": {"reason": "invalid_args"}}) + "\n",
        encoding="utf-8",
    )
    assert not is_rate_limit_stop(2, 1, summary)
    summary.write_text(
        json.dumps(old) + "\n" +
        json.dumps({"stopped": {"reason": "rate_limited"}}) + "\n",
        encoding="utf-8",
    )
    assert is_rate_limit_stop(2, 1, summary)
