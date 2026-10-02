"""LLM-assisted CANDIDATE question generation. Nothing here is a benchmark
until a human accepts it (scripts/review_questions.py).

Known biases to keep in mind when reading results:
- gold evidence = the chunks the question was written from. Other chunks may
  also answer it, so recall is a conservative estimate.
- generated questions can echo source wording and flatter lexical retrieval;
  prompts ask for paraphrase, review should reject obvious echoes."""
from __future__ import annotations
import json
import random
import re

import numpy as np

from .schema import Question, make_id, paper_split

SKIP_SECTIONS = {"Front matter"}
EVIDENCE_SECT = re.compile(r"result|method|data|observ|analys|discussion|measure|conclusion", re.I)
MAXC = 1200

COMMON = ("You write evaluation questions for a retrieval system over astrophysics papers. "
          "Questions must be self-contained, specific, paraphrased (do not copy distinctive "
          "phrases), and must not mention 'the passage', 'the text' or paper titles. "
          'Reply with JSON only: {"question": "...", "reference_answer": "..."} '
          '(reference_answer: 1-3 sentences). If the task is impossible for the given '
          'material reply {"question": "NONE"}.')

TASKS = {
    "simple": "Write one factual question answerable from this passage alone.",
    "multi_hop": "Write one question that can ONLY be answered by combining information from BOTH passages (neither alone suffices).",
    "conflicting": ("Do the two passages report findings that disagree or are in tension about the same quantity or claim? "
                    "If not, answer NONE. If so, write a neutral question asking how the findings compare or whether they agree; "
                    "the reference answer must describe the disagreement."),
    "temporal": ("Passage A is from an earlier study and B from a later one. If they address the same quantity or claim, write a question "
                 "about how the reported result changed or was updated; otherwise NONE."),
    "chain": ("Passage A is a paper's abstract and B a later section of the SAME paper. Write one question asking what evidence or method "
              "supports a specific claim made in the abstract; the answer must need B."),
}


def load_meta(raw_dir) -> dict:
    import pathlib
    p = pathlib.Path(raw_dir) / "metadata.jsonl"
    if not p.exists():
        return {}
    return {r["id"]: r for r in (json.loads(l) for l in open(p, encoding="utf-8") if l.strip())}


def parse_qa(text: str):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    q, a = str(d.get("question", "")).strip(), str(d.get("reference_answer", "")).strip()
    if len(q) < 15 or q.upper().startswith("NONE") or not a:
        return None
    return q, a


class Generator:
    def __init__(self, index, llm, meta: dict, seed: int = 0, model: str | None = None):
        self.ix, self.llm, self.meta, self.model = index, llm, meta, model
        self.rng = random.Random(seed)
        self.paper_of = [c["paper_id"] for c in index.chunks]
        self.pool = {"train": [], "test": []}
        for i, c in enumerate(index.chunks):
            if len(c["text"]) >= 500 and c["section"] not in SKIP_SECTIONS:
                self.pool[paper_split(c["paper_id"])].append(i)

    def _neighbor(self, i: int, split: str):
        sims = self.ix.emb @ self.ix.emb[i]
        for j in np.argsort(-sims)[:60]:
            j = int(j)
            if (j != i and self.paper_of[j] != self.paper_of[i]
                    and paper_split(self.paper_of[j]) == split
                    and len(self.ix.chunks[j]["text"]) >= 500):
                return j
        return None

    def _abstract_of(self, paper_id: str):
        for i, c in enumerate(self.ix.chunks):
            if c["paper_id"] == paper_id and c["section"] == "Abstract":
                return i
        return None

    def _date(self, paper_id: str) -> str:
        return str(self.meta.get(paper_id, {}).get("published", ""))[:10]

    def _ask(self, task: str, body: str):
        out = self.llm.chat([{"role": "system", "content": COMMON + " " + task},
                             {"role": "user", "content": body}],
                            temperature=0.3, max_tokens=300, model=self.model)
        return parse_qa(out)

    def make(self, qtype: str, split: str):
        pool = self.pool[split]
        if not pool:
            return None
        ch = self.ix.chunks
        i = self.rng.choice(pool)
        idxs, body = [i], ""
        if qtype == "simple":
            body = f"Passage:\n{ch[i]['text'][:MAXC]}"
        elif qtype in ("multi_hop", "conflicting"):
            j = self._neighbor(i, split)
            if j is None:
                return None
            idxs = [i, j]
            body = f"Passage A:\n{ch[i]['text'][:MAXC]}\n\nPassage B:\n{ch[j]['text'][:MAXC]}"
        elif qtype == "temporal":
            j = self._neighbor(i, split)
            if j is None:
                return None
            da, db = self._date(self.paper_of[i]), self._date(self.paper_of[j])
            if not da or not db or da == db:
                return None
            idxs = [i, j] if da < db else [j, i]
            a, b = idxs
            body = f"Passage A (earlier, {self._date(self.paper_of[a])}):\n{ch[a]['text'][:MAXC]}\n\nPassage B (later, {self._date(self.paper_of[b])}):\n{ch[b]['text'][:MAXC]}"
        elif qtype == "chain":
            if not EVIDENCE_SECT.search(ch[i]["section"]):
                return None
            a = self._abstract_of(self.paper_of[i])
            if a is None:
                return None
            idxs = [a, i]
            body = f"Passage A (abstract):\n{ch[a]['text'][:MAXC]}\n\nPassage B ({ch[i]['section']}):\n{ch[i]['text'][:MAXC]}"
        else:
            raise ValueError(qtype)
        qa = self._ask(TASKS[qtype], body)
        if qa is None:
            return None
        question, ref = qa
        papers = list(dict.fromkeys(self.paper_of[k] for k in idxs))
        return Question(id=make_id(qtype, question), question=question, qtype=qtype,
                        reference_answer=ref, gold_chunk_ids=[ch[k]["chunk_id"] for k in idxs],
                        gold_paper_ids=papers, split=split, status="candidate")
