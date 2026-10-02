"""LLM audit of whether a question is actually supported by its gold evidence.

The audit remains a filter, not ground truth. For multi-passage questions it also
checks that the generated structure explicitly assigns a contribution to each
passage, while temporal/conflicting questions must track the same quantity/claim.
"""
from __future__ import annotations
import json
import re

SYSTEM = """You audit evaluation questions for a retrieval system over astrophysics papers.
Use ONLY the numbered passages. Do not use outside knowledge.
Reply with JSON only:
{
  "answer_supported": true|false,
  "unsupported_claims": ["..."],
  "needs_all_passages": true|false,
  "passage_1_contribution": "what passage 1 contributes, or empty if irrelevant",
  "passage_2_contribution": "what passage 2 contributes, or empty if irrelevant",
  "joint_reason": "why both passages are required, or empty",
  "quantities_comparable": true|false|null,
  "same_quantity": true|false|null,
  "problems": "one short sentence or empty"
}
For multi-hop/chain questions, needs_all_passages is true only when the answer
requires substantive evidence from every passage. Merely providing background
or context does not count. The two contribution fields and joint_reason must
explain distinct, answer-relevant roles.
For temporal/conflicting questions, same_quantity is true only when both passages
address the same scientific quantity or claim. For numeric comparisons,
quantities_comparable is true only for the same kind of quantity with compatible
units.
"""

MAXC = 1500


def parse_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return {}
    raw = re.sub(r"//[^\n]*", "", m.group(0))
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def judge_support(llm, question: str, reference: str, passages: list[str], model: str | None = None) -> dict:
    body = "\n\n".join(f"[{i}] {p[:MAXC]}" for i, p in enumerate(passages, 1))
    out = llm.chat(
        [{"role": "system", "content": SYSTEM},
         {"role": "user", "content": f"Passages:\n{body}\n\nQuestion: {question}\nReference answer: {reference}"}],
        temperature=0.0,
        max_tokens=400,
        model=model,
    )
    return parse_json(out)


def _nonempty(v) -> bool:
    return isinstance(v, str) and bool(v.strip())


def verdict(v: dict, qtype: str) -> tuple[bool, list[str]]:
    """Pure function: judge output + question type -> (passes, reasons)."""
    if not v:
        return False, ["judge_unparseable"]
    reasons = []
    if v.get("answer_supported") is not True:
        reasons.append("answer_not_supported")
    if qtype != "simple" and v.get("needs_all_passages") is not True:
        reasons.append("not_all_passages_needed")
    if qtype != "simple":
        if not _nonempty(v.get("passage_1_contribution")) or not _nonempty(v.get("passage_2_contribution")):
            reasons.append("missing_passage_contributions")
        if not _nonempty(v.get("joint_reason")):
            reasons.append("missing_joint_reason")
    if v.get("quantities_comparable") is False:
        reasons.append("quantities_not_comparable")
    if qtype in ("temporal", "conflicting") and v.get("same_quantity") is not True:
        reasons.append("different_quantity")
    return (not reasons), reasons
