import numpy as np
import pytest

pytest.importorskip("rank_bm25")
from atlasrag.retrieval.index import Index


def test_index_dense_and_bm25(tmp_path):
    chunks = [{"chunk_id": f"p::{i}", "paper_id": "p", "title": "T", "section": "S", "text": t}
              for i, t in enumerate(["dark energy equation of state", "exoplanet transit photometry",
                                     "hubble constant cepheid calibration"])]
    emb = np.eye(3, dtype="float32")
    idx = Index(chunks, emb)
    assert idx.dense(np.array([0, 1, 0], dtype="float32"), 1)[0][0] == 1
    assert idx.bm25("cepheid hubble", 1)[0][0] == 2


def test_pdf_roundtrip(tmp_path):
    fitz = pytest.importorskip("pymupdf")
    from atlasrag.ingest.pdf_parse import extract_text, split_sections
    doc = fitz.open()
    page = doc.new_page()
    page.insert_textbox(fitz.Rect(50, 50, 500, 80), "1 Introduction", fontsize=12)
    page.insert_textbox(fitz.Rect(50, 120, 500, 300),
                        "We study the expansion rate of the universe using standard candles.", fontsize=10)
    page.insert_textbox(fitz.Rect(50, 340, 500, 370), "2 Methods", fontsize=12)
    page.insert_textbox(fitz.Rect(50, 410, 500, 600),
                        "Distances are calibrated with parallaxes and detached eclipsing binaries.", fontsize=10)
    p = tmp_path / "t.pdf"
    doc.save(str(p))
    names = [n for n, _ in split_sections(extract_text(p))]
    assert "Introduction" in names and "Methods" in names
