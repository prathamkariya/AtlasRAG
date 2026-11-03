### Verdict

The engineering is better than most student projects: 165 tests pass, ruff is clean, there are no secrets in git history, writes are atomic, and the split is paper-level with cluster bootstraps. The headline scientific claims are not solid, though, and several are contradicted by your own committed data. In an interview, the oracle and “frozen” claims are where you’d get hurt.

### Critical: the results don’t support what the README says

1. **E_oracle can’t be reproduced and isn’t an upper bound.**
   - All 64 questions in the committed file have `gold_route = None`. `run_experiment.py --exp E` filters on that field, so it would exit with “no accepted questions”.
   - The recorded E routes (UNCERTAIN 28, SIMPLE 24, MULTI_HOP 12) are old v1-style labels. They disagree with the committed `gold_route_v2` on 25 of 64 questions.
   - The oracle ladder is SIMPLE, MULTI_HOP, UNCERTAIN. It excludes STATIC and STATIC_K10, so it isn’t a ceiling. B_static beats the best ladder strategy on 4 questions.
   - The per-question best across the six runs I compared (A, B, C, E, F, G) averages 0.75 against B’s 0.69, a headroom of about 0.06, not 0.02.
   - “Within 2% of the oracle” is a point estimate. The CI on E−B runs up to +0.08.
2. **The benchmark isn’t frozen.** The run metadata records a questions hash of `58ebacd6a9e8`, but the committed file hashes to `b0144a062d1e`. The benchmark manifest is stamped 2026-10-26, two days after the results.
3. **Your router narrative is backwards.**
   - The report says the LLM router “under-routes multi-hop questions to SIMPLE” and picks MULTI_HOP only 4% of the time.
   - In the data, C sent 23 of 23 multi_hop questions to MULTI_HOP. SIMPLE was chosen 10 times, all on simple questions. UNCERTAIN was chosen 0 times.
   - The “19% route accuracy” is measured against labels where unretrievable questions are tagged UNCERTAIN, which no router can predict.
4. **C’s deficit is a strategy-table artifact.**
   - Those 10 SIMPLE routes drop from recall 1.0 under B to 0.5, which accounts for about 0.078 of the 0.10 gap.
   - That is because `SIMPLE` is the A_vanilla strategy: dense-only, no rerank, k=5. The router isn’t failing; it’s being handed a deliberately weak option.
   - The 54 MULTI_HOP routes produce exactly G’s results (0.60 vs B’s 0.63 on those questions).
5. **The benchmark labels are weak.**
   - 27 of 64 questions are “insufficient”: no strategy retrieves all the gold, including 20 of 23 multi_hop.
   - `multi_hop-81cd3cae` literally says “the first passage… the second passage”.
   - In `multi_hop-50549cd8`, one gold chunk is the intro of an unrelated “Guide for the Hubble Tension” paper.
   - In `multi_hop-c593c727`, the only human-reviewed question, B retrieved chunk `::20`, which arguably answers it better than the gold `::23`.
   - 63 of 64 questions are only LLM-reviewed, with the generator and judge from the same model family, so “high-quality” and “curated” are overclaims.
   - Simple questions share about 68% of their tokens with the gold chunk and saturate at 0.97 for every non-vanilla strategy. All the discriminating signal comes from about 34 questions, and some of those have bad gold.
6. **The replication check is vacuous.** `final_v3_rerun` contains only B_static, which has 0 LLM calls and is deterministic. A “ranking stable” check over one item proves nothing. The runs that could drift (C, F, G) weren’t rerun.
7. **The latency claim isn’t measurable.**
   - F and G have identical cached decompositions on 64 of 64 questions, yet their medians are 4.35s and 9.14s.
   - F’s simple questions take 8.65s against 4.06s for multi_hop on the same code path.
   - Per-query maxima reach 2,024s for C, 450s for F and 320s for G.
   - The numbers also include your own 2.1s pacing sleeps. Your report admits latency wasn’t isolated, but the README headline still says “&gt;2x lower latency”.
8. **The attribution has no ablation behind it.**
   - A→B changes three things at once: BM25, the reranker, and k going from 5 to 8.
   - “Dense fails on exact numerics, BM25 fixes it” is untested.
   - Your tokenizer `\w+` splits “73.04” into “73” and “04”, which undercuts the exact-decimal story anyway.
   - The scope is also overstated: one narrow-topic corpus of 4k chunks is not “scientific literature”.

### Engineering issues

- **API:** There’s no `max_length` on `question` and no auth. The OpenAI client has no timeout (default is 10 minutes) while a global lock is held, so one slow call blocks everyone.
- **Health check:** `/health` reports ready before the embedder and reranker have loaded. They load lazily, so the first request pays the model download.
- **LLM client:** Provider 5xx errors aren’t retried, only 429 and connection errors.
- **Retrieval:** Dense text includes title and section but BM25 sees only the chunk text. `_retrieve` with `rerank=False` and several subqueries takes the first subquery’s candidates (a latent bug, since no current strategy does this).
- **Docker and CI:** The container runs as root with unpinned `>=` dependencies, including pytest and wandb. CI verifies the v2 manifest, not the frozen v3 one. Nothing ties results to the benchmark hash, and no test uses a real model.
- **Files:** About ten `open()` calls are never closed, which matters on Windows.

### Repo hygiene

There are 817 tracked files, including 603 LLM cache blobs and about 20 backup, `before_`, repair or unstable question files. A zero-byte “final” benchmark is also committed on purpose. `docs/` contains `PHASE_B_PROMPT.md`, and `.gitignore` lists agent-prompt files. The README and audit prose reads agent-written. If an interviewer asks why E can’t be rerun, “the agent handled it” won’t work.

### Fix order

1. Correct the README and report: the router narrative, “oracle upper bound”, “frozen”, and the latency headline.
2. Freeze the benchmark first. Make the runner refuse to run if the questions hash doesn’t match the manifest, and commit the labels E uses.
3. Redefine SIMPLE (for example, hybrid without rerank). Add ablations for dense-only k=8 and hybrid without rerank at k=8. Rerun everything, including C, F and G under a fresh cache namespace.
4. Human-review the 34 non-simple questions. Report recall separately on the sufficient subset and drop the “first passage” artifacts.
5. Drop latency, or measure it warm with no pacing and LLM time separated from local compute.
6. Harden the API: input limits, timeouts, real readiness. Prune the repo.

The negative result may well survive, since the strategies here have little complementarity. But right now the repo claims “decisive” and “scientific integrity” more than it has earned. Overselling will cost you more with JP Morgan than a modest claim you can defend line by line.

I can’t push to your repo, but I can write the hash-guard script and the corrected README/report text if you want them.