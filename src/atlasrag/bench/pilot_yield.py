"""Read the last run summary written by gen_questions_v2.py and report what a pilot costs per surviving question."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path


def load_last_run(path) -> dict:
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    if not rows:
        raise ValueError(f"{path} is empty")
    return rows[-1]


def summarize_run(run: dict) -> dict:
    o, llm = run.get("outcomes", {}), run.get("llm", {})
    types = sorted({k.split(":", 1)[1] for k in o if k.startswith("attempt:")})
    per_type = {}
    for t in types:
        a, s = o.get(f"attempt:{t}", 0), o.get(f"survived:{t}", 0)
        per_type[t] = {"attempts": a, "survived": s, "survival_rate": round(s / a, 3) if a else None}
    tokens = llm.get("provider_prompt_tokens", 0) + llm.get("provider_completion_tokens", 0)
    surv = sum(v["survived"] for v in per_type.values())
    skip = {"passed", "generator_returned_none"}
    top = [(k, v) for k, v in Counter({k: v for k, v in o.items() if not k.startswith(("attempt:", "survived:")) and k not in skip}).most_common(8)]
    return {"per_type": per_type, "total_survivors": surv, "provider_tokens": tokens,
            "provider_calls": llm.get("provider_calls"), "rate_limit_errors": llm.get("rate_limit_errors"),
            "tokens_per_survivor": round(tokens / surv) if surv else None, "elapsed_s": run.get("elapsed_s"),
            "stopped": run.get("stopped"), "judge_model": run.get("judge_model"), "model": run.get("model"),
            "top_rejection_reasons": top}


def count_prior_runs(path) -> int:
    """How many runs are already recorded in a runs.jsonl (0 if none). Used to give every resume a NEW random sample stream."""
    p = Path(path)
    return sum(1 for l in open(p, encoding="utf-8") if l.strip()) if p.exists() else 0


def _has_judge_model(q: dict) -> bool:
    try:
        return bool(json.loads(q.get("validation") or "{}").get("judge_model"))
    except json.JSONDecodeError:
        return False


def summarize_pilot(runs: list[dict], questions: list[dict]) -> dict:
    """Whole-pilot totals. Per-run attempt counts are NOT comparable after a resume (cached replays inflate them), so
    the honest yield metrics are: saved candidates (from the file) and provider tokens summed over all runs."""
    llm = lambda r, k: r.get("llm", {}).get(k, 0)
    tokens = sum(llm(r, "provider_prompt_tokens") + llm(r, "provider_completion_tokens") for r in runs)
    n = len(questions)
    return {"runs": len(runs), "saved_total": n, "saved_per_type": dict(Counter(q["qtype"] for q in questions)),
            "distinct_gold_papers": len({p for q in questions for p in q.get("gold_paper_ids", [])}),
            "provider_tokens_total": tokens, "tokens_per_saved_candidate": round(tokens / n) if n else None,
            # NOT a quota figure: it sums both models, retries and replays. Per-model quota is on the provider's usage page.
            "provider_calls_total": sum(llm(r, "provider_calls") for r in runs),
            "cache_hits_total": sum(llm(r, "cache_hits") for r in runs),
            "rate_limit_errors_total": sum(llm(r, "rate_limit_errors") for r in runs),
            "runs_stopped_by_rate_limit": sum(1 for r in runs if (r.get("stopped") or {}).get("reason") == "rate_limited"),
            "runs_stopped_by_token_budget": sum(1 for r in runs if (r.get("stopped") or {}).get("reason") == "token_budget"),
            "generator_models": sorted({r.get("model") for r in runs if r.get("model")}),
            "judge_models": sorted({r.get("judge_model") for r in runs if r.get("judge_model")}),
            "saved_without_judge_model": sum(not _has_judge_model(q) for q in questions)}
