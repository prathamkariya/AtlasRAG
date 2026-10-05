import json
import math

import pytest

from atlasrag.bench.report import (bootstrap_ci, cluster_bootstrap_ci, cluster_map, build_rows, to_markdown,
                                   paired_vs, paired_markdown, compare_groups, _exp_files)
from atlasrag.bench.schema import Question


def test_cluster_ci_is_wider_than_question_ci_when_questions_within_a_paper_agree():
    # 6 papers x 10 questions; each paper is all-0 or all-1 => the 60 questions are NOT 60 independent draws
    vals = [1.0] * 30 + [0.0] * 30
    clus = [f"p{i // 10}" for i in range(60)]
    m, lo, hi = bootstrap_ci(vals)
    cm, clo, chi, n = cluster_bootstrap_ci(vals, clus)
    assert n == 6 and cm == m == 0.5
    assert (chi - clo) > 1.5 * (hi - lo)


def test_too_few_papers_gives_undefined_interval_not_a_fake_tight_one():
    cm, clo, chi, n = cluster_bootstrap_ci([0.2, 0.4, 0.6], ["a", "a", "b"])
    assert n == 2 and math.isclose(cm, 0.4) and math.isnan(clo) and math.isnan(chi)
    assert cluster_bootstrap_ci([], [])[3] == 0


def test_cluster_bootstrap_is_deterministic_and_uses_pooled_mean():
    vals = [1.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 1.0]
    clus = ["a", "a", "b", "c", "d", "e", "f", "f"]
    r1, r2 = cluster_bootstrap_ci(vals, clus), cluster_bootstrap_ci(vals, clus)
    assert r1 == r2 and math.isclose(r1[0], sum(vals) / len(vals))       # pooled over questions, not mean of paper means


def Q(i, papers, qtype="simple"):
    return Question(id=f"q{i}", question=f"q{i}?", qtype=qtype, reference_answer="a", gold_chunk_ids=["c"],
                    gold_paper_ids=papers, status="accepted")


def row(i, rec, qtype="simple", source="x"):
    return json.dumps({"id": f"q{i}", "qtype": qtype, "evidence_recall": rec,
                       "route": {"label": "SIMPLE", "source": source},
                       "metrics": {"latency_s": 0.1, "llm_calls": 0, "prompt_tokens": 0, "completion_tokens": 0}})


def test_cluster_map_uses_first_gold_paper_and_survives_missing_papers():
    m = cluster_map([Q(0, ["pA", "pB"]), Q(1, [])])
    assert m == {"q0": "pA", "q1": "q1"}


def test_zero_byte_result_files_are_ignored_everywhere(tmp_path):
    d = tmp_path / "g"; d.mkdir()
    (d / "B_static.jsonl").write_text(row(0, 0.5) + "\n")
    (d / "D_compass.jsonl").write_text("")                                 # aborted run
    assert list(_exp_files(d)) == ["B_static"]
    rows = build_rows(d, [Q(0, ["p"])])
    assert {r["experiment"] for r in rows} == {"B_static"}
    (tmp_path / "h").mkdir(); (tmp_path / "h" / "B_static.jsonl").write_text(row(0, 0.5) + "\n")
    (tmp_path / "h" / "D_compass.jsonl").write_text("")
    cmp = compare_groups(d, tmp_path / "h")
    assert cmp["ranking_stable"] and cmp["ranking_run1"] == ["B_static"]


def test_build_rows_and_markdown_expose_paper_counts_and_cluster_ci(tmp_path):
    qs = [Q(i, [f"p{i % 6}"]) for i in range(12)]
    d = tmp_path / "g"; d.mkdir()
    (d / "A_x.jsonl").write_text("\n".join(row(i, 1.0 if (i % 6) < 3 else 0.0) for i in range(12)) + "\n")
    allrow = [r for r in build_rows(d, qs) if r["qtype"] == "ALL"][0]
    assert allrow["n"] == 12 and allrow["n_papers"] == 6 and not math.isnan(allrow["recall_clo"])
    assert (allrow["recall_chi"] - allrow["recall_clo"]) > (allrow["recall_hi"] - allrow["recall_lo"])
    md = to_markdown(build_rows(d, qs))
    assert "by paper" in md and "evidence recall" in md


def test_paired_vs_with_questions_adds_cluster_fields_and_stays_backward_compatible(tmp_path):
    qs = [Q(i, [f"p{i % 6}"]) for i in range(12)]
    d = tmp_path / "g"; d.mkdir()
    (d / "B_static.jsonl").write_text("\n".join(row(i, 0.5) for i in range(12)) + "\n")
    (d / "F_always.jsonl").write_text("\n".join(row(i, 1.0) for i in range(12)) + "\n")
    old = paired_vs(d, "B")                                                # old call signature still works
    assert "clo" not in old[0] and old[0]["wins"] == 12
    new = paired_vs(d, "B", questions=qs)
    assert new[0]["n_papers"] == 6 and new[0]["wins"] == 12
    md = paired_markdown(new)
    assert "by paper" in md and "yes" in md
    assert "by paper" not in paired_markdown(old)
