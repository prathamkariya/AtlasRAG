# AtlasRAG — WEEK 1 FOUNDATION
## Corpus, ingestion, chunking, retrieval, API, reproducibility, and baseline A/B

> **Companion to:** `AtlasRAG_MASTER_PROJECT_CONTEXT.md`
>
> **Repository:** https://github.com/prathamkariya/AtlasRAG
>
> **Purpose:** This document is the execution manual for the **foundation phase** of AtlasRAG.
>
> Give the Master Context file first, then this Week 1 file, to a new coding/research agent.
>
> This file is deliberately operational: it explains what Week 1 is supposed to establish, the exact workflow, commands, files, tests, failure handling, reproducibility requirements, and exit criteria.

---

# 1. What Week 1 Is Supposed to Accomplish

Week 1 establishes the **scientific RAG substrate** on which every later routing experiment depends.

The goal is not to build Compass.

The goal is not to optimize the final answering LLM.

The goal is to make the following path work and be inspectable:

```text
scientific papers
        ↓
metadata + PDFs
        ↓
PDF parsing
        ↓
section-aware chunking
        ↓
embeddings
        ↓
dense retrieval
        ↓
BM25 / lexical retrieval
        ↓
hybrid retrieval
        ↓
reranking
        ↓
answering LLM
        ↓
answer + citations
```

Then establish fixed retrieval baselines that later routing experiments can safely reuse.

The central Week 1 principle is:

> **Build one stable pipeline first. Add routing later without changing the underlying retrieval machinery.**

---

# 2. Week 1 in the Larger Research Program

The full project roughly moves through:

```text
WEEK 1
Foundation
   ↓
WEEK 2
Benchmark
   ↓
WEEK 3
Compass
   ↓
WEEK 4
Adaptive integration
   ↓
WEEK 5
Evaluation + analysis
```

However, the roadmap is not binding.

The actual evidence can change the sequence.

For example, the current project has already progressed beyond the original clean Week 1/Week 2 boundary because retrieval, benchmark generation, Oracle analysis, and deterministic pair selection have been developed together.

Therefore this document should be interpreted as:

```text
"what Week 1 establishes and how it should be understood"
```

rather than:

```text
"what must literally be executed before any Week 2 work can occur"
```

---

# 3. Research Context

AtlasRAG is a controlled study of adaptive retrieval routing for scientific literature.

Current broader question:

> Does adaptive retrieval routing provide consistent benefits for scientific-literature QA, or are its gains concentrated in particular question types and evidence structures?

Current sharper research objective:

> Can a lightweight learned router retain the evidence quality of a strong retrieval policy while reducing unnecessary retrieval/LLM cost, approaching an empirical cheapest-sufficient oracle?

Week 1 exists to make sure later results can actually answer those questions.

If retrieval quality is unstable, routing comparisons become difficult to interpret.

---

# 4. What Counts as "Foundation Complete"

Week 1 should establish all of the following:

```text
[1] environment works
[2] source papers can be acquired
[3] PDFs/metadata are reproducible
[4] section structure is parsed reasonably
[5] chunks are sensible
[6] embeddings can be generated
[7] dense retrieval works
[8] BM25/lexical retrieval works
[9] hybrid retrieval works
[10] reranking works
[11] API can call the pipeline
[12] baseline retrieval can be measured
[13] tests cover important deterministic behavior
[14] the exact configuration is recorded
[15] historical artifacts can be reproduced
```

The foundation does **not** need to be perfect.

It needs to be:

```text
working
inspectable
repeatable
and stable enough to serve as a baseline
```

---

# 5. Repository

Primary repository:

```text
https://github.com/prathamkariya/AtlasRAG
```

Expected source layout:

```text
AtlasRAG/
│
├── configs/
│   └── default.yaml
│
├── src/
│   └── atlasrag/
│       ├── __init__.py
│       ├── config.py
│       ├── llm.py
│       ├── pipeline.py
│       │
│       ├── ingest/
│       │
│       ├── retrieval/
│       │
│       ├── routers/
│       │
│       ├── bench/
│       │
│       └── api/
│
├── scripts/
│
├── tests/
│
├── docs/
│
├── data/
│
├── results/
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

Always inspect the current tree before assuming an exact path.

---

# 6. Week 1 Scope

Week 1 concerns:

```text
environment
configuration
corpus
ingestion
PDF parsing
section extraction
chunking
embedding
retrieval
reranking
pipeline wiring
API
baseline A/B retrieval
testing
reproducibility
```

Week 1 does NOT concern:

```text
Compass training
LoRA fine-tuning
Oracle-v2 research decisions
large benchmark regeneration
answer-level benchmark claims
final paper claims
Kubernetes-scale deployment
```

---

# 7. Source Domain

Current starting domain:

```text
Astrophysics / cosmology
```

Current corpus focus:

```text
Hubble tension
```

Current configured arXiv categories:

```yaml
categories:
  - astro-ph.CO
  - astro-ph.GA
