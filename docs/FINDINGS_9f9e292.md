# AtlasRAG audit findings (repo state 9f9e292)

> **CORRECTION (after re-auditing the same questions).** Sections 2-3 below report ONE judge run. The same judge on the
> same 27 questions, run again (`data/bench/audit.jsonl`), disagreed on 4 of them (85% raw agreement, but only 6/10 on the
> non-simple questions). Multi-hop: 0/6 pass in the first run, 3/6 in the second. Among the 10 non-simple questions:
> **5 fail in both runs, 1 passes in both, 4 flip.** Read "0/6 multi-hop pass" as "3 of 6 fail in both runs, 3 are unstable".
> What still holds: on every audit-clean subset (19, 21, 18 pass-in-both, 22 pass-in-either) experiments C, E, F and G have
> equal recall (0.82 / 0.79 / 0.83 / 0.77) and A < B = K < them, so routing's measurable value is cost only. But the 18
> pass-in-both questions are 17 simple + 1 temporal, so this says nothing about multi-hop. A single LLM-judge run must not be
> a keep/reject rule: use `scripts/audit_stability.py` (stable_pass / stable_fail / unstable; unstable goes to a human).

Everything here was measured on the committed repo (cloned from GitHub) with no LLM calls. Reproduce with the
scripts named in each line. "Measured" = a number from the repo's own data/code; "Hypothesis" = not yet tested.

## 1. Repo state (measured)
- `main` @ `9f9e292`; 55 tests passed before this patch. Commit `9f9e292` changes data/docs only (audit results,
  17 cache files, context doc); its message ("Refactor code structure...") does not describe that.
- Frozen assets are tracked, not ignored; no `.env` tracked; no key-like strings in tracked text (grep, excluding cache).
- `D_compass.jsonl` in `results/run1` is a 0-byte file (aborted run against the Compass placeholder).
- `data/bench/audit.jsonl` held only 17 rows (all `simple`): the remains of the run that hit the rate limit. The
  complete 27-question audit is in `data/bench/v2_review_manifest.json`.

## 2. Benchmark validity (measured; manifest + questions.jsonl)
| | simple | multi_hop | temporal | chain | conflicting |
|---|---|---|---|---|---|
| accepted | 17 | 6 | 2 | 2 | 0 |
| pass support audit | 17/17 | **0/6** | 1/2 | 1/2 | - |

- Audit failures: `not_all_passages_needed` x7 (one passage suffices => not multi-hop), `answer_not_supported` x2,
  `different_quantity` x1. 8 of 27 questions fail; 6 of those are the entire multi-hop category.
- All 27 accepted questions come from **9 papers** (the whole test split); 10 come from one paper, 22/35 gold-paper
  slots from three papers. Question-level bootstrap CIs treat these as independent and are therefore too narrow.
- Oracle labels: v1 SIMPLE/MULTI/UNCERTAIN = 11/5/11; v2 = 18/7/2; they differ on 9 questions. v2 sends unretrievable
  questions to SIMPLE, so "SIMPLE" mixes "easy" with "hopeless".

## 3. Run 1 re-read on audit-clean questions (measured; no new calls)
| experiment | recall, all 27 | recall, 19 audit-clean |
|---|---|---|
| A vanilla | 0.52 | 0.61 |
| B static / K static k=10 | 0.63 / 0.65 | 0.71 / 0.71 |
| G always multi-hop | 0.72 | 0.82 |
| C LLM router | 0.70 | 0.82 |
| F always strongest | 0.76 | 0.82 |
| E oracle | 0.76 | 0.82 |
- The 19 clean questions are 17 simple + 1 chain + 1 temporal. On them C = E = F = G. The "C < F" gap on all 27 came
  from invalid multi-hop questions (their gold sets require a redundant second chunk).
- Decomposition raises recall even on SIMPLE questions (0.71 -> 0.82). Hypothesis: the gain is query breadth/rewriting,
  not multi-hop reasoning, which would mean the SIMPLE/MULTI_HOP labels do not describe what helps.
- Cost is the only place routing can win: C used 1.85 LLM calls/query, F 1.00, E 0.59.
- Net: Run 1 supports "A < B < decomposition" for retrieval on simple questions. It supports **no** routing claim and
  cannot test H4 (almost no non-simple valid questions).

## 4. Why generation yield is low (measured offline: `scripts/chain_funnel.py`, `scripts/pair_funnel.py`)
- Chain: 1136 abstract x same-paper-chunk pairs; **387 pass the current deterministic gate** (27/30 papers; 118 in the
  9 test papers). 730 are rejected by the section whitelist. 27% of passes come from Conclusion/Summary/Outlook sections
  (restatements of the abstract). Tightening to exclude those leaves 281 passes in 21/30 papers.
- Multi-hop, test split, ALL cross-paper chunk pairs (an upper bound on the candidate pool): 71,316 pairs, **65% pass**
  the deterministic gate; all 36 paper pairs have passing chunk pairs. The gate is not the bottleneck; it is close to
  non-discriminating.
- Cause (bug): `specific_scientific_signals` pattern `\b[A-Za-z]*\d+...` allows zero leading letters, so bare numbers
  ("1", "0", "2023") are "specific anchors". 67% of all anchors are bare numbers; the shared-anchor check passes 82% of
  pairs, 33.5% after requiring a letter. Even then the common anchors (CMB, LCDM, H0) are ubiquitous in a Hubble-tension
  corpus, so shared anchors prove topic overlap, not complementarity.
- Consequence (hypothesis, consistent with 0/6): the gate selects *redundant* passage pairs, the LLM writes a question
  answerable from either, and the support audit correctly rejects it. A bridge-style gate (shared RARE anchor, otherwise
  dissimilar passages) leaves 1.6% of pairs (1,169; 34/36 paper pairs): a far more targeted pool. Untested on survivors.
- The test split has 9 papers because the split is by paper (30%) over a 30-paper corpus. This caps diversity for every
  question type and is the structural limit, independent of any gate.

## 5. In this patch
Applied by default: LLM quota counters (`provider_calls`, `cache_misses`, `retry_attempts`, `rate_limit_errors`,
`connection_errors`, `rate_limit_stops`, `empty_completions`, provider token counters; legacy keys unchanged);
per-type funnel counters in the generator (`attempt:<type>`, `survived:<type>`, `pair:<type>:<reason>`); a per-run
summary (`<out>.runs.jsonl`) that is written even on abort and stops the whole run on a rate limit (exit code 2);
a resumable audit (`audit_questions.py`) with opt-in bounded `--wait-on-rate-limit`; offline funnel scripts; repo audit v2.
Not applied (needs owner approval, changes generation behavior): `optional/anchor_letter_fix.patch` (regex needs a letter).

## 6. Decisions for the owner
1. Expand the corpus (about 100 papers, separate index dir so Run 1 stays reproducible) vs keep 30 papers and scope claims.
2. Remove Conclusion/Summary/Outlook from chain evidence sections (measured effect in section 4).
3. Apply the anchor fix; then pilot a bridge-style gate and compare survivor rate per LLM call.
4. Re-run the audit-failing multi-hop questions: reject them or re-gold them; do not keep them as "multi_hop".
5. Use a cluster bootstrap by paper in `report.py` and report `n_papers` beside `n`.
6. Time-box benchmark repair; if valid non-simple questions stay under about 15 per type, drop H4 and report cost only.
