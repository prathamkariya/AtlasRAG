import json
import math

import numpy as np
import pytest

pytest.importorskip("rank_bm25")
from atlasrag.bench.schema import Question, load_questions, paper_split, save_questions
from atlasrag.bench.validate import parse_json, verdict, judge_support
from atlasrag.bench.generate_v2 import (
    ValidatedGenerator,
    assess_chain_pair,
    assess_cross_paper_pair,
    has_shared_scientific_signal,
    scientific_signals,
)
from atlasrag.bench.oracle_v2 import derive_oracle_v2, training_pairs
from atlasrag.bench.diagnostics import diagnose, to_markdown
from atlasrag.llm import LLMRateLimitExceeded, run_with_bounded_retries
from atlasrag.retrieval.index import Index
from atlasrag.bench.experiments import make_router


def test_parse_json_tolerates_comments_and_garbage():
    t = '{"answer_supported": true, // yes\n "needs_all_passages": false}'
    assert parse_json(t) == {"answer_supported": True, "needs_all_passages": False}
    assert parse_json("no json here") == {}


def test_verdict_rules():
    good = {"answer_supported": True, "needs_all_passages": True, "passage_1_contribution": "fact from A", "passage_2_contribution": "fact from B", "joint_reason": "both facts are needed", "quantities_comparable": None, "same_quantity": True}
    assert verdict(good, "multi_hop") == (True, [])
    assert verdict({"answer_supported": True}, "simple") == (True, [])               # simple needs only one passage
    ok, why = verdict({"answer_supported": True, "needs_all_passages": False}, "multi_hop")
    assert not ok and "not_all_passages_needed" in why
    ok, why = verdict({**good, "quantities_comparable": False}, "multi_hop")
    assert not ok and "quantities_not_comparable" in why                              # the 73 km/s/Mpc vs percentages bug
    ok, why = verdict({**good, "same_quantity": False}, "temporal")
    assert not ok and "different_quantity" in why
    ok, why = verdict({"answer_supported": False, "needs_all_passages": True}, "chain")
    assert not ok and "answer_not_supported" in why
    assert verdict({}, "simple") == (False, ["judge_unparseable"])


class SeqLLM:
    """Returns a structured generation payload and a configurable audit."""
    def __init__(self, judge, generation=None):
        self.judge, self.n = judge, 0
        self.generation = generation or {
            "question": "How does the early-universe value compare with the local one?",
            "reference_answer": "They differ by several sigma.",
            "passage_1_contribution": "the early-universe measurement",
            "passage_2_contribution": "the local measurement",
            "joint_reason": "the comparison requires both measurements",
            "same_quantity": True,
        }

    def chat(self, messages, **kw):
        self.n += 1
        if "audit evaluation questions" in messages[0]["content"]:
            return json.dumps(self.judge)
        return json.dumps(self.generation)


def small_index():
    pids = [f"p{i}" for i in range(60)]
    chunks = [{"chunk_id": f"{p}::{k}", "paper_id": p, "title": "T",
               "section": "Abstract" if k == 0 else "Results",
               "text": (f"Hubble measurement cosmology source{p} result{k} " * 70)}
              for p in pids for k in range(2)]
    emb = np.random.RandomState(0).rand(len(chunks), 8).astype("float32")
    return Index(chunks, emb)


def test_validated_generator_filters_and_counts():
    good = {"answer_supported": True, "needs_all_passages": True, "passage_1_contribution": "fact from A", "passage_2_contribution": "fact from B", "joint_reason": "both facts are needed", "quantities_comparable": None, "same_quantity": True}
    g = ValidatedGenerator(small_index(), SeqLLM(good), {}, seed=1)
    made = [q for q in (g.make("multi_hop", "test") for _ in range(10)) if q]
    assert made and g.vstats["passed"] == len(made)
    assert json.loads(made[0].validation)["ok"] is True

    bad = {**good, "needs_all_passages": False}
    g2 = ValidatedGenerator(small_index(), SeqLLM(bad), {}, seed=1)
    assert all(g2.make("multi_hop", "test") is None for _ in range(10))
    assert g2.vstats["not_all_passages_needed"] > 0 and g2.vstats["passed"] == 0