```

Current configured date boundary:

```yaml
date_from: "2022-01-01"
```

Current configured maximum:

```yaml
max_papers: 150
```

The actual early working corpus was intentionally much smaller.

Current known successful build:

```text
30 papers
1239 chunks
0 failed
```

This is the important current baseline corpus state.

Do not silently replace the 30-paper corpus with a new larger corpus and then compare results as though nothing changed.

---

# 8. Why the Corpus Must Be Narrow First

A narrow corpus is intentional during the foundation stage.

A routing experiment needs meaningful questions involving:

```text
same scientific quantities
different papers
different conclusions
temporal revisions
cross-paper evidence
```

A broad random science corpus can make such pair relationships difficult to discover.

The current Hubble-tension focus provides likely shared entities such as:

```text
H0
DESI
BAO
CMB
S8
ΛCDM
EDE
Ωb h²
YHe
D/H
etc.
```

This does not mean these exact entities must dominate every question.

It means the corpus should contain enough scientifically related literature to support structured evidence relationships.

---

# 9. Corpus Acquisition

Primary source:

```text
arXiv API
```

Supporting metadata source when appropriate:

```text
Semantic Scholar API
```

Current project command:

```powershell
python scripts/fetch_arxiv.py --max-papers 30
```

The larger configuration may contain:

```yaml
request_delay_s: 3.0
```

This is intentionally polite for arXiv access.

Do not remove the delay merely to accelerate a local experiment.

---

# 10. Environment Setup

Windows PowerShell is the primary environment used in the existing work.

Activate the virtual environment.

Typical:

```powershell
.\.venv\Scripts\Activate.ps1
```

Set the source layout:

```powershell
$env:PYTHONPATH="src"
```

Confirm Python:

```powershell
python --version
```

The previously observed environment was Python 3.13.x.

Do not assume that the exact patch version is unchanged.

Record the actual value for each reproducibility run.

---

# 11. Environment Variables

Typical variables:

```text
GROQ_API_KEY
WANDB_API_KEY
HF_TOKEN
```

Potential `.env` structure:

```env
GROQ_API_KEY=
WANDB_API_KEY=
HF_TOKEN=
```

Never commit:

```text
.env
```

Never paste keys into chat.

Never commit credentials to GitHub.

---

# 12. Configuration Source of Truth

Main configuration:

```text
configs/default.yaml
```

The current foundation configuration includes:

```yaml
corpus:
  categories: ["astro-ph.CO", "astro-ph.GA"]
  keywords: ["hubble tension"]
  max_papers: 150
  date_from: "2022-01-01"
  raw_dir: data/raw
  processed_dir: data/processed
  request_delay_s: 3.0

chunking:
  max_chars: 1800
  overlap_chars: 200
  min_chars: 200

embedding:
  model: BAAI/bge-small-en-v1.5
  query_prefix: "Represent this sentence for searching relevant passages: "

reranker:
  model: cross-encoder/ms-marco-MiniLM-L-6-v2

retrieval:
  index_dir: data/index
  dense_k: 20
  bm25_k: 20
  rrf_k: 60
```

These values should be treated as the current baseline configuration, not as immutable forever.

Any future change must be recorded and evaluated as a new configuration/experiment.

---

# 13. Step 1 — Environment Verification

Run:

```powershell
$env:PYTHONPATH="src"
python scripts/check_env.py
```

For an LLM connectivity check:

```powershell
python scripts/check_env.py --ping
```

Expected conceptual checks:

```text
imports
environment variables
optional LLM connectivity
```

If the environment check fails:

```text
STOP
```

Do not continue into large corpus operations while the environment itself is uncertain.

---

# 14. Step 2 — Fetch Metadata and Papers

For the first sanity-check corpus:

```powershell
python scripts/fetch_arxiv.py --max-papers 30
```

Expected outputs are under the configured raw/processed locations.

After fetching, verify:

```powershell
Get-ChildItem data\raw
```

and inspect the metadata:

```powershell
Get-Content data\raw\metadata.jsonl | Select-Object -First 5
```

The exact metadata layout must be checked against the current script.

Do not assume all downloaded PDFs are valid.

---

# 15. Corpus Sanity Check

Before indexing:

Inspect:

```text
metadata
titles
publication dates
categories
abstracts
PDF presence
```

Look for:

```text
duplicate papers
missing PDFs
broken metadata
unexpected categories
papers unrelated to the target topic
```

Also manually open a few PDFs.

The purpose is not scientific peer review.

The purpose is to confirm that the retrieval corpus actually contains the intended literature.

---

# 16. Step 3 — Parse PDFs

The PDF parser is heuristic.

Known limitation:

```text
two-column reading order
equations
tables
special formatting
```

can be imperfect.

This matters because the entire benchmark later depends on chunk text.

A parser problem can become:

```text
bad chunk
   ↓
