# Strict-generation smoke review

Command:

```powershell
.\.venv\Scripts\python.exe scripts\gen_questions.py --split test --per-type 1 --types multi_hop chain --attempts 2 --out data/bench/questions_v2_cleanup_smoke.jsonl
```

The only surviving candidate, `multi_hop-721c8f40`, remains `candidate` and
was not promoted.  Its first passage says that generalized PAge can alleviate
a tension in general terms, but does not establish applying GPAge to the H0DN
measurement in the second passage.  The generated answer asserted that
application, so the pair does not support the requested cross-passage link.

No chain candidate survived the two-attempt smoke run.  This failed smoke
result is retained for review; it is not part of `questions_v2_clean.jsonl`.