@pytest.mark.parametrize("field", ["passage_1_contribution", "passage_2_contribution", "joint_reason"])
def test_structured_generator_rejects_missing_required_evidence(field):
    good = {"answer_supported": True, "needs_all_passages": True,
            "passage_1_contribution": "fact from A", "passage_2_contribution": "fact from B",
            "joint_reason": "both facts are needed", "quantities_comparable": None,
            "same_quantity": True}
    generated = {"question": "How do the two measurements constrain the shared parameter?",
                 "reference_answer": "Together they constrain it.", **good}
    generated[field] = ""
    g = ValidatedGenerator(small_index(), SeqLLM(good, generated), {}, seed=1)
    assert g.make("multi_hop", "test") is None
    assert g.vstats["missing_structured_evidence"] == 1


def test_structured_generator_rejects_identical_passage_roles():
    good = {"answer_supported": True, "needs_all_passages": True,
            "passage_1_contribution": "fact from A", "passage_2_contribution": "fact from B",
            "joint_reason": "both facts are needed", "quantities_comparable": None,
            "same_quantity": True}
    generated = {"question": "How do the two measurements constrain the shared parameter?",
                 "reference_answer": "Together they constrain it.",
                 "passage_1_contribution": "the measured Hubble constant",
                 "passage_2_contribution": "the measured Hubble constant",
                 "joint_reason": "both facts are needed", "same_quantity": True}
    g = ValidatedGenerator(small_index(), SeqLLM(good, generated), {}, seed=1)
    assert g.make("multi_hop", "test") is None
    assert g.vstats["non_distinct_passage_contributions"] == 1


def test_structured_generator_rejects_comparison_without_a_shared_quantity():
    good = {"answer_supported": True, "needs_all_passages": True,
            "passage_1_contribution": "fact from A", "passage_2_contribution": "fact from B",
            "joint_reason": "both facts are needed", "quantities_comparable": None,
            "same_quantity": True}
    generated = {"question": "Which model performs better, and why?",
                 "reference_answer": "One model performs better.",
                 "passage_1_contribution": "the first model's result",
                 "passage_2_contribution": "the second model's result",
                 "joint_reason": "both results are compared", "same_quantity": False}
    g = ValidatedGenerator(small_index(), SeqLLM(good, generated), {}, seed=1)
    assert g.make("multi_hop", "test") is None
    assert g.vstats["comparison_without_shared_quantity"] == 1


def test_generator_rejects_answer_that_needs_only_one_passage():
    audit = {"answer_supported": True, "needs_all_passages": False,
             "passage_1_contribution": "the answer", "passage_2_contribution": "background",
             "joint_reason": "", "quantities_comparable": None, "same_quantity": True}
    g = ValidatedGenerator(small_index(), SeqLLM(audit), {}, seed=1)
    assert g.make("multi_hop", "test") is None
    assert g.vstats["not_all_passages_needed"] == 1


@pytest.mark.parametrize(("question", "reason"), [
    ("According to the passage, what causes the observed shift?", "simple_mentions_source"),
    ("Which reference reports results from the telescope?", "citation_trivia"),
])
def test_simple_generator_rejects_source_framing_and_citation_trivia(question, reason):
    audit = {"answer_supported": True, "needs_all_passages": False,
             "passage_1_contribution": "the fact", "passage_2_contribution": "",
             "joint_reason": "", "quantities_comparable": None, "same_quantity": None}
    generation = {"question": question, "reference_answer": "A supported answer."}
    g = ValidatedGenerator(small_index(), SeqLLM(audit, generation), {}, seed=1)
    assert g.make("simple", "test") is None
    assert g.vstats[reason] == 1