bad gold evidence
   ↓
bad benchmark question
   ↓
bad Oracle label
   ↓
misleading routing result
```

Therefore parsing quality is research infrastructure, not cosmetic formatting.

---

# 17. What to Inspect in Parsed Text

After parsing, inspect:

```text
paper title
abstract
introduction
methods
data
results
discussion
conclusion
tables
equations
```

Specifically verify:

### Abstracts

Are they recognizable as independent abstract chunks?

### Section boundaries

Are section names preserved?

### Tables

Are numerical relationships readable?

### Equations

Are variables and symbols not destroyed beyond usefulness?

### Multi-column pages

Is text in a sensible reading order?

### References/front matter

Are these separated from substantive evidence?

---

# 18. Step 4 — Chunking

Current configuration:

```yaml
max_chars: 1800
overlap_chars: 200
min_chars: 200
```

The goal of section-aware chunking is:

```text
preserve scientific context
+
avoid giant chunks
+
avoid tiny unusable fragments
```

A chunk should be large enough to contain a meaningful scientific statement but small enough for retrieval precision.

---

# 19. Chunking Rules

Current project logic is section-aware.

Front matter is excluded from the normal generation pool.

Evidence-bearing sections are recognized by patterns involving terms like:

```text
result
method
data
observ
analys
discussion
measure
conclusion
```

Do not assume that every section called "Discussion" is automatically useful evidence.

The label is a structural hint, not semantic truth.

---

# 20. Important Chunking Bug That Was Already Fixed

A genuine bug was found around undersized final chunks.

Current merge behavior:

```python
if len(chunks)>1 and len(chunks[-1])<min_chars:
    last=chunks.pop()
    chunks[-1]+="\n\n"+last
```

The chunking function must return the resulting list.

After the fix, the build succeeded:

```text
30 papers -> 1239 chunks (0 failed)
```

This fix is historical foundation work.

Do not change it simply to make code "cleaner."

Any future modification must have:

```text
reason
test
verification
```

---

# 21. Chunk Quality Checklist

For a sample of chunks, verify:

```text
[ ] chunk has a paper_id
[ ] chunk has a chunk_id
[ ] title is present when expected
[ ] section name is present
[ ] text is nonempty
[ ] text is scientifically coherent
[ ] equations are not catastrophically corrupted
[ ] tables are not reduced to meaningless fragments
[ ] chunk is not only boilerplate
[ ] chunk boundaries do not destroy every relevant statement
```

---

# 22. Step 5 — Build the Embeddings and Index

Current build command:

```powershell
python scripts/build_index.py
```

The index combines:

```text
chunk metadata
+
embedding vectors
+
lexical retrieval support
```

Current embedding baseline:

```text
BAAI/bge-small-en-v1.5
```

It was chosen because it is:

```text
small
CPU-friendly
easy to run locally
```

The fact that a larger model exists does not justify replacing the baseline.

---

# 23. Why the Embedding Model Should Stay Stable Initially

Embeddings influence:

```text
candidate retrieval
benchmark gold-recall
multi-hop neighbor selection
temporal candidate pairing
Oracle outcomes
```

Changing embeddings changes more than retrieval quality.

It can also change:

```text
which questions get generated
which candidates are paired
which questions become insufficient
```

Therefore:

> Do not casually change the embedding model during benchmark construction.

A future embedding experiment should be explicitly separated as an ablation.

---

# 24. Retrieval Architecture

Current retrieval components:

```text
Dense retrieval
+
BM25 lexical retrieval
        ↓
hybrid / RRF style combination
        ↓
reranker
        ↓
final evidence
```

Current retrieval settings:

```yaml
dense_k: 20
bm25_k: 20
rrf_k: 60
```

These are baseline values.

---

# 25. Dense Retrieval

Dense retrieval uses the embedding space.

Conceptually:

```text
question
   ↓
query embedding
   ↓
similarity against chunk embeddings
   ↓
