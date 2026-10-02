# AtlasRAG V1

Adaptive retrieval routing for scientific literature (astrophysics / arXiv) — a replication and extension.

> Compass implements and extends the adaptive retrieval-routing paradigm established by Adaptive-RAG for scientific literature, with emphasis on question-type-specific behavior and scientific evidence structure.

**Research question:** does adaptive retrieval routing give consistent benefits for scientific-literature QA, or are its gains concentrated in particular question types and evidence structures? Full spec in `docs/`.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # add GROQ_API_KEY (free, no card)
make check                                             # imports + keys; `python scripts/check_env.py --ping` tests the LLM
make test                                              # 22 offline tests, no keys needed
make fetch                                             # arXiv metadata + PDFs (polite: 3s delay)
make index                                             # parse -> chunk -> embed -> index
make serve                                             # http://localhost:8000/docs
```

Docker: `cp .env.example .env && docker compose up --build`

## Week 1 checklist
- [ ] Accounts: Groq, W&B, Hugging Face, Kaggle; claim GitHub Student Pack
- [ ] `make check` all green
- [ ] **Pick the subtopic** in `configs/default.yaml` (`corpus.keywords`). It must have papers that disagree.
- [ ] `make fetch` (start with `--max-papers 30` to sanity check)
- [ ] `make index`, then spot-read `data/processed/chunks.jsonl`: are sections sane? Fix the parser before scaling.
- [ ] `POST /ask` with routers `vanilla` and `static` on 10 hand-written questions
- [ ] Push to GitHub

## Week 2: benchmark (built, tested offline)
See `docs/WEEK2_GUIDE.md`. Pipeline: `gen_questions` -> `review_questions` (human) -> `label_oracle` -> `run_experiment` -> `report`.

## How experiments map to code
One pipeline (`pipeline.py`). The router returns a strategy label; `configs/default.yaml -> strategies` defines what runs.

| Exp | Router | Where |
|---|---|---|
| A vanilla | `FixedRouter("VANILLA")` | working |
| B static | `FixedRouter("STATIC")` | working |
| C LLM router | `LLMRouter` | working |
| D Compass | `CompassRouter` | Week 3 (`HeuristicRouter` is a dev stand-in, not a baseline) |
| E oracle | `OracleRouter(gold)` | needs Week 2 gold labels |

`EscalatingRouter(compass, llm_router, threshold)` implements the H3 escalation. Sweep the threshold; don't fix it.

## Rules that keep the study honest
- Every experiment uses the same pipeline; only the router changes.
- Run every comparison twice (change `llm.cache_namespace` for the rerun) and check rankings hold.
- Measure latency on uncached runs only. LLM-call and token counts are cache-independent.
- Compass never sees the answering LLM's context.
- Never state results before running them.

## Free-tier budget (plan for this)
Free-tier LLM access changes often. Groq's llama-3.x models became Enterprise-only; the self-serve models are now `openai/gpt-oss-20b` / `openai/gpt-oss-120b` (reasoning models). Run `python scripts/list_models.py` to see what YOUR key can call, and check your per-model limits at console.groq.com/settings/limits (requests/min and tokens/day differ per model). One answered question costs roughly 2-4K tokens, so full A-E runs plus reruns can span days: keep the benchmark to ~100-150 questions at first and rely on the LLM cache. Reasoning models also spend completion tokens thinking; `llm.reasoning_effort: low` and `llm.token_headroom` in the config control that.

## Layout
```
configs/default.yaml     all knobs (corpus, chunking, models, strategies, thresholds)
src/atlasrag/ingest/     arXiv fetch, PDF parse, chunking
src/atlasrag/retrieval/  embedder, numpy+BM25 index, RRF fusion, reranker
src/atlasrag/routers/    fixed, heuristic, llm, oracle, compass (stub), escalating
src/atlasrag/pipeline.py shared pipeline for A-E
src/atlasrag/bench/      question schema, generation, oracle, runner, stratified report
src/atlasrag/api/        FastAPI service
scripts/                 fetch_arxiv, build_index, check_env
tests/                   offline tests (fake LLM/embedder)
docs/                    project spec (MD + HTML)
```

## Known limitations (Week 1)
- PDF parsing is heuristic; two-column order and equations/tables are imperfect. Upgrade path: parse arXiv LaTeX source.
- Dense index is a numpy matrix (fine to ~10^5 chunks).