def test_temporal_and_chain_verdicts_require_their_evidence_relationships():
    supported = {"answer_supported": True, "needs_all_passages": True,
                 "passage_1_contribution": "earlier result", "passage_2_contribution": "later update",
                 "joint_reason": "the change requires both results", "quantities_comparable": True,
                 "same_quantity": True}
    assert verdict(supported, "temporal") == (True, [])
    assert verdict({**supported, "same_quantity": False}, "temporal")[0] is False
    assert "quantities_not_comparable" in verdict({**supported, "quantities_comparable": False}, "conflicting")[1]
    assert verdict(supported, "chain") == (True, [])
    abstract_alone = {**supported, "needs_all_passages": False, "joint_reason": ""}
    assert "not_all_passages_needed" in verdict(abstract_alone, "chain")[1]


def test_pair_preselection_requires_a_shared_scientific_signal():
    assert has_shared_scientific_signal(
        "The Hubble constant measurement is 70 km/s/Mpc.",
        "A later Hubble constant measurement is 73 km/s/Mpc.",
    )
    assert not has_shared_scientific_signal(
        "The telescope calibration is stable across observations.",
        "Dark matter simulations use a different numerical method.",
    )


def test_pair_sourcing_rejects_unrelated_and_generic_only_pairs():
    unrelated = assess_cross_paper_pair(
        "DESI BAO constrains the Hubble constant H0.",
        "Milky Way contamination is estimated from a stellar catalogue.",
        qtype="multi_hop", dense_similarity=0.9,
    )
    generic = assess_cross_paper_pair(
        "The model reports analysis results for this study.",
        "This study reports model analysis results.",
        qtype="multi_hop", dense_similarity=0.99,
    )
    assert unrelated.reason == "no_shared_scientific_signal"
    assert generic.reason == "no_shared_scientific_signal"


def test_pair_sourcing_accepts_related_complementary_scientific_evidence():
    a = "DESI BAO constrains the Hubble constant H0 using a distance-ladder fit."
    b = "A later DESI BAO H0 estimate tests early dark energy against the CMB."
    assessed = assess_cross_paper_pair(a, b, qtype="multi_hop", dense_similarity=0.7)
    assert {"desi", "bao", "h0"} <= scientific_signals(a) & scientific_signals(b)
    assert assessed.reason is None and assessed.score > 0


def test_pair_sourcing_penalizes_near_duplicate_passages():
    text = "DESI BAO constrains the Hubble constant H0 using the same distance-ladder fit."
    assessed = assess_cross_paper_pair(text, text, qtype="multi_hop", dense_similarity=1.0)
    assert assessed.reason == "near_duplicate_passages"


def test_pair_sourcing_rejects_broad_topic_overlap_without_a_shared_anchor():
    assessed = assess_cross_paper_pair(
        "A local gravitational field can mimic dark energy at late times.",
        "A scalar field changes gravity and dark energy at late times.",
        qtype="multi_hop", dense_similarity=0.8,
    )
    assert assessed.reason == "no_shared_specific_signal"


def test_temporal_pair_sourcing_requires_dates_signals_and_evidence_sections():
    a = "DESI BAO gives an H0 measurement with a distance-ladder analysis."
    b = "A revised DESI BAO H0 measurement improves the distance-ladder constraint."
    assert assess_cross_paper_pair(
        a, b, qtype="temporal", dense_similarity=0.6,
        date_a="2025-01-01", date_b="2025-01-01",
        section_a="Results", section_b="Discussion",
    ).reason == "temporal_bad_dates"
    assert assess_cross_paper_pair(
        a, "A revised dark-matter simulation changes halo profiles.", qtype="temporal",
        dense_similarity=0.6, date_a="2024-01-01", date_b="2025-01-01",
        section_a="Results", section_b="Discussion",
    ).reason == "no_shared_scientific_signal"
    accepted = assess_cross_paper_pair(
        a, b, qtype="temporal", dense_similarity=0.6,
        date_a="2024-01-01", date_b="2025-01-01",
        section_a="Results", section_b="Discussion",
    )
    assert accepted.reason is None


def test_chain_pair_sourcing_requires_same_paper_and_evidence_section():
    abstract = "We measure the Hubble constant H0 with DESI BAO and find a tension."
    evidence = "Our Results give the DESI BAO H0 posterior and quantify the tension."
    assert assess_chain_pair(abstract, evidence, same_paper=False, section="Results").reason == "chain_different_paper"
    assert assess_chain_pair(abstract, evidence, same_paper=True, section="Introduction").reason == "no_evidence_section"
    accepted = assess_chain_pair(abstract, evidence, same_paper=True, section="Results")
    assert accepted.reason is None and accepted.score > 0
    assert assess_chain_pair(abstract, evidence, same_paper=True, section="Conclusions").reason is None


