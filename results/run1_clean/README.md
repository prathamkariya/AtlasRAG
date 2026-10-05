# Run 1 clean derived report

`report.md` is a derived view of the persisted `results/run1` rows, filtered to
the accepted questions in `data/bench/questions_v2_clean.jsonl`.  No retrieval
or LLM experiment was rerun, and nothing under `results/run1` was changed.

It was produced with:

```powershell
.\.venv\Scripts\python.exe scripts\report.py --group run1 --file data/bench/questions_v2_clean.jsonl --out results/run1_clean/report.md --paired-ref F
```

The clean benchmark removes only questions that the recorded support audit
marked invalid.  This report is therefore useful for sensitivity analysis, not
a replacement for the historical Run 1 report.
