import pytest
from atlasrag.config import load_config
from atlasrag.ingest.chunking import chunk_section, build_chunks
from atlasrag.ingest.pdf_parse import split_sections, is_heading
from atlasrag.ingest.arxiv_fetch import build_query
from atlasrag.retrieval.fusion import rrf
from atlasrag.routers import build_router, HeuristicRouter, EscalatingRouter, OracleRouter, FixedRouter
from atlasrag.routers.base import Router, RouteDecision


def test_config_has_a_strategy_for_every_route_label():
    cfg = load_config()
    for label in ["VANILLA", "STATIC", "SIMPLE", "MULTI_HOP", "UNCERTAIN"]:
        assert label in cfg["strategies"]


def test_chunking_respects_max_and_progresses():
    text = "\n\n".join(["word " * 120] * 10)
    chunks = chunk_section(text, max_chars=800, overlap_chars=100, min_chars=100)
    assert len(chunks) > 1
    assert all(len(c) <= 1000 for c in chunks)
    long_par = "x" * 5000
    assert len(chunk_section(long_par, 800, 100, 100)) >= 6


def test_headings_and_reference_stop():
    assert is_heading("1 Introduction")
    assert is_heading("2.1 Data and Observations")
    assert is_heading("CONCLUSIONS")
    assert not is_heading("We measure H0 = 73 km/s/Mpc using Cepheids calibrated by parallaxes.")
    text = "Title block\n\n1 Introduction\n\nIntro text here.\n\n2 Methods\n\nMethod text.\n\nReferences\n\nSmith 2020"
    secs = dict(split_sections(text))
    assert "Introduction" in secs and "Methods" in secs
    assert not any("Smith" in v for v in secs.values())


def test_build_chunks_ids_unique():
    cfg = {"max_chars": 500, "overlap_chars": 50, "min_chars": 50}
    ch = build_chunks("p1", "T", [("A", "a " * 600), ("B", "b " * 600)], cfg)
    assert len({c["chunk_id"] for c in ch}) == len(ch)


def test_arxiv_query():
    assert build_query(["astro-ph.CO"], []) == "cat:astro-ph.CO"
    q = build_query(["astro-ph.CO", "astro-ph.GA"], ["hubble tension"])
    assert q == '(cat:astro-ph.CO OR cat:astro-ph.GA) AND (all:"hubble tension")'


def test_rrf_prefers_items_ranked_high_in_both():
    fused = [i for i, _ in rrf([[1, 2, 3], [3, 2, 9]])]
    assert fused[0] in (2, 3) and set(fused) == {1, 2, 3, 9}


def test_fixed_and_heuristic_routers():
    assert build_router("vanilla", {}).route("q").label == "VANILLA"
    assert build_router("static", {}).route("q").label == "STATIC"
    h = HeuristicRouter()
    assert h.route("What is the Hubble constant measured in paper X?").label == "SIMPLE"
    assert h.route("Compare the studies and say whether they disagree.").label == "MULTI_HOP"


def test_oracle_raises_on_missing_gold():
    o = OracleRouter({"What is X?": "SIMPLE"})
    assert o.route("what is   x?").label == "SIMPLE"
    with pytest.raises(KeyError):
        o.route("unknown question")


class _Const(Router):
    def __init__(self, label, conf, name):
        self.label, self.conf, self.name = label, conf, name
    def route(self, q):
        return RouteDecision(self.label, self.conf, self.name)


def test_escalation_threshold_behaviour():
    hi = EscalatingRouter(_Const("SIMPLE", 0.9, "p"), _Const("MULTI_HOP", 1.0, "f"), 0.7)
    lo = EscalatingRouter(_Const("SIMPLE", 0.4, "p"), _Const("MULTI_HOP", 1.0, "f"), 0.7)
    assert hi.route("q").label == "SIMPLE" and not hi.route("q").escalated
    d = lo.route("q")
    assert d.label == "MULTI_HOP" and d.escalated


def test_compass_is_a_clear_placeholder():
    with pytest.raises(NotImplementedError):
        build_router("compass", {}).route("q")
