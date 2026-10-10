"""Guardrails for what may live in Git. They exist because a 297 MB commit (119 PDFs, a duplicate index file, patch
files and generated views) once went straight to main. If one of these fails, fix the REPO, not the test; extend an
allowlist only with a reason."""
import hashlib
import re
import subprocess
from collections import defaultdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 8_000_000                  # chunks.jsonl for ~120 papers is ~7 MB
FORBIDDEN_SUFFIXES = {".pdf", ".npy", ".npz", ".zip", ".patch", ".pt", ".safetensors", ".bin", ".pkl"}
FORBIDDEN_DIR_PREFIXES = ("data/index",)    # embeddings/indexes are rebuilt, not stored (data/index*/ ...)
FORBIDDEN_DIR_REGEX = re.compile(r"^data/raw[^/]*/pdf/")
ROOT_ALLOWED = {".dockerignore", ".env.example", ".gitignore", "Dockerfile", "Makefile", "README.md",
                "docker-compose.yml", "pytest.ini", "requirements.txt", "LICENSE"}
LLM_CACHE_ALLOWED = "data/llm_cache/default/"      # only the Run 1 namespace is tracked
DOCS_MAX_LINES = 8000                              # docs/ is for the current design record, not for planning ahead
IDENTICAL_ALLOWED = [{"data/bench/questions.jsonl", "data/bench/questions_v1_frozen.jsonl"}]   # intentional frozen copy


def tracked():
    try:
        out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except Exception:
        pytest.skip("not a git checkout")
    return [p for p in out.splitlines() if p and (ROOT / p).is_file()]


def test_no_binary_or_generated_artifacts_tracked():
    bad = [p for p in tracked() if Path(p).suffix.lower() in FORBIDDEN_SUFFIXES
           or p.startswith(FORBIDDEN_DIR_PREFIXES) or FORBIDDEN_DIR_REGEX.match(p)]
    assert not bad, f"{len(bad)} artifact(s) must not be in Git (PDFs, indexes, patches, archives): {bad[:8]}"


def test_no_large_tracked_files():
    big = [(p, (ROOT / p).stat().st_size) for p in tracked() if (ROOT / p).stat().st_size > MAX_FILE_BYTES]
    assert not big, f"tracked files over {MAX_FILE_BYTES / 1e6:.0f} MB: {big}"


def test_repo_root_has_no_stray_files():
    stray = [p for p in tracked() if "/" not in p and p not in ROOT_ALLOWED]
    assert not stray, f"unexpected files at the repo root (move or delete; extend ROOT_ALLOWED only with a reason): {stray}"


def test_only_the_run1_llm_cache_namespace_is_tracked():
    bad = [p for p in tracked() if p.startswith("data/llm_cache/") and not p.startswith(LLM_CACHE_ALLOWED)]
    assert not bad, f"{len(bad)} cache files outside {LLM_CACHE_ALLOWED} are tracked, e.g. {bad[:3]}"


def test_docs_do_not_sprawl():
    lines = 0
    for p in tracked():
        if p.startswith("docs/") and Path(p).suffix in {".md", ".html", ".txt"}:
            lines += len((ROOT / p).read_text(encoding="utf-8", errors="ignore").splitlines())
    assert lines <= DOCS_MAX_LINES, f"docs/ holds {lines} lines (> {DOCS_MAX_LINES}). Trim before adding more planning text."


def test_no_unintended_duplicate_files_in_bench():
    groups = defaultdict(set)
    for p in tracked():
        if p.startswith("data/bench/") and p.endswith(".jsonl") and (ROOT / p).stat().st_size:
            groups[hashlib.sha256((ROOT / p).read_bytes().replace(b"\r\n", b"\n")).hexdigest()].add(p)
    dupes = [g for g in groups.values() if len(g) > 1 and g not in IDENTICAL_ALLOWED]
    assert not dupes, f"byte-identical benchmark files (a 'v2' that is really v1?): {[sorted(g) for g in dupes]}"


def test_no_secrets_in_tracked_text():
    pat = [re.compile(r"gsk_[A-Za-z0-9]{20,}"), re.compile(r"WANDB_API_KEY\s*=\s*[0-9a-f]{40}")]
    hits = []
    for p in tracked():
        f = ROOT / p
        if p.startswith("data/") or f.stat().st_size > 1_000_000 or f.suffix in {".pdf", ".npy"}:
            continue
        txt = f.read_text(encoding="utf-8", errors="ignore")
        hits += [p for rx in pat if rx.search(txt)]
    assert not hits, f"possible secret in: {hits}"
    assert ".env" not in tracked()
