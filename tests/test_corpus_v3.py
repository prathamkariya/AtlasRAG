"""Corpus v3 tests — portable by default.

The default tests validate only tracked text artifacts (metadata.jsonl,
chunks.jsonl, corpus manifest).  Index artifacts (emb.npy) and PDFs live
in .gitignore and are checked only when they are locally present *or* when
the environment variable RUN_CORPUS_INTEGRATION=1 is set.
"""
import json
import os
from pathlib import Path

import pytest

from atlasrag.bench.schema import paper_split
from atlasrag.corpus_manifest import verify_manifest


CORPUS_ROOT = Path(__file__).resolve().parents[1]
RAW_V3 = CORPUS_ROOT / "data" / "raw_v3"
PROC_V3 = CORPUS_ROOT / "data" / "processed_v3"
INDEX_V3 = CORPUS_ROOT / "data" / "index_v3"
MANIFEST_V3 = CORPUS_ROOT / "corpus" / "manifests" / "atlasrag-corpus-v3.json"

_INTEGRATION = os.environ.get("RUN_CORPUS_INTEGRATION") == "1"


# ── Default (portable) tests ────────────────────────────────────────────

def test_corpus_v3_tracked_files_exist():
    """Tracked text artifacts must be present in any checkout."""
    assert MANIFEST_V3.exists(), "atlasrag-corpus-v3.json must exist"
    assert (RAW_V3 / "metadata.jsonl").exists(), "raw_v3/metadata.jsonl must exist"
    assert (PROC_V3 / "chunks.jsonl").exists(), "processed_v3/chunks.jsonl must exist"


def test_corpus_v3_paper_curation():
    meta_lines = [json.loads(l) for l in (RAW_V3 / "metadata.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    paper_ids = [m["id"] for m in meta_lines]
    assert len(paper_ids) == 121
    assert len(set(paper_ids)) == 121

    # Excluded paper
    assert "2609.13266v1" not in paper_ids

    # Added papers
    expected_additions = {"2510.23823v1", "2604.08530v1", "2610.14781v1"}
    assert expected_additions.issubset(set(paper_ids))


def test_corpus_v3_manifest_verifies():
    """Verify text hashes and paper IDs; PDF checks only when dir exists."""
    manifest = json.loads(MANIFEST_V3.read_text(encoding="utf-8"))
    pdf_dir = RAW_V3 / "pdf" if (RAW_V3 / "pdf").exists() else None
    res = verify_manifest(
        manifest,
        RAW_V3 / "metadata.jsonl",
        PROC_V3 / "chunks.jsonl",
        pdf_dir,
    )
    assert res["errors"] == []
    # PDF warnings are acceptable in a clean checkout without PDFs
    if pdf_dir is not None:
        assert res["warnings"] == []


def test_corpus_v3_train_test_split_isolation():
    chunks = [json.loads(l) for l in (PROC_V3 / "chunks.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(chunks) == 4076

    papers = sorted(set(c["paper_id"] for c in chunks))
    assert len(papers) == 121

    train_papers = {p for p in papers if paper_split(p) == "train"}
    test_papers = {p for p in papers if paper_split(p) == "test"}

    # No leakage between train and test
    assert train_papers.isdisjoint(test_papers)
    assert train_papers | test_papers == set(papers)
    assert len(train_papers) > 0
    assert len(test_papers) > 0

    # Ensure pilot multihop question chunks exist and are in test split
    pilot_chunks = {"2607.24443v2::23", "2608.28260v1::13"}
    found_chunks = {c["chunk_id"]: c for c in chunks if c["chunk_id"] in pilot_chunks}
    assert set(found_chunks.keys()) == pilot_chunks
    for cid, c in found_chunks.items():
        assert paper_split(c["paper_id"]) == "test"
        assert len(c["text"]) >= 500


# ── Integration tests (local artifacts required) ────────────────────────

_skip_integration = pytest.mark.skipif(
    not _INTEGRATION and not (INDEX_V3 / "emb.npy").exists(),
    reason="Index artifacts not present; set RUN_CORPUS_INTEGRATION=1 to require",
)


@_skip_integration
def test_corpus_v3_index_artifacts_exist():
    """Verify built index files are locally present and aligned."""
    assert (INDEX_V3 / "chunks.jsonl").exists(), "index_v3/chunks.jsonl must exist"
    assert (INDEX_V3 / "emb.npy").exists(), "index_v3/emb.npy must exist"
    import numpy as np
    emb = np.load(INDEX_V3 / "emb.npy")
    idx_chunks = [json.loads(l) for l in (INDEX_V3 / "chunks.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    assert emb.shape[0] == len(idx_chunks), f"emb rows {emb.shape[0]} != index chunks {len(idx_chunks)}"
    assert emb.shape[1] == 384, f"expected 384-dim BGE-small embeddings, got {emb.shape[1]}"