top-k chunks
```

Main source to inspect:

```text
src/atlasrag/retrieval/index.py
```

Important questions:

```text
How is query embedding produced?
How are vectors normalized?
How is similarity calculated?
Is self-retrieval excluded where appropriate?
What k is used?
```

Do not change the algorithm without testing the effect.

---

# 26. BM25 / Lexical Retrieval

BM25 provides lexical matching.

This is important for scientific text because exact symbols and identifiers can matter:

```text
H0
DESI
BAO
Neff
YHe
ΛCDM
etc.
```

A dense retriever can retrieve semantically related text while missing an exact parameter or acronym.

That is one reason the project uses a hybrid strategy.

---

# 27. Hybrid Retrieval

The current static retrieval strategy is intended to be stronger than the vanilla baseline.

Conceptually:

```text
dense results
      +
BM25 results
      ↓
fusion
      ↓
reranking
      ↓
final top-k
```

This is Experiment B's foundation.

---

# 28. Reranking

Current reranker:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

Conceptually:

```text
query + candidate chunk
        ↓
cross-encoder score
        ↓
reranked candidates
```

A reranker is more expensive than raw embedding lookup, but the corpus is currently small enough for CPU use.

The purpose is to improve:

```text
relevance ordering
```

not to define the benchmark labels.

---

# 29. Experiment A — Vanilla Retrieval

Experiment A is the simplest retrieval baseline.

Conceptually:

```text
question
   ↓
dense retrieval only
   ↓
small final top-k
```

Current configuration:

```yaml
VANILLA:
  use_hybrid: false
  rerank: false
  decompose: false
  final_k: 5
```

Purpose:

```text
absolute retrieval floor
```

Later:

```text
B vs A
```

answers:

> How much does a stronger static retrieval stack help before routing enters the picture?

---

# 30. Experiment B — Static Retrieval

Experiment B is a stronger fixed retrieval policy.

Conceptually:

```text
question
   ↓
dense + BM25
   ↓
fusion
   ↓
rerank
   ↓
final evidence
```

Current configuration:

```yaml
STATIC:
  use_hybrid: true
  rerank: true
  decompose: false
  final_k: 8
```

Purpose:

```text
separate retrieval quality from routing
```

This is a foundational comparison.

---

# 31. Why A and B Must Be Kept

Without A:

```text
you cannot show what better retrieval itself contributes
```

Without B:

```text
you cannot tell whether routing improves on a strong fixed retrieval policy
```

The later Oracle comparison also depends heavily on this ladder.

---

# 32. Step 6 — Core Pipeline

Main file:

```text
src/atlasrag/pipeline.py
```

This should provide a shared execution path.

Conceptual structure:

```text
question
    ↓
router
    ↓
strategy
    ↓
retrieve
    ↓
rerank
    ↓
answer
```

The router should be swappable.

That means A/B/C/D/E can share the same pipeline while changing who chooses the strategy.

---

# 33. Shared-Pipeline Rule

This is one of the most important experimental rules in the entire project.

Bad design:

```text
A uses one pipeline
B uses a different pipeline
C uses a different implementation
D uses another framework
```

because then differences are confounded.

Preferred:

```text
same pipeline
same corpus
same retriever implementations
same answering model
same evaluation
different routing decision
```

The later router comparison becomes much more defensible.

---

# 34. Answer Generation

Current answering LLM:

```text
openai/gpt-oss-20b
```

through:

```text
https://api.groq.com/openai/v1
```

Current reasoning configuration:

```yaml
reasoning_effort: low
token_headroom: 400
```

The answer generator belongs downstream of retrieval.

Do not use answer quality to conceal retrieval failures.

---

# 35. LLM Caching

Current LLM caching is stored under:

```text
data/llm_cache/
```

and namespaced by:

```yaml
cache_namespace: default
```

The cache exists to reduce repeated provider usage during development.

Research rule:

```text
LLM logical call count
```

must be distinguished from:

```text
provider API calls
```

because a cached call may involve:

```text
1 logical call
0 provider calls
```

---

# 36. Rate-Limit Handling

Current provider rate limits have affected generation pilots.

The intended behavior is:

```text
provider 429
   ↓
bounded retry
   ↓
retry exhausted
   ↓
LLMRateLimitExceeded
   ↓
