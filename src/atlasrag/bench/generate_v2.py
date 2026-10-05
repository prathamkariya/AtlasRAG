"""Quality-gated benchmark candidate generation.

V2.1 improves pair selection and candidate structure before the support audit:
- multi-hop/conflicting candidates come from related cross-paper neighbors, but
  the generator must explicitly state what each passage contributes and why the
  answer needs both;
- temporal candidates are generated only with an explicit same-quantity/claim
  check and earlier/later dates;
- chain candidates must ask for later-section evidence supporting a concrete
  abstract claim rather than asking about a fact already stated in the abstract.

Survivors are still candidates until human review accepts them.
"""
from __future__ import annotations
import json
import re
from collections import Counter
from dataclasses import dataclass

import numpy as np

from .generate import Generator, COMMON, TASKS, EVIDENCE_SECT
from .schema import Question, make_id, paper_split
from .validate import judge_support, verdict
from ..llm import LLMRateLimitExceeded

STRUCTURED_TASKS = {
    "multi_hop": """Use BOTH passages in a genuinely joint question. Identify one substantive contribution from each passage and make the reference answer depend on both. If either passage is merely background, or if no joint question is possible, reply {\"question\":\"NONE\"}.""",
    "conflicting": """Use BOTH passages only if they report findings that disagree or are in tension about the SAME quantity or claim. State the contribution of each passage. If they are not genuinely comparable, reply {\"question\":\"NONE\"}.""",
    "temporal": """Passage A is earlier and Passage B is later. They MUST address the SAME scientific quantity or claim and provide enough evidence to describe a real update or change. If the quantities/claims differ, or there is no meaningful change to report, reply {\"question\":\"NONE\"}.""",
    "chain": """Passage A is an abstract and Passage B is a later section of the SAME paper. Ask about a specific claim from A whose support/evidence/method/result is supplied by B. The answer MUST need a substantive detail from B and must not be answerable from A alone. If that is impossible, reply {\"question\":\"NONE\"}.""",
}

STRUCTURED_SYSTEM = COMMON + """ For non-simple tasks, return JSON with exactly these useful fields:
{\"question\":\"...\",\"reference_answer\":\"...\",\"passage_1_contribution\":\"...\",\"passage_2_contribution\":\"...\",\"joint_reason\":\"...\",\"same_quantity\":true|false|null}. \
Do not copy distinctive wording from the passages. Keep the reference answer to 1-3 sentences. Return question NONE when the requested structure cannot be satisfied."""

_NON_SCIENTIFIC_TERMS = {
    "about", "after", "also", "analysis", "between", "could", "discussion",
    "early", "first", "from", "into", "later", "method", "model", "paper",
    "passage", "reported", "results", "section", "should", "study", "that",
    "their", "there", "these", "this", "through", "using", "which", "with",
    "were", "been", "being", "does", "find", "finds", "gave", "gives",
    "have", "into", "more", "most", "over", "same", "than", "then", "they",
    "what", "when", "where", "would", "your", "abstract", "introduction",
}
_TEMPORAL_EVIDENCE_TERMS = {
    "constraint", "conclusion", "estimate", "measurement", "posterior", "result",
    "tension", "update", "updated", "revised", "improve", "improved", "change",
    "changed", "refine", "refined", "increase", "decrease",
}


@dataclass(frozen=True)
class PairAssessment:
    score: float = 0.0
    reason: str | None = None
    shared_signals: frozenset[str] = frozenset()


def scientific_signals(text: str) -> set[str]:
    """Extract conservative lexical/entity signals without a corpus-specific lexicon."""
    words = re.findall(r"[A-Za-z][A-Za-z0-9_+\-]*", text)
    out = set()
    for word in words:
        low = word.lower()
        is_parameter = bool(re.fullmatch(r"[a-zA-Z][0-9]+", word))
        is_acronym = len(word) >= 2 and word.isupper()
        if (len(low) >= 4 or is_parameter or is_acronym) and low not in _NON_SCIENTIFIC_TERMS:
            out.add(low)
    return out


