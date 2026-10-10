import json
import sys
import types
from datetime import datetime, timezone

import pytest

from atlasrag.ingest.arxiv_fetch import build_query, fetch_papers


def test_build_query_without_dates_is_unchanged():
    assert build_query(["astro-ph.CO"], []) == "cat:astro-ph.CO"
    assert build_query(["astro-ph.CO", "astro-ph.GA"], ["hubble tension"]) == '(cat:astro-ph.CO OR cat:astro-ph.GA) AND (all:"hubble tension")'


def test_build_query_adds_a_server_side_date_window():
    q = build_query(["astro-ph.CO"], ["hubble tension"], "2023-01-01", "2023-12-31")
    assert q == '((cat:astro-ph.CO) AND (all:"hubble tension")) AND submittedDate:[202301010000 TO 202312312359]'
    assert "submittedDate:[202401010000 TO 209912312359]" in build_query(["x"], [], date_from="2024-01-01")
    assert "submittedDate:[199101010000 TO 202212312359]" in build_query(["x"], [], date_to="2022-12-31")


class FakeResult:
    def __init__(self, i, pub):
        self.published = pub
        self._i = i
        self.title = f"Paper {i}"
        self.authors = [types.SimpleNamespace(name="A. Author")]
        self.categories = ["astro-ph.CO"]
        self.summary = "An abstract."
        self.pdf_url = f"http://x/{i}.pdf"

    def get_short_id(self):
        return f"2301.{self._i:05d}v1"


def install_fake_arxiv(monkeypatch, results):
    seen = {}

    class Search:
        def __init__(self, query, max_results, sort_by):
            seen.update(query=query, max_results=max_results, sort_by=sort_by)

    class Client:
        def __init__(self, **kw): pass
        def results(self, search): return iter(results)

    mod = types.SimpleNamespace(Client=Client, Search=Search,
                                SortCriterion=types.SimpleNamespace(SubmittedDate="DATE", Relevance="REL"))
    monkeypatch.setitem(sys.modules, "arxiv", mod)
    import atlasrag.ingest.arxiv_fetch as m
    monkeypatch.setattr(m.requests, "get", lambda *a, **k: types.SimpleNamespace(status_code=200, content=b"%PDF-fake"))
    monkeypatch.setattr(m.time, "sleep", lambda *_: None)
    return seen


D = lambda y, mth, d: datetime(y, mth, d, tzinfo=timezone.utc)


def test_date_sorted_fetch_stops_at_date_from(tmp_path, monkeypatch):
    res = [FakeResult(1, D(2024, 6, 1)), FakeResult(2, D(2024, 3, 1)), FakeResult(3, D(2021, 5, 1)), FakeResult(4, D(2024, 1, 1))]
    seen = install_fake_arxiv(monkeypatch, res)
    n = fetch_papers(["astro-ph.CO"], [], 10, "2023-01-01", tmp_path, delay=0, sort="date")
    assert n == 2 and seen["sort_by"] == "DATE"                      # stops at the first paper older than date_from


def test_relevance_fetch_skips_out_of_window_but_keeps_going(tmp_path, monkeypatch):
    res = [FakeResult(1, D(2024, 6, 1)), FakeResult(2, D(2021, 5, 1)), FakeResult(3, D(2023, 2, 1)), FakeResult(4, D(2025, 1, 1))]
    seen = install_fake_arxiv(monkeypatch, res)
    n = fetch_papers(["astro-ph.CO"], [], 10, "2023-01-01", tmp_path, delay=0, date_to="2024-12-31", sort="relevance")
    ids = [json.loads(l)["id"] for l in open(tmp_path / "metadata.jsonl")]
    assert seen["sort_by"] == "REL" and "submittedDate:[202301010000 TO 202412312359]" in seen["query"]
    assert ids == ["2301.00001v1", "2301.00003v1"]                   # 2021 (too old) and 2025 (after date_to) skipped, loop continued
    assert n == 2 and (tmp_path / "pdf" / "2301.00001v1.pdf").exists()


def test_fetch_is_resumable_and_does_not_duplicate(tmp_path, monkeypatch):
    res = [FakeResult(1, D(2024, 6, 1)), FakeResult(2, D(2024, 3, 1))]
    install_fake_arxiv(monkeypatch, res)
    assert fetch_papers(["x"], [], 10, "2023-01-01", tmp_path, delay=0) == 2
    assert fetch_papers(["x"], [], 10, "2023-01-01", tmp_path, delay=0) == 0
    assert len(open(tmp_path / "metadata.jsonl").read().strip().splitlines()) == 2
