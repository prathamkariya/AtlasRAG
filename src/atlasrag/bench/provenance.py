"""Fail-closed provenance checks for frozen benchmark question files."""
from __future__ import annotations

import json
import re
from pathlib import Path

from .finalize import sha_text_bytes

MANIFEST_NAME = "benchmark_manifest.json"
_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
ORACLE_LABELS = frozenset({"SIMPLE", "MULTI_HOP", "UNCERTAIN"})


class BenchmarkProvenanceError(ValueError):
    """Base class for benchmark provenance failures."""


class BenchmarkManifestMissing(BenchmarkProvenanceError):
    """No manifest accompanies the question file."""


class BenchmarkManifestInvalid(BenchmarkProvenanceError):
    """The manifest cannot safely identify a frozen benchmark."""


class BenchmarkQuestionFileInvalid(BenchmarkProvenanceError):
    """The question file is missing or empty."""


class BenchmarkHashMismatch(BenchmarkProvenanceError):
    """A valid manifest records a different digest for the question file."""


def questions_sha256(path: str | Path) -> str:
    """Return the full CRLF-normalized SHA-256 used by finalization manifests."""
    return sha_text_bytes(Path(path).read_bytes())


def _load_manifest(path: Path) -> dict:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BenchmarkManifestInvalid(f"invalid JSON manifest {path}: {exc}") from exc
    if not isinstance(manifest, dict):
        raise BenchmarkManifestInvalid(f"manifest {path} must contain a JSON object")
    benchmark_id = manifest.get("benchmark_id")
    if not isinstance(benchmark_id, str) or not benchmark_id.strip():
        raise BenchmarkManifestInvalid(f"manifest {path} has no non-empty benchmark_id")
    expected = manifest.get("questions_sha256")
    if not isinstance(expected, str) or not _SHA256.fullmatch(expected):
        raise BenchmarkManifestInvalid(
            f"manifest {path} has no valid questions_sha256 (expected 64 hexadecimal characters)"
        )
    return {"benchmark_id": benchmark_id, "questions_sha256": expected.lower()}


def verify_benchmark(questions_path: str | Path, manifest_path: str | Path | None = None) -> dict:
    """Verify that a non-empty question file matches its complete manifest.

    Only :class:`BenchmarkHashMismatch` is an overrideable content mismatch.
    Missing files and invalid manifests intentionally fail closed.
    """
    question_file = Path(questions_path)
    manifest_file = Path(manifest_path) if manifest_path else question_file.parent / MANIFEST_NAME
    if not question_file.is_file():
        raise BenchmarkQuestionFileInvalid(f"question file not found: {question_file}")
    if question_file.stat().st_size == 0:
        raise BenchmarkQuestionFileInvalid(f"question file is empty (0 bytes): {question_file}")
    if not manifest_file.is_file():
        raise BenchmarkManifestMissing(f"no {MANIFEST_NAME} next to {question_file}")
    manifest = _load_manifest(manifest_file)
    actual = questions_sha256(question_file)
    expected = manifest["questions_sha256"]
    if actual != expected:
        raise BenchmarkHashMismatch(
            f"questions_sha256 mismatch for {question_file}: file={actual[:12]} manifest={expected[:12]}. "
            "Restore the question file or deliberately refresh its manifest."
        )
    return {
        "benchmark_id": manifest["benchmark_id"],
        "questions_sha256": actual,
        "manifest_path": str(manifest_file),
    }


def load_oracle_labels(path: str | Path, question_ids) -> dict[str, str]:
    """Load a complete, valid v1 Oracle-label sidecar for ``question_ids``."""
    sidecar = Path(path)
    try:
        payload = json.loads(sidecar.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BenchmarkProvenanceError(f"invalid Oracle sidecar {sidecar}: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("labels"), dict):
        raise BenchmarkProvenanceError(f"Oracle sidecar {sidecar} must be a JSON object with a labels object")
    labels = payload["labels"]
    expected = set(question_ids)
    actual = set(labels)
    if actual != expected:
        missing, extra = sorted(expected - actual), sorted(actual - expected)
        details = []
        if missing:
            details.append(f"missing IDs: {', '.join(missing[:3])}")
        if extra:
            details.append(f"unknown IDs: {', '.join(extra[:3])}")
        raise BenchmarkProvenanceError(f"Oracle sidecar {sidecar} IDs do not match benchmark ({'; '.join(details)})")
    non_string = sorted(key for key, value in labels.items() if not isinstance(value, str))
    if non_string:
        raise BenchmarkProvenanceError(
            f"Oracle sidecar {sidecar} route labels must be strings; invalid values for: "
            f"{', '.join(non_string[:3])}"
        )
    invalid = sorted(key for key, value in labels.items() if value not in ORACLE_LABELS)
    if invalid:
        raise BenchmarkProvenanceError(
            f"Oracle sidecar {sidecar} has invalid route labels for: {', '.join(invalid[:3])}"
        )
    return labels