stop cleanly
```

Current retry configuration:

```yaml
max_retries: 2
retry_base_seconds: 1.0
retry_max_seconds: 4.0
```

This gives at most:

```text
3 total attempts
```

Do not convert this into an unbounded retry loop.

---

# 37. Why This Matters for Week 1

Rate-limit behavior is not just a convenience issue.

A hanging run can cause:

```text
partial experiment
unknown resource usage
ambiguous completion
```

A clean stop provides:

```text
known failure mode
resumability
reproducibility
```

---

# 38. Step 7 — FastAPI

The API entry point is under:

```text
src/atlasrag/api/
```

The development server command is:

```powershell
$env:PYTHONPATH="src"
python -m uvicorn atlasrag.api.main:app --reload --port 8000
```

Expected development URL:

```text
http://localhost:8000/docs
```

The API should remain thin.

It should call the same underlying pipeline used by experiments.

---

# 39. Why the API Exists

The API is not the research contribution.

It is infrastructure.

It allows:

```text
local testing
frontend integration
demo use
repeatable requests
future deployment
```

Do not turn API-layer complexity into the project itself.

---

# 40. API Sanity Test

After starting the server:

```text
http://localhost:8000/docs
```

Inspect the endpoints.

Test with a simple scientific query.

Example conceptual query:

```text
What is the reported value of H0 in this paper?
```

The exact request schema must be read from the current FastAPI implementation.

Do not guess an endpoint payload.

---

# 41. Baseline Retrieval-Only Evaluation

For retrieval research, retrieval-only experiments are deliberately useful.

Run:

```powershell
python scripts/run_experiment.py --group run1 --exp A --retrieval-only
python scripts/run_experiment.py --group run1 --exp B --retrieval-only
```

Later, Oracle and other routers can be compared using the same benchmark and retrieval-only structure.

Why retrieval-only?

Because early on we need to isolate:

```text
evidence retrieval
```

from:

```text
answer-generation quality
```

---

# 42. First Baseline Outputs

Current historical result files include:

```text
results/run1/A_vanilla.jsonl
results/run1/B_static.jsonl
results/run1/C_llm_router.jsonl
results/run1/E_oracle.jsonl
```

Run 1 is historical and should not be overwritten.

If rerunning after changes:

```text
use a new experiment group
```

for example:

```text
run2
run3
```

---

# 43. Baseline Metrics

Core retrieval metric:

```text
evidence recall
```

Also useful:

```text
paper recall
latency p50
latency p95
LLM calls/query
prompt tokens
completion tokens
total tokens
```

Later answer-level work may add:

```text
correctness
relevance
faithfulness
citation support
```

Do not claim answer-quality improvement from retrieval-only metrics.

---

# 44. Current Historical Baseline Numbers

Run 1 reported approximately:

```text
A Vanilla       0.52 evidence recall
B Static        0.63
C LLM Router    0.70
E Oracle        0.76
F Always Strong 0.76
G Multi-Hop     0.72
K Static K10    0.65
```

Important:

These are historical measurements.

Do not recalculate or overwrite the stored values just because the code later changes.

---

# 45. What A/B Establishes Scientifically

The first major question is:

```text
Does a stronger retrieval stack improve evidence coverage?
```

That is:

```text
B vs A
```

The result provides the foundation for later routing research.

If B does not improve much:

```text
the retrieval substrate itself may already be near its useful ceiling
```

If B improves significantly:

```text
retrieval policy is an important variable
```

Both outcomes are informative.

---

# 46. Do Not Optimize A/B Until the Measurement Works

Do not immediately start sweeping:

```text
embedding models
chunk sizes
rerankers
top-k values
BM25 parameters
```

The first goal is a coherent baseline.

A giant optimization sweep creates multiple problems:

```text
reproducibility burden
multiple comparisons
benchmark contamination risk
unclear baseline selection
```

Stability comes before optimization.

---

# 47. Testing Strategy

Run:

```powershell
$env:PYTHONPATH="src"
python -m pytest -q
```

The exact current test count may change.

The required outcome is:

```text
all tests pass
```

Do not treat old test counts as permanent.

---

# 48. What Tests Should Cover in the Foundation

At minimum, test:

```text
configuration loading
chunking behavior
undersized final chunk handling
index dimensions
dense retrieval
BM25 retrieval
fusion behavior
strategy configuration
router output contracts
LLM retry behavior
cache behavior
API import/startup
benchmark schema
```

The tests should prefer fake embeddings/fake LLMs where possible.

Do not make the default unit test suite dependent on paid or rate-limited network calls.

---

# 49. Offline vs Online Tests

Offline tests:

```text
unit logic
parsing
chunking
retrieval mathematics
router behavior
schema
benchmark validation
```

Online/integration checks:

```text
arXiv fetching
real model API
real LLM provider
real external services
```

Keep them separate.

This allows:

```text
pytest
```

to remain fast and reproducible.

---

# 50. Debugging Order

When a foundation test fails, debug from the bottom upward:

```text
environment
   ↓
configuration
   ↓
input data
   ↓
parser
   ↓
chunker
   ↓
index
   ↓
retriever
   ↓
reranker
   ↓
pipeline
   ↓