def test_generator_ranks_a_candidate_pool_over_random_dense_neighbors():
    paper_ids = [f"pair-{n}" for n in range(100)]
    test_ids = [p for p in paper_ids if paper_split(p) == "test"][:4]
    source, duplicate, complement, unrelated = test_ids
    def source_text(text):
        return (text + " ") * 12

    chunks = [
        {"chunk_id": f"{source}::0", "paper_id": source, "title": "T", "section": "Results",
         "text": source_text("DESI BAO constrains the Hubble constant H0 with a distance-ladder fit.")},
        {"chunk_id": f"{duplicate}::0", "paper_id": duplicate, "title": "T", "section": "Results",
         "text": source_text("DESI BAO constrains the Hubble constant H0 with a distance-ladder fit.")},
        {"chunk_id": f"{complement}::0", "paper_id": complement, "title": "T", "section": "Discussion",
         "text": source_text("DESI BAO H0 constraints test early dark energy against the CMB.")},
        {"chunk_id": f"{unrelated}::0", "paper_id": unrelated, "title": "T", "section": "Results",
         "text": source_text("Milky Way contamination is estimated from a stellar catalogue.")},
    ]
    emb = np.array([[1.0, 0.0], [0.99, 0.01], [0.8, 0.2], [0.9, 0.1]], dtype="float32")
    g = ValidatedGenerator(Index(chunks, emb), SeqLLM({}), {}, seed=1)
    ranked = g._rank_cross_paper_candidates(0, "test", "multi_hop")
    assert [idx for idx, _ in ranked] == [2]


def test_bounded_rate_limit_retries_then_raises_without_unbounded_sleep():
    attempts, delays = [], []

    def rate_limited():
        attempts.append(1)
        raise FakeRateLimitError("429")

    with pytest.raises(LLMRateLimitExceeded):
        run_with_bounded_retries(rate_limited, retries=2, base_delay_s=1,
                                 max_delay_s=1.5, sleep=delays.append,
                                 retryable=(FakeRateLimitError,))
    assert len(attempts) == 3
    assert delays == [1, 1.5]


class FakeRateLimitError(Exception):
    pass


def Q(i, gold, route=None):
    return Question(id=f"q{i}", question=f"q {i}?", qtype="simple", reference_answer="a",
                    gold_chunk_ids=gold, gold_paper_ids=["p"], status="accepted", gold_route=route)


def test_verdict_requires_structured_contributions_for_multi_passage():
    v={"answer_supported":True,"needs_all_passages":True,"quantities_comparable":None,"same_quantity":None}
    ok,why=verdict(v,"multi_hop")
    assert not ok
    assert "missing_passage_contributions" in why
    assert "missing_joint_reason" in why



class LadderPipe:
    """Per-label recall table keyed by question text."""
    def __init__(self, table):
        self.table = table

    def retrieve_only(self, q, label):
        rec = self.table[q][label]
        gold = ["g1", "g2"]
        got = gold[: round(rec * 2)]
        return {"chunks": [{"chunk_id": c} for c in got]}


