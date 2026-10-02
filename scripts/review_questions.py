"""Review benchmark questions interactively or in batches."""
import argparse
import json
import sys
import textwrap
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

from atlasrag.config import load_config,resolve
from atlasrag.bench.schema import load_questions,save_questions

ap=argparse.ArgumentParser()
ap.add_argument("--file",default="data/bench/questions.jsonl")
ap.add_argument("--split",default="test")
ap.add_argument("--types",nargs="*")
ap.add_argument("--batch",type=int,default=0)
ap.add_argument("--apply",default="")
a=ap.parse_args()

cfg=load_config()

chunks={}
with open(resolve(cfg["retrieval"]["index_dir"])/"chunks.jsonl",encoding="utf-8") as f:
    for line in f:
        c=json.loads(line)
        chunks[c["chunk_id"]]=c

path=resolve(a.file)
allq=load_questions(path)

todo=[
    q for q in allq
    if q.status=="candidate"
    and q.split==a.split
    and (not a.types or q.qtype in a.types)
]

def show_question(n,total,q):
    print("="*80)
    print(f"[{n}/{total}] {q.qtype}   id={q.id}")
    print("Q:",q.question)
    print("A:",q.reference_answer)

    for cid in q.gold_chunk_ids:
        c=chunks.get(cid,{})
        print(
            f"\n--- {cid} | "
            f"{c.get('title','?')[:60]} | "
            f"{c.get('section','?')}"
        )
        print(textwrap.fill(c.get("text","")[:700],100))

# ---------------------------------------------------------
# BATCH EXPORT
# ---------------------------------------------------------
if a.batch>0:
    batch=todo[:a.batch]

    print(f"{len(todo)} candidates remaining")
    print(f"Showing next {len(batch)} questions\n")

    for n,q in enumerate(batch,1):
        show_question(n,len(batch),q)

    print("\nDecision format:")
    print("A = accept")
    print("R = reject")
    print("\nSend the numbered batch to ChatGPT and get back A/R decisions.")

    sys.exit(0)

# ---------------------------------------------------------
# BATCH APPLY
# ---------------------------------------------------------
if a.apply:
    decisions=[
        x.strip().lower()
        for x in a.apply.replace(","," ").split()
        if x.strip()
    ]

    if len(decisions)>len(todo):
        print(
            f"Error: {len(decisions)} decisions supplied "
            f"but only {len(todo)} candidates remain."
        )
        sys.exit(1)

    for i,k in enumerate(decisions):
        if k=="a":
            todo[i].status="accepted"
        elif k=="r":
            todo[i].status="rejected"
        else:
            print(
                f"Error: invalid decision '{k}' at position {i+1}. "
                "Use only a or r."
            )
            sys.exit(1)

    save_questions(path,allq)

    print(f"Applied {len(decisions)} decisions.")
    print(f"Accepted: {decisions.count('a')}")
    print(f"Rejected: {decisions.count('r')}")

    sys.exit(0)

# ---------------------------------------------------------
# ORIGINAL INTERACTIVE MODE
# ---------------------------------------------------------
print(f"{len(todo)} candidates to review\n")

for n,q in enumerate(todo,1):
    show_question(n,len(todo),q)

    while True:
        k=input(
            "\n[a]ccept [r]eject [e]dit-Q [t]edit-A [s]kip [q]uit > "
        ).strip().lower()

        if k=="a":
            q.status="accepted"
            break

        if k=="r":
            q.status="rejected"
            break

        if k=="e":
            q.question=input("new question: ").strip() or q.question
            continue

        if k=="t":
            q.reference_answer=input(
                "new reference: "
            ).strip() or q.reference_answer
            continue

        if k=="s":
            break

        if k=="q":
            save_questions(path,allq)
            sys.exit(0)

    save_questions(path,allq)

print("done")