API
```

Do not immediately blame the LLM.

---

# 51. Common Foundation Failure Modes

## Missing API key

Symptom:

```text
GROQ_API_KEY is not set
```

Fix:

```text
.env
```

or correct environment setup.

---

## Incorrect PYTHONPATH

Symptom:

```text
ModuleNotFoundError: atlasrag
```

Fix:

```powershell
$env:PYTHONPATH="src"
```

---

## Bad PDF parsing

Symptom:

```text
garbled sections
reordered text
empty chunks
```

Fix:

```text
inspect parser input/output
```

before changing retrieval.

---

## Index mismatch

Symptom:

```text
embedding row count != chunk count
```

Fix:

```text
rebuild index
```

after verifying source artifacts.

---

## Broken chunking

Symptom:

```text
tiny useless final chunks
missing return
unexpected chunk count
```

Inspect the chunking implementation and regression tests.

---

## Retrieval returns obvious junk

Check:

```text
query embedding
dense similarity
BM25 query
fusion
reranking
```

in that order.

---

## API starts but returns incorrect results

Trace:

```text
request
→ pipeline
→ router
→ strategy
→ retrieval
→ answer
```

Do not debug the frontend first.

---

# 52. Reproducibility Metadata

For every foundation snapshot, record:

```text
date
git commit
branch
Python version
OS
corpus query
paper count
chunk count
embedding model
reranker model
retrieval k values
LLM model
LLM configuration
cache namespace
```

A future result should be reconstructable from this.

---

# 53. Recommended Run Manifest

A future run manifest should conceptually look like:

```json
{
  "git_commit": "...",
  "python_version": "...",
  "corpus": {
    "papers": 30,
    "chunks": 1239
  },
  "embedding_model": "BAAI/bge-small-en-v1.5",
  "reranker": "cross-encoder/ms-marco-MiniLM-L-6-v2",
  "llm_model": "openai/gpt-oss-20b",
  "cache_namespace": "run1",
  "experiments": ["A", "B"]
}
```

Do not invent values.

Generate them from the actual environment.

---

# 54. Docker

The project contains Docker infrastructure.

Foundation principle:

```text
Docker is for reproducibility
```

not:

```text
Docker is part of the research variable
```

If Docker is used during a foundation verification, make sure the container uses the same:

```text
source
configuration
models
index
```

as the local pipeline.

Do not create a separate hidden implementation inside Docker.

---

# 55. Weights & Biases

W&B is intended as experiment tracking infrastructure.

Record:

```text
experiment id
git commit
configuration
metrics
timing
token counts
```

The tracking layer should not change retrieval behavior.

If tracking is unavailable, the experiment can still be locally logged, but the eventual paper-facing workflow should preserve run metadata.

---

# 56. Foundation Data Directories

Typical directory roles:

```text
data/raw/
    source metadata + downloaded source data

data/processed/
    parsed/processed text/chunks

data/index/
    embeddings/index artifacts

data/bench/
    benchmark files

data/llm_cache/
    cached LLM calls

results/
    experiment results
