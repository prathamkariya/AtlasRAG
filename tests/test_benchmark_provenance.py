"""Regression tests for the immutable v3 benchmark guard and v1 Oracle sidecar."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from atlasrag.bench.metrics import evidence_recall
from atlasrag.bench.provenance import (
    BenchmarkHashMismatch,
    BenchmarkManifestInvalid,
    BenchmarkManifestMissing,
    BenchmarkQuestionFileInvalid,
    BenchmarkProvenanceError,
    load_oracle_labels,
    questions_sha256,
    verify_benchmark,
)
from atlasrag.routers.base import LABELS

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "data" / "bench" / "final" / "atlasrag-bench-v3"
QFILE = BENCH / "questions_final.jsonl"
MANIFEST = BENCH / "benchmark_manifest.json"
SIDECAR = BENCH / "oracle_v1_labels.json"
RESULTS = ROOT / "results" / "final_v3"


def _copy_bench(tmp_path: Path) -> Path:
    shutil.copy(QFILE, tmp_path / "questions_final.jsonl")
    shutil.copy(MANIFEST, tmp_path / "benchmark_manifest.json")
    return tmp_path / "questions_final.jsonl"


def _question_ids() -> list[str]:
    return [json.loads(line)["id"] for line in QFILE.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_committed_benchmark_matches_its_manifest():
    info = verify_benchmark(QFILE)
    assert info["benchmark_id"] == "atlasrag-bench-v3"
    assert info["questions_sha256"] == "b0144a062d1e8011ec5f77ff38ab0637ff81c4337b028b6770762f95258b0f29"


def test_tampered_questions_are_rejected_and_crlf_is_normalized(tmp_path):
    question_file = _copy_bench(tmp_path)
    question_file.write_bytes(question_file.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    assert verify_benchmark(question_file)["questions_sha256"] == questions_sha256(QFILE)
    question_file.write_bytes(question_file.read_bytes() + b"\n{}\n")
    with pytest.raises(BenchmarkHashMismatch):
        verify_benchmark(question_file)


def test_missing_empty_and_invalid_manifest_inputs_fail_closed(tmp_path):
    question_file = _copy_bench(tmp_path)
    question_file.write_bytes(b"")
    with pytest.raises(BenchmarkQuestionFileInvalid):
        verify_benchmark(question_file)
    shutil.copy(QFILE, question_file)
    (tmp_path / "benchmark_manifest.json").unlink()
    with pytest.raises(BenchmarkManifestMissing):
        verify_benchmark(question_file)
    manifest = tmp_path / "benchmark_manifest.json"
    for content in ("{", "[]", "{}", '{"benchmark_id": " ", "questions_sha256": "0"}',
                    '{"benchmark_id": "v3", "questions_sha256": "not-a-digest"}'):
        manifest.write_text(content, encoding="utf-8")
        with pytest.raises(BenchmarkManifestInvalid):
            verify_benchmark(question_file)


def test_run_experiment_aborts_before_loading_when_hash_mismatches(tmp_path):
    question_file = _copy_bench(tmp_path)
    question_file.write_bytes(question_file.read_bytes() + b"\n")
    group = f"provenance_{tmp_path.name}"
    output_dir = ROOT / "results" / group
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_experiment.py"), "--group", group, "--exp", "B",
         "--file", str(question_file), "--retrieval-only"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert result.returncode != 0
    assert "questions_sha256 mismatch" in (result.stdout + result.stderr)
    assert not output_dir.exists()


def test_run_experiment_default_file_passes_the_manifest_guard(tmp_path):
    group = f"default_path_{tmp_path.name}"
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_experiment.py"), "--group", group, "--exp", "E",
         "--limit", "0", "--retrieval-only"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert result.returncode != 0
    assert "no accepted questions" in (result.stdout + result.stderr)
    assert not (ROOT / "results" / group).exists()


def test_verify_script_exit_codes(tmp_path):
    good = subprocess.run([sys.executable, str(ROOT / "scripts" / "verify_benchmark.py")],
                          capture_output=True, text=True, cwd=ROOT)
    assert good.returncode == 0 and "OK: atlasrag-bench-v3" in good.stdout
    _copy_bench(tmp_path).write_bytes(b"x\n")
    bad = subprocess.run([sys.executable, str(ROOT / "scripts" / "verify_benchmark.py"), "--dir", str(tmp_path)],
                         capture_output=True, text=True, cwd=ROOT)
    assert bad.returncode != 0 and "FAIL:" in (bad.stdout + bad.stderr)


def test_oracle_sidecar_is_complete_and_matches_recorded_e_routes(tmp_path):
    labels = load_oracle_labels(SIDECAR, _question_ids())
    assert len(labels) == 64 and set(labels.values()) <= set(LABELS)
    recorded = RESULTS / "E_oracle.jsonl"
    assert recorded.is_file(), "committed E_oracle rows are required for this regression test"
    rows = [json.loads(line) for line in recorded.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert {row["id"]: row["route"]["label"] for row in rows} == labels
    malformed = tmp_path / "malformed.json"
    malformed.write_text("[]", encoding="utf-8")
    with pytest.raises(BenchmarkProvenanceError):
        load_oracle_labels(malformed, _question_ids())
    partial = tmp_path / "partial.json"
    partial.write_text(json.dumps({"labels": dict(list(labels.items())[1:])}), encoding="utf-8")
    with pytest.raises(BenchmarkProvenanceError, match="IDs do not match"):
        load_oracle_labels(partial, _question_ids())


@pytest.mark.parametrize("bad_label", [["SIMPLE"], {"route": "SIMPLE"}])
def test_oracle_sidecar_rejects_non_string_route_labels(tmp_path, bad_label):
    labels = json.loads(SIDECAR.read_text(encoding="utf-8"))["labels"]
    labels = dict(labels)
    labels[next(iter(labels))] = bad_label
    sidecar = tmp_path / "non_string_label.json"
    sidecar.write_text(json.dumps({"labels": labels}), encoding="utf-8")
    with pytest.raises(BenchmarkProvenanceError, match="route labels must be strings"):
        load_oracle_labels(sidecar, _question_ids())


def test_oracle_sidecar_is_rejected_for_non_oracle_experiments():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_experiment.py"), "--group", "never-created", "--exp", "B",
         "--file", str(QFILE), "--oracle-labels", str(SIDECAR), "--retrieval-only"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert result.returncode != 0
    assert "--oracle-labels is valid only with --exp E" in (result.stdout + result.stderr)
    assert not (ROOT / "results" / "never-created").exists()


def test_committed_final_v3_rows_tie_out_to_current_gold():
    gold = {json.loads(line)["id"]: json.loads(line)["gold_chunk_ids"]
            for line in QFILE.read_text(encoding="utf-8").splitlines() if line.strip()}
    result_files = [path for path in sorted(RESULTS.glob("*.jsonl")) if path.stat().st_size]
    assert result_files, "committed final_v3 result rows are required for this regression test"
    for path in result_files:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                assert evidence_recall(gold[row["id"]], row["retrieved_chunk_ids"]) == pytest.approx(
                    row["evidence_recall"]
                ), (path.name, row["id"])