def specific_scientific_signals(text: str) -> set[str]:
    """Return high-precision anchors: acronyms, parameters, and model symbols."""
    patterns = (
        r"\b[A-Z]{2,}[A-Za-z0-9_+\-]*\b",       # DESI, BAO, FLRW
        r"\b[A-Za-z]*\d+[A-Za-z0-9_+\-]*\b",   # H0, Neff, omega_b2
        r"\b[a-z][A-Z][A-Za-z0-9_+\-]*\b",      # mH, wCDM
        r"[ΩΩΛΔξωλδ][A-Za-z0-9_+\-]+",              # Ωm, ΛCDM, ΔNeff
        r"[ΩΛΔξ][A-Za-z0-9_+\-]+",                # Ωm, ΛCDM, ΔNeff
    )
    return {
        match.lower()
        for pattern in patterns
        for match in re.findall(pattern, text)
    }


def _signal_similarity(a: str, b: str) -> float:
    signals_a, signals_b = scientific_signals(a), scientific_signals(b)
    union = signals_a | signals_b
    return len(signals_a & signals_b) / len(union) if union else 0.0


def _has_temporal_evidence(text: str) -> bool:
    terms = scientific_signals(text)
    return bool(terms & _TEMPORAL_EVIDENCE_TERMS)


def assess_cross_paper_pair(passage_a: str, passage_b: str, *, qtype: str,
                            dense_similarity: float, date_a: str | None = None,
                            date_b: str | None = None, section_a: str = "",
                            section_b: str = "") -> PairAssessment:
    """Score a cross-paper pair or return an interpretable deterministic rejection."""
    signals_a, signals_b = scientific_signals(passage_a), scientific_signals(passage_b)
    shared = signals_a & signals_b
    if len(shared) < 2:
        return PairAssessment(reason="no_shared_scientific_signal", shared_signals=frozenset(shared))
    if not (specific_scientific_signals(passage_a) & specific_scientific_signals(passage_b)):
        return PairAssessment(reason="no_shared_specific_signal", shared_signals=frozenset(shared))
    duplicate_similarity = _signal_similarity(passage_a, passage_b)
    if duplicate_similarity >= 0.80:
        return PairAssessment(reason="near_duplicate_passages", shared_signals=frozenset(shared))
    if qtype == "multi_hop" and (not signals_a - shared or not signals_b - shared):
        return PairAssessment(reason="not_complementary_evidence", shared_signals=frozenset(shared))
    if qtype == "temporal":
        if not date_a or not date_b or date_a >= date_b:
            return PairAssessment(reason="temporal_bad_dates", shared_signals=frozenset(shared))
        if not EVIDENCE_SECT.search(section_a) or not EVIDENCE_SECT.search(section_b):
            return PairAssessment(reason="temporal_weak_section", shared_signals=frozenset(shared))
        if not _has_temporal_evidence(passage_a) or not _has_temporal_evidence(passage_b):
            return PairAssessment(reason="temporal_no_update_signal", shared_signals=frozenset(shared))
    complementarity = min(len(signals_a - shared), len(signals_b - shared))
    score = (3.0 * len(shared)) + min(complementarity, 6) + max(dense_similarity, 0.0)
    return PairAssessment(score=score, shared_signals=frozenset(shared))


def assess_chain_pair(abstract: str, evidence: str, *, same_paper: bool,
                      section: str) -> PairAssessment:
    """Require a same-paper abstract/evidence pairing with a concrete overlap."""
    if not same_paper:
        return PairAssessment(reason="chain_different_paper")
    if not EVIDENCE_SECT.search(section):
        return PairAssessment(reason="no_evidence_section")
    signals_a, signals_b = scientific_signals(abstract), scientific_signals(evidence)
    shared = signals_a & signals_b
    if len(shared) < 2:
        return PairAssessment(reason="no_shared_scientific_signal", shared_signals=frozenset(shared))
    if _signal_similarity(abstract, evidence) >= 0.80:
        return PairAssessment(reason="near_duplicate_passages", shared_signals=frozenset(shared))
    return PairAssessment(score=(3.0 * len(shared)) + min(len(signals_b - shared), 6),
                          shared_signals=frozenset(shared))


