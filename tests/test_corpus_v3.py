import json
from pathlib import Path

from atlasrag.bench.schema import paper_split
from atlasrag.corpus_manifest import verify_manifest


CORPUS_ROOT = Path(__file__).resolve().parents[1]
RAW_V3 = CORPUS_ROOT / "data" / "raw_v3"
PROC_V3 = CORPUS_ROOT / "data" / "processed_v3"
INDEX_V3 = CORPUS_ROOT / "data" / "index_v3"
MANIFEST_V3 = CORPUS_ROOT / "corpus" / "manifests" / "atlasrag-corpus-v3.json"


def test_corpus_v3_manifest_and_files_exist():
    assert MANIFEST_V3.exists(), "atlasrag-corpus-v3.json must exist"
    assert (RAW_V3 / "metadata.jsonl").exists(), "raw_v3/metadata.jsonl must exist"
    assert (PROC_V3 / "chunks.jsonl").exists(), "processed_v3/chunks.jsonl must exist"
    assert (INDEX_V3 / "chunks.jsonl").exists(), "index_v3/chunks.jsonl must exist"
    assert (INDEX_V3 / "emb.npy").exists(), "index_v3/emb.npy must exist"


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
    manifest = json.loads(MANIFEST_V3.read_text(encoding="utf-8"))
    res = verify_manifest(
        manifest,
        RAW_V3 / "metadata.jsonl",
        PROC_V3 / "chunks.jsonl",
        RAW_V3 / "pdf",
    )
    assert res["errors"] == []
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