```

Keep raw inputs separate from generated benchmark/evaluation artifacts.

---

# 57. Separation of Historical and Working Artifacts

Historical:

```text
results/run1/
data/bench/questions.jsonl
data/bench/questions_v1_frozen.jsonl
```

Working/new:

```text
data/bench/questions_v2.jsonl
new experiment groups
new pilots
new reports
```

Never confuse a working artifact with the historical baseline.

---

# 58. Foundation Exit Test

Before declaring the foundation stable, verify:

```text
[ ] fresh environment can import project
[ ] configuration loads
[ ] papers fetch
[ ] metadata exists
[ ] PDFs exist
[ ] parser produces sections
[ ] chunks look sensible
[ ] chunk count is recorded
[ ] embeddings build
[ ] index loads
[ ] dense retrieval works
[ ] BM25 works
[ ] hybrid retrieval works
[ ] reranking works
[ ] A runs
[ ] B runs
[ ] results are saved
[ ] tests pass
[ ] API starts
[ ] configuration is committed
[ ] secrets remain uncommitted
```

---

# 59. Current AtlasRAG Foundation State

As of the current project checkpoint:

```text
Environment        WORKING
LLM connectivity   WORKING
Ingestion          WORKING
Index              WORKING
30 papers          INDEXED
1239 chunks        INDEXED
FastAPI            WORKING
Embedding          BGE-small baseline
Reranker           MiniLM cross-encoder
A baseline         COMPLETE
B baseline         COMPLETE
```

So Week 1 is largely established.

The important task now is not to pretend Week 1 has not happened.

The important task is to preserve and understand the foundation so later agents do not accidentally rebuild or invalidate it.

---

# 60. Current Foundation Commit/Tree Verification Rule

Before any new agent changes foundation code:

```powershell
git status
git rev-parse HEAD
git log --oneline -5
```

Then inspect:

```text
configs/default.yaml
src/atlasrag/pipeline.py
src/atlasrag/ingest/
src/atlasrag/retrieval/
src/atlasrag/llm.py
src/atlasrag/api/
tests/
```

The GitHub repository is the authoritative shared implementation source:

```text
https://github.com/prathamkariya/AtlasRAG
```

Do not trust old chat snippets when the repository is available.

---

# 61. Foundation Change Policy

Any foundation change must answer:

```text
What exact problem are we solving?
Which file/function has the problem?
How do we know the problem is real?
What test reproduces it?
What is the smallest fix?
Could it change benchmark behavior?
Could it change historical comparability?
```

If the answer to these questions is unclear:

```text
do not make the change yet
```

---

# 62. What Must Stay Frozen During Foundation Work

Unless an explicitly approved experiment requires otherwise:

```text
data/bench/questions.jsonl
data/bench/questions_v1_frozen.jsonl
results/run1/
src/atlasrag/bench/oracle_v2.py
src/atlasrag/bench/experiments.py
```

Do not "clean up" these files.

Do not format them.

Do not regenerate them.

Do not change labels simply because they are inconvenient.

---

# 63. What Foundation Work Can Still Change

Reasonable foundation work can include:

```text
real parser bug fix
real chunking bug fix
retrieval implementation bug fix
index serialization bug fix
API correctness fix
test coverage
logging/instrumentation
bounded retry handling
configuration documentation
reproducibility tooling
```

But even safe engineering changes should be checked for experimental impact.

---

# 64. Scientific-Evidence Considerations Starting in Week 1

Scientific RAG is different from generic text QA.

The retrieval system must preserve:

```text
numbers
units
symbols
parameter names
equations
tables
section context
paper identity
publication date
```

A retrieval system can return a semantically related passage that is still scientifically unusable.

Example:

```text
H0 = 67
```

and:

```text
H0 = 73
```

are both highly relevant to "Hubble tension" but not interchangeable.

The foundation should therefore retain enough metadata for later evidence analysis.

---

# 65. Required Chunk Metadata

The current chunk records include fields such as:

```text
chunk_id
paper_id
title
section
text
```

The benchmark and retrieval layers depend on these identifiers.

Do not remove them for simplicity.

They are needed for:

```text
gold evidence
retrieval analysis
paper recall
temporal ordering
chain relationships
error analysis
citations
```

---

# 66. Why Paper IDs Matter

A question may require:

```text
paper A
+
paper B
```

Without reliable paper identity, later analysis cannot distinguish:

```text
same paper
vs
different paper
```

That breaks multi-hop and chain analysis.

Therefore `paper_id` is a first-class piece of the scientific data model.

---

# 67. Why Section Labels Matter

The later benchmark uses evidence structures such as:

```text
Abstract → Results
Abstract → Methods
Earlier paper → Later paper
```

Therefore:

```text
section
```

is not merely presentation metadata.

It becomes a semantic feature in benchmark construction and validation.

---

# 68. Why Publication Dates Matter

Temporal questions require:

```text
earlier paper
later paper
```

which requires trustworthy publication dates.

The current metadata has:

```text
published
```

and the benchmark code extracts the date for temporal ordering.

Bad date parsing can produce false temporal relationships.

Verify dates before trusting temporal benchmark generation.

---

# 69. Why Retrieval-Only Comes First

Retrieval-only evaluation gives:

```text
question
→ retrieved evidence
→ metric
```

without adding the answering LLM as another variable.

This makes it much easier to diagnose:

```text
retrieval failure
```

versus:

```text
answer-generation failure
```

This design principle carries directly into Week 2.

---

# 70. Week 1 and Benchmark Contamination

Foundation code can influence benchmark generation indirectly.

For example:

```text
embedding model
→ nearest neighbor
→ benchmark pair
→ generated question
```

Therefore if you change embeddings after benchmark generation, you may change:

```text
which candidates are selected
```

This is another reason to freeze a baseline before generating large benchmark sets.

---

# 71. Foundation Exit Artifacts

A mature Week 1 checkpoint should preserve:

```text
corpus metadata
parsed chunks
index artifacts
configuration
test output
Git commit
baseline A results
baseline B results
environment manifest
```

If these can be recreated, later experiments are much easier to trust.

---

# 72. Recommended Week 1 Agent Prompt

Use this exact prompt for a coding agent if it needs to audit the foundation:

```text
Inspect the current AtlasRAG repository:

https://github.com/prathamkariya/AtlasRAG

Treat the repository as the implementation source of truth.

Do not modify anything yet.

