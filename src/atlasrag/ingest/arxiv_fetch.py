from __future__ import annotations
import json
import time
from pathlib import Path

import requests


def build_query(categories: list[str], keywords: list[str], date_from: str | None = None,
                date_to: str | None = None) -> str:
    """arXiv query. Optional date_from/date_to ('YYYY-MM-DD') add a server-side submittedDate window, which is how
    you sample across YEARS instead of only the newest papers."""
    cat_q = " OR ".join(f"cat:{c}" for c in categories)
    q = cat_q
    if keywords:
        kw_q = " OR ".join(f'all:"{k}"' for k in keywords)
        q = f"({cat_q}) AND ({kw_q})"
    if date_from or date_to:
        lo = (date_from or "1991-01-01").replace("-", "") + "0000"
        hi = (date_to or "2099-12-31").replace("-", "") + "2359"
        q = f"({q}) AND submittedDate:[{lo} TO {hi}]"
    return q


def fetch_papers(categories, keywords, max_papers, date_from, raw_dir, delay=3.0, date_to=None, sort="date"):
    """Download metadata + PDFs. Resumable: already-downloaded papers are skipped."""
    import arxiv  # lazy import

    raw_dir = Path(raw_dir)
    pdf_dir = raw_dir / "pdf"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    meta_path = raw_dir / "metadata.jsonl"
    seen = set()
    if meta_path.exists():
        with open(meta_path, encoding="utf-8") as f:
            seen = {json.loads(l)["id"] for l in f if l.strip()}

    client = arxiv.Client(page_size=50, delay_seconds=delay, num_retries=5)
    search = arxiv.Search(
        query=build_query(categories, keywords, date_from, date_to),
        max_results=max_papers,
        sort_by=arxiv.SortCriterion.SubmittedDate if sort == "date" else arxiv.SortCriterion.Relevance,
    )
    kept = 0
    for r in client.results(search):
        pub = r.published.strftime("%Y-%m-%d")
        if pub < date_from:
            if sort == "date":
                break                      # newest-first: everything after this is older still
            continue                       # relevance order is not chronological
        if date_to and pub > date_to:
            continue
        pid = r.get_short_id().replace("/", "_")
        if pid in seen:
            continue
        pdf_path = pdf_dir / f"{pid}.pdf"
        if not pdf_path.exists():
            resp = requests.get(r.pdf_url, timeout=90,
                                headers={"User-Agent": "atlasrag-research/0.1 (student project)"})
            if resp.status_code != 200:
                print(f"skip {pid}: HTTP {resp.status_code}")
                continue
            pdf_path.write_bytes(resp.content)
            time.sleep(delay)
        rec = {
            "id": pid,
            "title": " ".join(r.title.split()),
            "authors": [a.name for a in r.authors],
            "published": r.published.isoformat(),
            "categories": r.categories,
            "abstract": " ".join(r.summary.split()),
            "pdf_url": r.pdf_url,
            "pdf_path": str(pdf_path),
        }
        with open(meta_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        kept += 1
        print(f"[{kept}] {pid}  {rec['title'][:70]}")
    return kept
