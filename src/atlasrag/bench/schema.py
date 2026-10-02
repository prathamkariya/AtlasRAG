from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path

QTYPES = ("simple", "multi_hop", "conflicting", "temporal", "chain")


def paper_split(paper_id: str, test_fraction: float = 0.3) -> str:
    """Paper-level split: a paper is wholly 'train' (feeds Compass training) or
    wholly 'test' (benchmark). Prevents leakage through shared papers."""
    h = int(hashlib.md5(paper_id.encode()).hexdigest(), 16) % 1000
    return "test" if h < test_fraction * 1000 else "train"


@dataclass
class Question:
    id: str
    question: str
    qtype: str
    reference_answer: str
    gold_chunk_ids: list[str]
    gold_paper_ids: list[str]
    split: str = "test"
    status: str = "candidate"          # candidate | accepted | rejected
    gold_route: str | None = None      # filled by oracle labelling
    oracle_sufficient: bool | None = None
    notes: str = ""
    gold_route_v2: str | None = None   # oracle v2 (best-recall, cheapest)
    ladder_recalls: dict | None = None
    validation: str = ""               # support-audit verdict (json)


def load_questions(path, status: str | None = None, split: str | None = None) -> list[Question]:
    path = Path(path)
    if not path.exists():
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                q = Question(**json.loads(line))
                if (status is None or q.status == status) and (split is None or q.split == split):
                    out.append(q)
    return out


def save_questions(path, qs: list[Question]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for q in qs:
            f.write(json.dumps(asdict(q)) + "\n")


def make_id(qtype: str, question: str) -> str:
    return f"{qtype}-{hashlib.sha1(question.encode()).hexdigest()[:8]}"
