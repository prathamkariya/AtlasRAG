import json
import types

import numpy as np
import pytest

from atlasrag.corpus_manifest import build_manifest, verify_manifest, sha_text
from atlasrag.ingest.refetch import refetch_pdfs


def make_corpus(tmp_path, n=3, with_pdfs=True):
    raw = tmp_path / "raw"; (raw / "pdf").mkdir(parents=True)
    meta = [{"id": f"2401.0000{i}v1", "published": f"2024-01-0{i + 1}T00:00:00", "title": f"T{i}",
             "pdf_url": f"http://x/{i}.pdf"} for i in range(n)]
    (raw / "metadata.jsonl").write_text("\n".join(json.dumps(m) for m in meta) + "\n")
    chunks = [{"chunk_id": f"{m['id']}::0", "paper_id": m["id"], "title": m["title"], "section": "Abstract", "text": "x " * 300} for m in meta]
    (tmp_path / "chunks.jsonl").write_text("\n".join(json.dumps(c) for c in chunks) + "\n")
    if with_pdfs:
        for m in meta:
            (raw / "pdf" / f"{m['id']}.pdf").write_bytes(b"%PDF-" + m["id"].encode())
    return raw, tmp_path / "chunks.jsonl"


def test_manifest_roundtrip_and_drift_detection(tmp_path):
    raw, chunks = make_corpus(tmp_path)
    m = build_manifest("c1", raw / "metadata.jsonl", chunks, raw / "pdf", {"embedding": {"model": "bge"}}, "abc1234")
    assert m["n_papers"] == 3 and m["n_chunks"] == 3 and all(p["pdf_sha256"] for p in m["papers"])
    assert verify_manifest(m, raw / "metadata.jsonl", chunks, raw / "pdf") == {"errors": [], "warnings": []}
    crlf = chunks.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")  # a Windows checkout must not look like drift
    chunks.write_bytes(crlf)
    assert verify_manifest(m, raw / "metadata.jsonl", chunks)["errors"] == []
    chunks.write_text(chunks.read_text().replace("x x", "y y", 1))
    assert "chunks.jsonl does not match" in verify_manifest(m, raw / "metadata.jsonl", chunks)["errors"][0]


def test_missing_or_changed_pdfs_are_warnings_but_extra_papers_are_errors(tmp_path):
    raw, chunks = make_corpus(tmp_path)
    m = build_manifest("c1", raw / "metadata.jsonl", chunks, raw / "pdf")
    (raw / "pdf" / "2401.00000v1.pdf").unlink()
    (raw / "pdf" / "2401.00001v1.pdf").write_bytes(b"changed")
    res = verify_manifest(m, raw / "metadata.jsonl", chunks, raw / "pdf")
    assert res["errors"] == [] and len(res["warnings"]) == 2
    with open(raw / "metadata.jsonl", "a") as f:
        f.write(json.dumps({"id": "9999.99999v1", "published": "2024-02-01", "title": "extra", "pdf_url": "u"}) + "\n")
    errs = verify_manifest(m, raw / "metadata.jsonl", chunks)["errors"]
    assert any("metadata.jsonl does not match" in e for e in errs) and any("paper ids differ" in e for e in errs)


def test_manifest_without_local_pdfs_has_null_hashes(tmp_path):
    raw, chunks = make_corpus(tmp_path, with_pdfs=False)
    m = build_manifest("c1", raw / "metadata.jsonl", chunks, raw / "pdf")
    assert all(p["pdf_sha256"] is None for p in m["papers"])
    assert sha_text(chunks) == m["chunks_sha256"]


def test_refetch_only_downloads_missing_pdfs_and_records_failures(tmp_path, monkeypatch):
    raw, _ = make_corpus(tmp_path, with_pdfs=False)
    (raw / "pdf" / "2401.00000v1.pdf").write_bytes(b"already here")
    got = []

    def fake_get(url, **kw):
        got.append(url)
        return types.SimpleNamespace(status_code=404 if url.endswith("/2.pdf") else 200, content=b"%PDF-new")
    import atlasrag.ingest.refetch as rf
    monkeypatch.setattr(rf.requests, "get", fake_get)
    monkeypatch.setattr(rf.time, "sleep", lambda *_: None)
    dry = refetch_pdfs(raw / "metadata.jsonl", raw / "pdf", dry_run=True)
    assert dry["present"] == 1 and dry["to_download"] == 2 and got == []
    res = refetch_pdfs(raw / "metadata.jsonl", raw / "pdf", log=lambda *_: None)
    assert res["downloaded"] == 1 and res["failed"] == [{"id": "2401.00002v1", "status": 404}]
    assert (raw / "pdf" / "2401.00000v1.pdf").read_bytes() == b"already here"        # never overwrites
    assert got == ["http://x/1.pdf", "http://x/2.pdf"]


class FakeEmbedder:
    def encode_docs(self, texts, batch_size=32):
        return np.random.RandomState(len(texts)).rand(len(texts), 4).astype("float32")


def test_rebuild_index_from_chunks_needs_no_pdfs(tmp_path):
    pytest.importorskip("rank_bm25")
    from atlasrag.retrieval.rebuild import rebuild_index
    from atlasrag.retrieval.index import Index
    _, chunks = make_corpus(tmp_path, with_pdfs=False)
    ix = rebuild_index(chunks, tmp_path / "idx", FakeEmbedder())
    assert len(ix.chunks) == 3 and (tmp_path / "idx" / "emb.npy").exists()
    again = Index.load(tmp_path / "idx")                                  # the loader that needs emb.npy now works
    assert again.emb.shape == (3, 4)
    dup = tmp_path / "dup.jsonl"
    dup.write_text(chunks.read_text() + chunks.read_text().splitlines()[0] + "\n")
    with pytest.raises(ValueError, match="duplicate"):
        rebuild_index(dup, tmp_path / "idx2", FakeEmbedder())
    empty = tmp_path / "empty.jsonl"; empty.write_text("")
    with pytest.raises(ValueError, match="empty"):
        rebuild_index(empty, tmp_path / "idx3", FakeEmbedder())