def has_shared_scientific_signal(passage_a: str, passage_b: str) -> bool:
    """Conservative prefilter for pairs that can support a comparison.

    It does not decide semantic equivalence; it avoids spending an LLM call on
    pairs linked only by embedding-neighbour noise or publication date.
    """
    return len(scientific_signals(passage_a) & scientific_signals(passage_b)) >= 2


def _parse_structured(text: str):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    q = str(d.get("question", "")).strip()
    if len(q) < 15 or q.upper().startswith("NONE"):
        return None
    a = str(d.get("reference_answer", "")).strip()
    if not a:
        return None
    return d


class ValidatedGenerator(Generator):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.text_of = {c["chunk_id"]: c["text"] for c in self.ix.chunks}
        self.vstats: Counter = Counter()

    def _cosine_similarity(self, i: int, j: int) -> float:
        a, b = self.ix.emb[i], self.ix.emb[j]
        denom = float(np.linalg.norm(a) * np.linalg.norm(b))
        return float(a @ b / denom) if denom else 0.0

    def _candidate_pool(self, i: int, limit: int = 80) -> tuple[set[int], dict[int, float]]:
        """Union dense and BM25 candidates before applying pair semantics."""
        dense = self.ix.dense(self.ix.emb[i], limit)
        query = " ".join(sorted(scientific_signals(self.ix.chunks[i]["text"])))
        lexical = self.ix.bm25(query, limit) if query else []
        pool = {j for j, _ in dense} | {j for j, _ in lexical}
        rank_bonus = {}
        for rank, (j, _) in enumerate(dense):
            rank_bonus[j] = rank_bonus.get(j, 0.0) + 1.0 / (rank + 1)
        for rank, (j, _) in enumerate(lexical):
            rank_bonus[j] = rank_bonus.get(j, 0.0) + 1.0 / (rank + 1)
        return pool, rank_bonus

    def _rank_cross_paper_candidates(self, i: int, split: str, qtype: str,
                                     limit: int = 12) -> list[tuple[int, float]]:
        """Return only deterministic, structurally promising cross-paper pairs."""
        chunks = self.ix.chunks
        pool, rank_bonus = self._candidate_pool(i)
        ranked = []
        for j in pool:
            if j == i or self.paper_of[j] == self.paper_of[i]:
                continue
            if paper_split(self.paper_of[j]) != split or len(chunks[j]["text"]) < 500:
                continue
            date_a, date_b = self._date(self.paper_of[i]), self._date(self.paper_of[j])
            args = (chunks[i]["text"], chunks[j]["text"])
            kwargs = {
                "qtype": qtype,
                "dense_similarity": self._cosine_similarity(i, j),
                "date_a": date_a,
                "date_b": date_b,
                "section_a": chunks[i]["section"],
                "section_b": chunks[j]["section"],
            }
            if qtype == "temporal" and date_a > date_b:
                args = (chunks[j]["text"], chunks[i]["text"])
                kwargs.update(date_a=date_b, date_b=date_a,
                              section_a=chunks[j]["section"], section_b=chunks[i]["section"])
            assessed = assess_cross_paper_pair(*args, **kwargs)
            if assessed.reason:
                self.vstats[f"pair_{assessed.reason}"] += 1               # legacy key (all types mixed)
                self.vstats[f"pair:{qtype}:{assessed.reason}"] += 1       # attributable per type
                continue
            ranked.append((j, assessed.score + rank_bonus.get(j, 0.0)))
        return sorted(ranked, key=lambda pair: (-pair[1], pair[0]))[:limit]

    def _rank_chain_candidates(self, i: int, limit: int = 12) -> list[tuple[int, int, float]]:
        """Rank evidence-bearing same-paper chunks against their paper abstract."""
        chunks = self.ix.chunks
        paper_id = self.paper_of[i]
        abstract = self._abstract_of(paper_id)
        if abstract is None:
            self.vstats["no_abstract"] += 1
            return []
        ranked = []
        for j, chunk in enumerate(chunks):
            if j == abstract or self.paper_of[j] != paper_id or len(chunk["text"]) < 500:
                continue
            assessed = assess_chain_pair(chunks[abstract]["text"], chunk["text"],
                                         same_paper=True, section=chunk["section"])
            if assessed.reason:
                self.vstats[f"pair_{assessed.reason}"] += 1               # legacy key (all types mixed)
                self.vstats[f"pair:chain:{assessed.reason}"] += 1         # attributable per type
                continue
            ranked.append((abstract, j, assessed.score + self._cosine_similarity(abstract, j)))
        return sorted(ranked, key=lambda pair: (-pair[2], pair[1]))[:limit]

    def _choose_neighbor(self, i: int, split: str, qtype: str):
        ranked = self._rank_cross_paper_candidates(i, split, qtype)
        return ranked[0][0] if ranked else None

    def _ask_structured(self, qtype: str, body: str):
        task = STRUCTURED_TASKS[qtype]
        try:
            out = self.llm.chat(
                [{"role": "system", "content": STRUCTURED_SYSTEM + " " + task},
                 {"role": "user", "content": body}],
                temperature=0.2,
                max_tokens=450,
                model=self.model,
            )
        except LLMRateLimitExceeded:
            self.vstats["rate_limited"] += 1
            return None
        return _parse_structured(out)

    def _structural_ok(self, qtype: str, d: dict) -> bool:
        if qtype == "simple":
            return True
        required = ("passage_1_contribution", "passage_2_contribution", "joint_reason")
        if not all(isinstance(d.get(k), str) and d[k].strip() for k in required):
            self.vstats["missing_structured_evidence"] += 1
            return False
        role_a = re.sub(r"\W+", " ", d["passage_1_contribution"].lower()).strip()
        role_b = re.sub(r"\W+", " ", d["passage_2_contribution"].lower()).strip()
        if role_a == role_b:
            self.vstats["non_distinct_passage_contributions"] += 1
            return False
        is_comparison = re.search(
            r"\b(compare|comparison|better|best|outperform|versus|vs\.?|agree|disagree|differ)\b",
            d["question"], re.I,
        )
        if qtype == "multi_hop" and is_comparison and d.get("same_quantity") is not True:
            self.vstats["comparison_without_shared_quantity"] += 1
            return False
        if qtype in ("temporal", "conflicting") and d.get("same_quantity") is not True:
            self.vstats["different_quantity"] += 1
            return False
        return True

    def _judge(self, question: str, reference: str, passages: list[str]):
        try:
            return judge_support(self.llm, question, reference, passages, model=self.model)
        except LLMRateLimitExceeded:
            self.vstats["rate_limited"] += 1
            return None

    def _simple_ok(self, question: str) -> bool:
        if re.search(r"\b(passages?|texts?)\b", question, re.I):
            self.vstats["simple_mentions_source"] += 1
            return False
        if re.search(r"\bwhich reference\b", question, re.I):
            self.vstats["citation_trivia"] += 1
            return False
        return True

    def make(self, qtype, split):
        q = self._make(qtype, split)
        self.vstats[f"attempt:{qtype}"] += 1
        if q is not None:
            self.vstats[f"survived:{qtype}"] += 1
        return q

    def _make(self, qtype, split):
        pool = self.pool[split]
        if not pool:
            return None
        ch = self.ix.chunks
        i = self.rng.choice(pool)
        idxs = [i]

        if qtype == "simple":
            try:
                qa = self._ask(TASKS[qtype], f"Passage:\n{ch[i]['text'][:1200]}")
            except LLMRateLimitExceeded:
                self.vstats["rate_limited"] += 1
                return None
            if qa is None:
                self.vstats["generator_returned_none"] += 1
                return None
            question, ref = qa
            if not self._simple_ok(question):
                return None
            validation = self._judge(question, ref, [ch[i]["text"]])
            if validation is None:
                return None
            ok, reasons = verdict(validation, qtype)
            payload = {"ok": ok, "reasons": reasons, "verdict": validation}
            q = self._build(qtype, question, ref, idxs, ch, split, payload)
            if not ok:
                for r in reasons: self.vstats[r] += 1
                return None
            self.vstats["passed"] += 1
            return q

        if qtype in ("multi_hop", "conflicting", "temporal"):
            j = self._choose_neighbor(i, split, qtype)
            if j is None:
                self.vstats["no_valid_pair"] += 1
                return None
            da = self._date(self.paper_of[i])
            db = self._date(self.paper_of[j])
            if qtype == "temporal":
                if not da or not db or da == db:
                    self.vstats["temporal_bad_dates"] += 1
                    return None
                idxs = [i, j] if da < db else [j, i]
                a, b = idxs
                body = (f"Passage A (earlier, {self._date(self.paper_of[a])}):\n{ch[a]['text'][:1200]}"
                        f"\n\nPassage B (later, {self._date(self.paper_of[b])}):\n{ch[b]['text'][:1200]}")
            else:
                idxs = [i, j]
                body = f"Passage A:\n{ch[i]['text'][:1200]}\n\nPassage B:\n{ch[j]['text'][:1200]}"
            d = self._ask_structured(qtype, body)
            if d is None:
                self.vstats["generator_returned_none"] += 1
                return None
            if not self._structural_ok(qtype, d):
                return None

        elif qtype == "chain":
            ranked = self._rank_chain_candidates(i)
            if not ranked:
                self.vstats["no_valid_chain_pair"] += 1
                return None
            a, j, _ = ranked[0]
            idxs = [a, j]
            body = (f"Passage A (abstract):\n{ch[a]['text'][:1200]}\n\n"
                    f"Passage B ({ch[j]['section']}):\n{ch[j]['text'][:1200]}")
            d = self._ask_structured(qtype, body)
            if d is None:
                self.vstats["generator_returned_none"] += 1
                return None
            if not self._structural_ok(qtype, d):
                return None
        else:
            raise ValueError(qtype)

        question = d["question"].strip()
        ref = d["reference_answer"].strip()
        passages = [ch[k]["text"] for k in idxs]
        audit = self._judge(question, ref, passages)
        if audit is None:
            return None
        ok, reasons = verdict(audit, qtype)
        payload = {
            "ok": ok,
            "reasons": reasons,
            "verdict": audit,
            "generation_structure": {
                "passage_1_contribution": d.get("passage_1_contribution", ""),
                "passage_2_contribution": d.get("passage_2_contribution", ""),
                "joint_reason": d.get("joint_reason", ""),
                "same_quantity": d.get("same_quantity"),
            },
        }
        q = self._build(qtype, question, ref, idxs, ch, split, payload)
        if not ok:
            for r in reasons: self.vstats[r] += 1
            return None
        self.vstats["passed"] += 1
        return q

    def _build(self, qtype, question, ref, idxs, ch, split, payload):
        papers = list(dict.fromkeys(self.paper_of[k] for k in idxs))
        q = Question(
            id=make_id(qtype, question),
            question=question,
            qtype=qtype,
            reference_answer=ref,
            gold_chunk_ids=[ch[k]["chunk_id"] for k in idxs],
            gold_paper_ids=papers,
            split=split,
            status="candidate",
        )
        q.validation = json.dumps(payload)
        return q