Audit the Week 1 foundation only:
- environment/configuration
- arXiv ingestion
- PDF parsing
- section extraction
- chunking
- embeddings
- dense retrieval
- BM25
- hybrid retrieval
- reranking
- shared pipeline
- FastAPI
- LLM caching/retries
- tests
- reproducibility

First report:
1. current commit/branch
2. actual current test count
3. current corpus/index assumptions
4. exact files/functions involved
5. any genuine remaining foundation bugs
6. whether fixing them could affect historical experiments
7. which files actually need changing
8. which files must remain untouched

Do not refactor for style.
Do not replace the embedding model.
Do not replace the LLM.
Do not modify benchmark v1 or results/run1.
Do not train Compass.
Wait before making changes if the issue is not clearly demonstrated by the code/tests.
```

---

# 73. Week 1 Handoff to Week 2

Once the foundation is stable:

```text
FOUNDATION
   ↓
corpus + parser + chunks + index
   ↓
A/B retrieval baselines
   ↓
WEEK 2 BENCHMARK
```

Week 2 then adds:

```text
human-reviewed questions
gold evidence
Oracle labels
stratified evaluation
retrieval-only comparisons
```

Do not build Compass from an unstable foundation.

---

# 74. Relationship to Week 2

Week 1 answers:

> Can we reliably represent and retrieve scientific evidence?

Week 2 answers:

> Can we build a trustworthy benchmark for measuring retrieval/routing behavior?

Week 3 answers:

> Can a lightweight model learn the routing decision?

Week 4 answers:

> Does integrating that router improve the end-to-end system?

Week 5 answers:

> Where does it help, by how much, and at what cost?

This separation is one of the main ways to keep the research interpretable.

---

# 75. Week 1 Final Checklist

```text
CORPUS
[ ] target scientific domain defined
[ ] arXiv query defined
[ ] corpus version recorded
[ ] paper count recorded

PARSING
[ ] PDFs parse
[ ] sections preserved
[ ] abstract extraction works
[ ] tables/equations are usable enough
[ ] obvious parsing defects inspected

CHUNKING
[ ] section-aware
[ ] max_chars recorded
[ ] overlap recorded
[ ] min_chars recorded
[ ] final small-chunk behavior tested
[ ] chunk count recorded

INDEX
[ ] embedding model recorded
[ ] embeddings build
[ ] index loads
[ ] dense retrieval works
[ ] BM25 works
[ ] hybrid retrieval works
[ ] reranker works

PIPELINE
[ ] shared pipeline exists
[ ] A works
[ ] B works
[ ] LLM call works
[ ] caching works
[ ] retries bounded

API
[ ] FastAPI starts
[ ] /docs opens
[ ] representative query works

TESTING
[ ] offline tests pass
[ ] network checks separated
[ ] regression tests cover known bugs

REPRODUCIBILITY
[ ] git commit recorded
[ ] config recorded
[ ] Python recorded
[ ] corpus count recorded
[ ] chunk count recorded
[ ] model versions recorded

SAFETY
[ ] secrets not committed
[ ] benchmark v1 untouched
[ ] run1 untouched
```

---

# 76. Week 1 Success Condition

Week 1 is successful when:

```text
a fresh engineer can clone the repository,
load the environment,
understand the corpus,
rebuild the index,
run the shared retrieval pipeline,
run A and B,
inspect their results,
run the tests,
and identify exactly which code produced each result.
```

That is the standard to aim for.

Not:

```text
"it runs on my machine."
```

---

# 77. Research References Used by the Foundation

The foundation depends on standard scientific-data and retrieval infrastructure.

Primary data source:

```text
arXiv API
https://info.arxiv.org/help/api/
```

Optional metadata:

```text
Semantic Scholar API
https://api.semanticscholar.org/
```

Later evaluation references:

```text
RAGAS
https://github.com/explodinggradients/ragas

ARES
https://github.com/stanford-futuredata/ARES
```

These are evaluation tools, not Week 1 research conclusions.

---

# 78. Final Week 1 Mental Model

Think of Week 1 as building the laboratory.

```text
papers
  ↓
scientific document representation
  ↓
retrieval machinery
  ↓
reproducible pipeline
  ↓
baseline measurement
```

Only once the laboratory is reliable does it make sense to ask:

```text
Can a router choose the right amount of retrieval?
```

That is the transition into Week 2 and beyond.

---

# 79. End of Week 1

**Project:** AtlasRAG  
**Repository:** https://github.com/prathamkariya/AtlasRAG

**Foundation status:** largely complete, with the current baseline consisting of approximately 30 indexed papers and 1239 chunks.

**Next major phase:** Week 2 benchmark construction, audit, Oracle labeling, and controlled evaluation.

**Non-negotiable principle:** preserve historical experiments and make future changes controlled, testable, and reproducible.
