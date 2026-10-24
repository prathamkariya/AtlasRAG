#!/usr/bin/env python3
"""
Safe, resumable wrapper for AtlasRAG's scripts/gen_questions_v2.py.

Defaults:
- Manual execution (no scheduler is installed or configured).
- Generate in batches targeting 5 additional audited candidates per type, up to 50 candidates per type.
- Resume only the selected output file; never edits the existing benchmark file unless
  the user explicitly points --out at it.
- Tracks cumulative provider tokens from <out>.runs.jsonl.
- Rate-limit cooldown uses bounded exponential backoff. Stops when retry limits or
  cumulative token limits are reached. If provider logs indicate quota exhaustion,
  stops immediately rather than repeatedly retrying a daily/monthly quota.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import math
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    rows.append(obj)
            except json.JSONDecodeError:
                print(f"WARNING: ignoring malformed JSON in {path} line {line_no}", file=sys.stderr)
    return rows


def provider_tokens(record: dict[str, Any]) -> int:
    stats = record.get("llm") or {}
    # Prefer provider-reported counts, fall back to generic counters for older runs.
    prompt = stats.get("provider_prompt_tokens", stats.get("prompt_tokens", 0)) or 0
    completion = stats.get("provider_completion_tokens", stats.get("completion_tokens", 0)) or 0
    try:
        return max(0, int(prompt)) + max(0, int(completion))
    except (TypeError, ValueError):
        return 0


def cumulative_tokens(summary_path: Path) -> int:
    return sum(provider_tokens(r) for r in read_jsonl(summary_path))


def existing_counts(out_path: Path, split: str, types: list[str]) -> dict[str, int]:
    counts = {t: 0 for t in types}
    for row in read_jsonl(out_path):
        if row.get("split") != split or row.get("status", "candidate") not in {"candidate", "accepted"}:
            continue
        qtype = row.get("qtype")
        if qtype in counts:
            counts[qtype] += 1
    return counts


def quota_exhausted(summary: dict[str, Any]) -> bool:
    """Conservative detection from error/outcome fields; transient 429s are not quota exhaustion."""
    blob = json.dumps(summary, ensure_ascii=False).lower()
    quota_phrases = (
        "insufficient_quota",
        "billing hard limit",
        "quota exceeded",
        "daily quota",
        "monthly quota",
        "usage limit reached",
        "exceeded your current quota",
        "credit balance is too low",
    )
    return any(p in blob for p in quota_phrases)


def is_rate_limit_stop(exit_code: int, prior_summary_count: int, summary_path: Path) -> bool:
    """Exit code 2 is rate limiting only when this child appended that exact stop record."""
    if exit_code != 2:
        return False
    rows = read_jsonl(summary_path)
    if len(rows) <= prior_summary_count:
        return False
    stopped = rows[-1].get("stopped")
    return isinstance(stopped, dict) and stopped.get("reason") == "rate_limited"


def main() -> int:
    p = argparse.ArgumentParser(description="Resumable AtlasRAG question-generation runner.")
    p.add_argument("--split", choices=("test", "train"), default="test")
    p.add_argument("--types", nargs="+", default=["simple", "multi_hop"])
    p.add_argument("--target-per-type", type=int, default=50,
                   help="target for non-rejected questions per type; candidate rows still need human review.")
    p.add_argument("--batch-size", type=int, default=5,
                   help="maximum additional non-rejected questions targeted per type in each invocation.")
    p.add_argument("--attempts", type=int, default=3,
                   help="candidate attempts per missing question in the generator.")
    p.add_argument("--model", default="qwen/qwen3.8-27b")
    p.add_argument("--judge-model", default="openai/gpt-oss-120b")
    p.add_argument("--generation-reasoning-effort", choices=("low", "medium", "high"), default="medium")
    p.add_argument("--generation-token-headroom", type=int, default=800)
    p.add_argument("--out", default="data/bench/auto_questions_test_20261023.jsonl",
                   help="dedicated output JSONL. Existing file is resumed, not cleared.")
    p.add_argument("--max-total-provider-tokens", type=int, default=100000,
                   help="cumulative token ceiling across all runs (0 disables this ceiling).")
    p.add_argument("--max-provider-tokens-per-run", type=int, default=12000,
                   help="generator's per-invocation provider-token ceiling (0 disables it).")
    p.add_argument("--cooldown-seconds", type=int, default=30,
                   help="fallback cooldown when provider reset timing is not present.")
    p.add_argument("--max-cooldown-seconds", type=int, default=900)
    p.add_argument("--max-rate-limit-retries", type=int, default=4,
                   help="maximum cooldown retries in this execution; then stop cleanly.")
    p.add_argument("--max-batches", type=int, default=100,
                   help="hard safety cap on generator invocations.")
    p.add_argument("--pause-between-batches", type=int, default=20)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if args.target_per_type < 0 or args.batch_size < 1 or args.attempts < 1:
        p.error("target-per-type must be >= 0; batch-size and attempts must be >= 1")
    allowed_types = {"simple", "multi_hop", "conflicting", "temporal", "chain"}
    if not args.types or len(set(args.types)) != len(args.types):
        p.error("--types must contain at least one unique question type")
    unknown_types = sorted(set(args.types) - allowed_types)
    if unknown_types:
        p.error(f"unknown type(s): {', '.join(unknown_types)}; choose from {', '.join(sorted(allowed_types))}")
    if args.generation_token_headroom < 0:
        p.error("--generation-token-headroom must be >= 0")
    if args.cooldown_seconds < 0 or args.max_cooldown_seconds < 0 or args.pause_between_batches < 0:
        p.error("cooldown, max cooldown and pause values must be >= 0")
    if args.max_total_provider_tokens < 0 or args.max_provider_tokens_per_run < 0:
        p.error("token ceilings must be >= 0")
    if args.max_rate_limit_retries < 0 or args.max_batches < 1:
        p.error("retry count must be >= 0 and max-batches must be >= 1")

    root = Path.cwd()
    generator = root / "scripts" / "gen_questions_v2.py"
    if not generator.is_file():
        print(f"ERROR: {generator} not found. Run this from the AtlasRAG repository root.", file=sys.stderr)
        return 2

    out = Path(args.out)
    summary = out.with_suffix(".runs.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    summary.parent.mkdir(parents=True, exist_ok=True)

    # Avoid accidental writes to known baseline names. An explicit override is possible,
    # but requires a deliberate opt-in environment variable.
    protected_names = {"questions.jsonl", "questions_v2.jsonl", "benchmark.jsonl", "bench.jsonl"}
    if out.name.lower() in protected_names and os.environ.get("ATLASRAG_ALLOW_PROTECTED_OUT") != "1":
        print(
            f"ERROR: refusing potentially important benchmark filename {out.name!r}. "
            "Choose a dedicated auto_*.jsonl path. If you intentionally want this, set "
            "ATLASRAG_ALLOW_PROTECTED_OUT=1 first.",
            file=sys.stderr,
        )
        return 2

    print("AtlasRAG automatic generation")
    print(f"  output: {out}")
    print(f"  run log: {summary}")
    print(f"  split/types: {args.split} / {', '.join(args.types)}")
    print(f"  target: {args.target_per_type} non-rejected questions per type; batch size: {args.batch_size}")
    print(f"  cumulative provider tokens already logged: {cumulative_tokens(summary):,}")
    print("  scheduling: manual (this process runs only when launched)")
    print("Existing output is resumed; it will not be truncated.")

    rate_retries = 0
    no_progress_batches = 0
    completed_batches = 0

    while completed_batches < args.max_batches:
        counts = existing_counts(out, args.split, args.types)
        pending = {t: max(0, args.target_per_type - counts.get(t, 0)) for t in args.types}
        if not any(pending.values()):
            print("TARGET REACHED:", counts)
            return 0

        used = cumulative_tokens(summary)
        if args.max_total_provider_tokens and used >= args.max_total_provider_tokens:
            print(f"STOP: cumulative provider token ceiling reached ({used:,} >= {args.max_total_provider_tokens:,}).")
            return 4

        # The generator interprets --per-type as an absolute target for every type
        # passed to one invocation. To keep batches at exactly five new accepted
        # audited candidates per type, process the currently least-filled type(s) together.
        active_counts = [counts.get(t, 0) for t in args.types if pending[t] > 0]
        floor_count = min(active_counts)
        active = [t for t in args.types if pending[t] > 0 and counts.get(t, 0) == floor_count]
        per_type_target = min(args.target_per_type, floor_count + args.batch_size)

        cmd = [
            sys.executable, str(generator),
            "--split", args.split,
            "--per-type", str(per_type_target),
            "--types", *active,
            "--attempts", str(args.attempts),
            "--model", args.model,
            "--judge-model", args.judge_model,
            "--max-provider-tokens", str(args.max_provider_tokens_per_run),
            "--out", str(out),
            "--summary", str(summary),
        ]

        # Confirm the child CLI supports these options; fail clearly rather than silently
        # running with settings different from the user's configured preferences.
        help_run = subprocess.run(
            [sys.executable, str(generator), "--help"],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        help_text = help_run.stdout + help_run.stderr
        for flag in ("--generation-reasoning-effort", "--generation-token-headroom"):
            if flag not in help_text:
                print(f"ERROR: {flag} is missing from gen_questions_v2.py. Apply the generation-controls patch first.", file=sys.stderr)
                return 2
        cmd += [
            "--generation-reasoning-effort", args.generation_reasoning_effort,
            "--generation-token-headroom", str(args.generation_token_headroom),
        ]

        before_counts = existing_counts(out, args.split, args.types)
        print(f"\nBATCH {completed_batches + 1}/{args.max_batches}")
        print("  counts:", before_counts, "targets this run:", {t: per_type_target for t in active})
        print("  command:", subprocess.list2cmdline(cmd))
        if args.dry_run:
            return 0

        summary_count_before = len(read_jsonl(summary))
        proc = subprocess.run(
            cmd, cwd=root, capture_output=True, text=True,
            encoding="utf-8", errors="replace"
        )
        child_output = (proc.stdout or "") + (proc.stderr or "")
        if child_output:
            print(child_output, end="" if child_output.endswith("\n") else "\n")
        completed_batches += 1
        after_counts = existing_counts(out, args.split, args.types)
        made_progress = sum(after_counts.values()) > sum(before_counts.values())
        no_progress_batches = 0 if made_progress else no_progress_batches + 1

        fresh_summaries = read_jsonl(summary)[summary_count_before:]
        latest = fresh_summaries[-1] if fresh_summaries else None
        if latest and quota_exhausted(latest):
            print("STOP: provider quota/billing exhaustion detected in the latest run summary. No retry will be attempted.")
            return 5

        used = cumulative_tokens(summary)
        print(f"  audited candidate counts: {after_counts}")
        print(f"  cumulative provider tokens logged: {used:,}")
        if args.max_total_provider_tokens and used >= args.max_total_provider_tokens:
            print(f"STOP: cumulative provider token ceiling reached ({used:,} >= {args.max_total_provider_tokens:,}).")
            return 4

        if is_rate_limit_stop(proc.returncode, summary_count_before, summary):
            if rate_retries >= args.max_rate_limit_retries:
                print(f"STOP: rate-limit retry cap reached ({rate_retries}/{args.max_rate_limit_retries}). Resume manually later.")
                return 2

            # Groq's error message may provide a precise rolling-window reset hint,
            # e.g. "Please try again in 23.04s". Prefer that over blind long backoff.
            match = re.search(
                r"(?:try again in|retry after)\s*(\d+(?:\.\d+)?)\s*(?:s|sec|seconds)\b",
                child_output,
                flags=re.IGNORECASE,
            )
            if match:
                delay = min(args.max_cooldown_seconds, max(1, math.ceil(float(match.group(1))) + 2))
                delay_source = "provider retry hint plus 2s safety margin"
            else:
                delay = min(args.max_cooldown_seconds, args.cooldown_seconds * (2 ** rate_retries))
                delay_source = "fallback exponential cooldown"

            rate_retries += 1
            print(f"Rate limit detected. Cooling down for {delay}s ({rate_retries}/{args.max_rate_limit_retries}; {delay_source}).")
            time.sleep(delay)
            continue
        if proc.returncode == 4:
            print("STOP: generator's per-run token budget was reached. Saved questions are preserved; rerun later to resume.")
            return 4
        if proc.returncode != 0:
            print(f"STOP: generator exited with code {proc.returncode}. Output is preserved; fix the error and rerun.")
            return proc.returncode

        # A successful batch resets transient rate-limit backoff.
        rate_retries = 0
        if no_progress_batches >= 2:
            print("STOP: two consecutive batches produced no new audited candidates. This avoids burning tokens on a stalled generator.")
            return 6

        if args.pause_between_batches > 0 and any(
            c < args.target_per_type for c in after_counts.values()
        ):
            print(f"Waiting {args.pause_between_batches}s before next batch...")
            time.sleep(args.pause_between_batches)

    print(f"STOP: maximum batch count reached ({args.max_batches}). Rerun this same command to resume.")
    return 7


if __name__ == "__main__":
    raise SystemExit(main())