def test_oracle_v2_best_effort_label_and_training_schemes():
    qs = [Q(0, ["g1", "g2"], "SIMPLE"), Q(1, ["g1", "g2"], "UNCERTAIN"), Q(2, ["g1", "g2"], "UNCERTAIN"), Q(3, ["g1", "g2"])]
    table = {"q 0?": {"SIMPLE": 1.0, "MULTI_HOP": 1.0, "UNCERTAIN": 1.0},
             "q 1?": {"SIMPLE": 0.0, "MULTI_HOP": 1.0, "UNCERTAIN": 1.0},
             "q 2?": {"SIMPLE": 0.5, "MULTI_HOP": 0.5, "UNCERTAIN": 0.5},      # never fully covered
             "q 3?": {"SIMPLE": 0.0, "MULTI_HOP": 0.0, "UNCERTAIN": 0.5}}
    out = derive_oracle_v2(LadderPipe(table), qs)
    assert [q.gold_route_v2 for q in qs] == ["SIMPLE", "MULTI_HOP", "SIMPLE", "UNCERTAIN"]
    assert [q.oracle_sufficient for q in qs] == [True, True, False, False]
    assert out["insufficient"] == 2 and out["differs_from_v1"] == 2          # q1 (UNCERTAIN->MULTI_HOP) and q2 (UNCERTAIN->SIMPLE)
    assert qs[2].ladder_recalls["UNCERTAIN"] == 0.5
    assert len(training_pairs(qs, "v2")) == 4
    assert [l for _, l in training_pairs(qs, "v2_sufficient")] == ["SIMPLE", "MULTI_HOP"]
    assert [l for _, l in training_pairs(qs, "v1")] == ["SIMPLE", "UNCERTAIN", "UNCERTAIN"]   # q3 has no v1 label


def test_schema_new_fields_roundtrip_and_old_files_load(tmp_path):
    p = tmp_path / "q.jsonl"
    q = Q(1, ["g1"])
    q.gold_route_v2, q.ladder_recalls, q.validation = "SIMPLE", {"SIMPLE": 1.0}, '{"ok": true}'
    save_questions(p, [q])
    back = load_questions(p)[0]
    assert back.gold_route_v2 == "SIMPLE" and back.ladder_recalls == {"SIMPLE": 1.0}
    old = {"id": "o", "question": "x", "qtype": "simple", "reference_answer": "a", "gold_chunk_ids": ["g"],
           "gold_paper_ids": ["p"], "split": "test", "status": "accepted", "gold_route": "SIMPLE",
           "oracle_sufficient": True, "notes": ""}
    (tmp_path / "old.jsonl").write_text(json.dumps(old) + "\n")
    assert load_questions(tmp_path / "old.jsonl")[0].gold_route_v2 is None


def _row(i, label, rec, calls):
    return {"id": f"q{i}", "qtype": "simple", "evidence_recall": rec,
            "route": {"label": label, "source": "x"},
            "metrics": {"llm_calls": calls, "latency_s": 1, "prompt_tokens": 0, "completion_tokens": 0}}


def test_diagnostics_wasted_vs_harmful():
    qs = []
    for i in range(4):
        q = Q(i, ["g"]); q.oracle_sufficient = True; qs.append(q)
    oracle = [_row(0, "SIMPLE", 1, 0), _row(1, "SIMPLE", 1, 0), _row(2, "MULTI_HOP", 1, 1), _row(3, "MULTI_HOP", 1, 1)]
    strong = [_row(i, "UNCERTAIN", 1, 1) for i in range(4)]
    router = [_row(0, "UNCERTAIN", 1, 1),     # over-routed, same recall -> wasted
              _row(1, "SIMPLE", 1, 0),        # exact
              _row(2, "SIMPLE", 0.0, 0),      # under-routed, lost evidence -> harmful
              _row(3, "SIMPLE", 1, 0)]        # under-routed, no loss (benign)
    d = diagnose(router, oracle, strong, qs)
    assert (d["over_routed"], d["wasted"], d["under_routed"], d["harmful"]) == (1, 1, 2, 1)
    assert d["exact_route_match"] == 0.25
    assert math.isclose(d["recall"], 0.75) and math.isclose(d["calls_saved_vs_strong"], 0.75)
    assert math.isclose(d["sufficient_cover_rate"], 0.75)
    assert "regret" in to_markdown(d)
    with pytest.raises(ValueError):
        diagnose([_row(0, "STATIC", 1, 0)], oracle, strong, qs)     # fixed routers are not diagnosable


def test_e2_router_uses_v2_labels():
    q = Q(1, ["g"], "UNCERTAIN"); q.gold_route_v2 = "SIMPLE"
    assert make_router("E", {}, None, [q]).route(q.question).label == "UNCERTAIN"
    assert make_router("E2", {}, None, [q]).route(q.question).label == "SIMPLE"
