"""Read the last run summary written by gen_questions_v2.py and report what a pilot costs per surviving question."""
from __future__ import annotations
import json
from collections import Counter


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
    reasons = Counter({k: v for k, v in o.items() if ":" not in k.split("pair:")[0] or k.startswith("pair:")})
    skip = {"passed", "generator_returned_none"}
    top = [(k, v) for k, v in Counter({k: v for k, v in o.items() if not k.startswith(("attempt:", "survived:")) and k not in skip}).most_common(8)]
    return {"per_type": per_type, "total_survivors": surv, "provider_tokens": tokens,
            "provider_calls": llm.get("provider_calls"), "rate_limit_errors": llm.get("rate_limit_errors"),
            "tokens_per_survivor": round(tokens / surv) if surv else None, "elapsed_s": run.get("elapsed_s"),
            "stopped": run.get("stopped"), "judge_model": run.get("judge_model"), "model": run.get("model"),
            "top_rejection_reasons": top}
