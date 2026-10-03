# AtlasRAG — MASTER PROJECT CONTEXT PACKET

> **Purpose:** This is the master context document for opening a new AI/chat/coding-agent session on AtlasRAG.
>
> Give this file to the new agent **before asking it to change anything**.
>
> The current GitHub repository is the source of truth for implementation:
>
> **https://github.com/prathamkariya/AtlasRAG**
>
> This document explains what AtlasRAG is, why it exists, what has already been built, what was tested, what was learned, what is frozen, what is currently broken/incomplete, what research questions remain, which papers inspired it, and how future work must proceed.

---

# 1. Project Identity

**Project name:** AtlasRAG

**Repository:** https://github.com/prathamkariya/AtlasRAG

**Domain:** Scientific-literature RAG, initially astrophysics / cosmology papers from arXiv.

**Author:** Pratham Kariya

**Current status:** Working research prototype / experimental system.

**Core idea:** Adaptive retrieval routing for scientific literature.

AtlasRAG is not being built merely as a normal chatbot. It is being developed as a controlled research experiment that asks whether a system can decide how much retrieval work a scientific question actually needs.

The system should eventually be able to distinguish, for example:

```text
Simple factual question
        ↓
cheap retrieval path

Complex multi-paper question
        ↓
multi-hop / decomposed retrieval path

Uncertain / difficult question
        ↓
stronger retrieval / escalation path
```

The central research interest is therefore the **quality–cost tradeoff created by adaptive retrieval routing**.

---

# 2. The Current Research Question

The current working formulation is:

> **Can a lightweight learned router retain the evidence quality of a strong retrieval policy while reducing unnecessary retrieval/LLM cost, approaching an empirical cheapest-sufficient oracle?**

The broader project framing is:

> **Does adaptive retrieval routing provide consistent benefits for scientific-literature QA, or are its gains concentrated in particular question types and evidence structures?**

This is deliberately narrower than the original idea.

Do not reduce the research question to:

> "Can we make a better RAG?"

That is not the experiment.

The experiment is about:

```text
question
   ↓
routing decision
   ↓
retrieval strategy
   ↓
evidence quality
   +
cost / latency
```

The router is valuable only if its decisions create a useful quality/efficiency tradeoff.

---

# 3. What Is Actually Novel

The project explicitly does **not** claim to invent adaptive retrieval routing.

Adaptive query-complexity routing is prior art.

The defensible contribution is the application and evaluation of the paradigm in a scientific-literature setting where evidence has structures such as:

```text
abstract → methods → results
paper A → paper B disagreement
earlier study → later study
tables / equations / numerical constraints
```

The current documentation frames the contribution around:

1. Applying adaptive routing to scientific literature.
2. A scientific-evidence failure taxonomy.
3. Stratified evaluation by question/evidence type.
4. Oracle-ceiling analysis showing how much routing headroom exists.

The required honest wording when describing Compass is:

> "Compass implements and extends the adaptive retrieval-routing paradigm established by Adaptive-RAG for scientific literature, with emphasis on question-type-specific behavior and scientific evidence structure."

Never say AtlasRAG invented adaptive routing.

Never present Compass as an invention of the basic routing mechanism.

---

# 4. Prior Art and Inspirations

These are the main research references that shape the project.

## 4.1 Adaptive-RAG

**Paper:** Soyeong Jeong et al., 2024  
**Title:** *Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity*

arXiv:
https://arxiv.org/abs/2403.14403

Code:
https://github.com/starsuzi/Adaptive-RAG

Why it matters:

Adaptive-RAG trains a smaller classifier to route questions among different retrieval/generation strategies based on predicted query complexity.

This is the closest conceptual prior art for Compass.

AtlasRAG is intentionally an extension/application rather than a claim of inventing this mechanism.

---

## 4.2 Self-RAG

**Paper:** Akari Asai et al.  
**Title:** *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection*

arXiv:
https://arxiv.org/abs/2310.11511

Why it matters:

Self-RAG makes retrieval decisions adaptive within generation and uses reflection signals to determine when retrieved information is useful.

It is relevant as a contrasting adaptive-retrieval design.

---

## 4.3 FLARE

**Paper:** Zhengbao Jiang et al.  
**Title:** *Active Retrieval Augmented Generation*

arXiv:
https://arxiv.org/abs/2305.06983

Code:
https://github.com/jzbjyb/FLARE

Why it matters:

FLARE uses predicted upcoming text and uncertainty-like signals to trigger retrieval during generation.

It establishes another family of adaptive retrieval decisions.

---

## 4.4 RouteLLM

**Paper:** Isaac Ong et al.  
**Title:** *RouteLLM: Learning to Route LLMs with Preference Data*

arXiv:
https://arxiv.org/abs/2406.18665

Code:
https://github.com/lm-sys/RouteLLM

Why it matters:

RouteLLM studies the cost/quality tradeoff of routing requests between stronger and weaker models.

The architectural target is different from AtlasRAG, but the cost-aware routing framing is directly useful.

---

## 4.5 RouterBench

**Paper:** Qitian Jason Hu et al.  
**Title:** *RouterBench: A Benchmark for Multi-LLM Routing System*

arXiv:
https://arxiv.org/abs/2403.12031

Code:
https://github.com/withmartian/routerbench

Why it matters:

Provides a broader evaluation framework for routing decisions and reinforces the idea that routing should be evaluated under a measurable quality/cost tradeoff.

---

## 4.6 Hybrid LLM

**Paper:** Dujian Ding et al.  
**Title:** *Hybrid LLM: Cost-Efficient and Quality-Aware Query Routing*

arXiv:
https://arxiv.org/abs/2404.14618

Why it matters:

The paper studies routing based on predicted quality gaps and explicitly frames routing as cost/quality optimization.

This is useful conceptual inspiration for future cost-aware extensions.

---

## 4.7 RAGRouter-Bench

**Paper:** Ziqi Wang et al., 2026  
**Title:** *RAGRouter-Bench: A Dataset and Benchmark for Adaptive RAG Routing*

arXiv:
https://arxiv.org/abs/2602.00296

GitHub:
https://github.com/ziqiwang0908/RAGRouter-Bench

Why it matters:

This is especially important because it is directly about adaptive RAG routing.

It evaluates different RAG paradigms under query–corpus compatibility and effectiveness/efficiency considerations.

AtlasRAG should treat this as a key modern related benchmark.

Crucial implication:

> Basic "adaptive RAG routing" is an active research area, so AtlasRAG's novelty must come from the scientific-literature setting, evidence structure, benchmark design, and analysis — not merely from adding a router.

---

## 4.8 RAGAS

Paper:
https://arxiv.org/abs/2309.15217

Code:
https://github.com/explodinggradients/ragas

Why it matters:

Relevant for later answer-level evaluation, especially context relevance, faithfulness, and answer quality.

RAGAS is intentionally not the main basis of the early retrieval-only experiment because retrieval quality needs to be isolated first.

---

## 4.9 ARES

Paper:
https://arxiv.org/abs/2311.09476

Code:
https://github.com/stanford-futuredata/ARES

Why it matters:

ARES provides another approach to automated RAG evaluation using learned judges for context relevance, faithfulness, and answer relevance.

Again, it is more useful later when answer-level evaluation is introduced.

---

## 4.10 LoRA

Paper:
https://arxiv.org/abs/2106.09685

Why it matters:

Compass is intended to be trained using parameter-efficient adaptation rather than full model fine-tuning.

---

## 4.11 QLoRA

Paper:
https://arxiv.org/abs/2305.14314

Why it matters:

Potentially useful if the selected Compass base requires memory reduction during training.

---

# 5. Conceptual Architecture

The intended architecture is:

```text
                 SCIENTIFIC QUESTION
                         │
                         ▼
                ┌─────────────────┐
                │      ROUTER     │
                │  swapped per    │
                │   experiment    │
                └────────┬────────┘
                         │
           ┌─────────────┼──────────────┐
           ▼             ▼              ▼
        SIMPLE        MULTI_HOP      UNCERTAIN
           │             │              │
           ▼             ▼              ▼
      cheap/simple   decomposition    strongest
       retrieval      + hybrid        retrieval /
                                      escalation
           └─────────────┼──────────────┘
                         ▼
                 retrieval strategy
                         │
                         ▼
                    reranker
                         │
                         ▼
                   answering LLM
                         │
                         ▼
                  answer + citations
                         │
                         ▼
                    evaluation
```

The crucial experimental rule:

> **Every experiment must share the same pipeline structure except for the routing decision.**

Otherwise the comparison becomes confounded.

---

# 6. Current Retrieval Strategy Ladder

The current strategy labels are approximately:

```text
SIMPLE
MULTI_HOP
UNCERTAIN
```

The configured strategies include:

```text
VANILLA
STATIC
SIMPLE
MULTI_HOP
UNCERTAIN
STATIC_K10
```

Current configuration:

```yaml
VANILLA:
  use_hybrid: false
  rerank: false
  decompose: false
  final_k: 5

STATIC:
  use_hybrid: true
  rerank: true
  decompose: false
  final_k: 8

SIMPLE:
  use_hybrid: false
  rerank: false
  decompose: false
  final_k: 5

MULTI_HOP:
  use_hybrid: true
  rerank: true
  decompose: true
  final_k: 8

UNCERTAIN:
  use_hybrid: true
  rerank: true
  decompose: true
  final_k: 10

STATIC_K10:
  use_hybrid: true
  rerank: true
  decompose: false
  final_k: 10
```

Do not change these casually. Any retrieval-strategy change can alter the historical experimental comparison.

---

# 7. Experiments

The original conceptual experiment set is:

```text
A = Vanilla RAG
B = Strong static RAG
C = LLM router
D = Compass router
E = Oracle
```

Current code also contains:

```text
E2 = Oracle v2
F  = always strongest / UNCERTAIN
G  = always MULTI_HOP
K  = STATIC_K10
H  = heuristic development stand-in
```

These later controls were introduced to make the evidence cleaner.

---

# 8. Experiment Definitions

## A — Vanilla

No adaptive routing.

Simple dense retrieval.

Purpose:

```text
establish a basic floor
```

---

## B — Static

Always use the stronger static retrieval policy.

Purpose:

```text
separate retrieval quality from routing
```

This is extremely important.

If B already reaches the same evidence quality as the adaptive systems, routing may provide little additional value.

---

## C — LLM Router

An LLM decides the retrieval strategy.

Purpose:

```text
measure what question-dependent routing can achieve
when routing itself is expensive
```

Current answering/routing LLM:

```text
openai/gpt-oss-20b
```

served through Groq's OpenAI-compatible API.

Important:

C uses question semantics for routing.

It does not represent the empirical Oracle's decision process.

---

## D — Compass

The planned learned local router.

Current status:

```text
PLACEHOLDER / NOT TRAINED
```

Intended V1 job:

```text
question
  ↓
small frozen base model
  ↓
LoRA adapter
  ↓
classification head
  ↓
SIMPLE / MULTI_HOP / UNCERTAIN
```

Compass should not consume:

- retrieved answer context
- gold chunks
- reference answers
- outputs from the answering LLM

because doing so would create leakage and undermine the claim that the router is cheap and question-driven.

---

## E — Oracle v1

Uses gold evidence and retrieval results to estimate the ideal strategy selection.

The original concept:

```text
cheapest strategy whose retrieval covers all gold evidence
```

This represents the ceiling available to routing under the chosen retrieval ladder.

It is not a real deployable router.

It is a diagnostic / upper-bound tool.

---

## E2 — Oracle v2

Oracle v2 was introduced because v1 had a significant conceptual problem.

Oracle v2:

1. Runs the retrieval ladders.
2. Records all ladder recalls.
3. Finds the best achievable recall.
4. Picks the cheapest strategy within epsilon of that best recall.
5. Tracks whether the best achievable recall is actually full recall.

Conceptually:

```text
recs = {
    SIMPLE: ...
    MULTI_HOP: ...
    UNCERTAIN: ...
}

best = max(recs.values())

gold_route_v2 =
    cheapest route with recall >= best - epsilon

oracle_sufficient =
    best >= 1.0
```

This separates:

```text
"what is the cheapest useful policy?"
```

from:

```text
"can the current retriever recover the gold evidence at all?"
```

That distinction is important.

---

# 9. Why Oracle v2 Was Needed

Original v1 labels had an overloaded `UNCERTAIN` category.

Nine of the 27 accepted test questions were not fully covered by any retrieval strategy.

If all such cases simply become:

```text
UNCERTAIN
```

then Compass can learn:

> "When the retrieval system is incapable of finding the evidence, spend the most retrieval effort."

That is not necessarily useful.

Oracle v2 instead exposes retrieval insufficiency as a separate property.

Training can later compare:

```text
v2
```

versus:

```text
v2_sufficient
```

where insufficient questions are excluded from router training.

---

# 10. Current Corpus

Known successful build:

```text
30 papers
1239 chunks
0 failures
```

Domain:

```text
Astrophysics / cosmology
```

Metadata includes:

```text
id
title
authors
published
categories
abstract
pdf_url
pdf_path
```

Current embedding model:

```text
BAAI/bge-small-en-v1.5
```

Current reranker:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The current index is a NumPy matrix plus BM25-style lexical retrieval.

Do not replace the embedding model just because a larger/newer embedding model exists.

First establish whether embeddings are actually the bottleneck.

---

# 11. Important Parser / Chunking Fix Already Made

A real chunking bug was fixed.

The final merge logic in `chunk_section()` handles a final undersized chunk:

```python
if len(chunks)>1 and len(chunks[-1])<min_chars:
    last=chunks.pop()
    chunks[-1]+="\n\n"+last
```

The function returns the final chunks.

The index build after this fix succeeded:

```text
30 papers -> 1239 chunks (0 failed)
```

Do not touch this unless a test or new evidence identifies a regression.

---

# 12. Current LLM / Provider Architecture

AtlasRAG runtime:

```text
Groq
  ↓
OpenAI-compatible API
  ↓
openai/gpt-oss-20b
```

Config:

```yaml
llm:
  base_url: https://api.groq.com/openai/v1
  api_key_env: GROQ_API_KEY
  model: openai/gpt-oss-20b
  reasoning_effort: low
  token_headroom: 400
  max_retries: 2
  retry_base_seconds: 1.0
  retry_max_seconds: 4.0
  cache_dir: data/llm_cache
  cache_namespace: default
```

The OpenAI SDK's own retries are disabled:

```python
OpenAI(...,max_retries=0)
```

AtlasRAG owns the retry loop.

---

# 13. Bounded 429 Handling

Current retry mechanism:

```text
RateLimitError
APIConnectionError
        ↓
bounded retries
        ↓
1s
2s
...
        ↓
LLMRateLimitExceeded
```

With:

```text
max_retries = 2
```

there are at most:

```text
3 total attempts
```

The process must not hang indefinitely on provider throttling.

This is particularly important because free-tier generation runs caused Groq 429s during benchmark generation.

The correct behavior is:

```text
rate limit
   ↓
bounded retry
   ↓
if still unavailable
   ↓
stop cleanly
   ↓
preserve partial output
```

Do not add an unbounded retry loop.

---

# 14. Important Distinction: Continue/OpenRouter vs AtlasRAG

The user also has a separate VS Code coding-assistant workflow:

```text
VS Code
  ↓
Continue
  ↓
OpenRouter free models
```

This is for coding assistance.

It is separate from AtlasRAG runtime:

```text
AtlasRAG
  ↓
Groq
  ↓
openai/gpt-oss-20b
```

Do not alter AtlasRAG's runtime LLM just because Continue uses OpenRouter.

---

# 15. Benchmark Construction

The benchmark has five intended question/evidence types:

```text
1. SIMPLE
2. MULTI_HOP
3. CONFLICTING
4. TEMPORAL
5. CHAIN
```

Definitions:

### SIMPLE

One passage should contain enough evidence.

### MULTI_HOP

Requires evidence from multiple papers/passages.

### CONFLICTING

Two papers must genuinely disagree or be in tension about the same quantity/claim.

### TEMPORAL

An earlier and later paper must address the same quantity/claim and provide evidence of a meaningful update/change.

### CHAIN

Abstract → later section in the same paper.

The later section must provide substantive evidence/method/result supporting a claim from the abstract.

---

# 16. Benchmark Generation History

Initial generation:

```text
30 simple candidates
30 multi-hop candidates
1 conflicting candidate
17 temporal candidates
16 chain candidates
```

Total:

```text
94 candidates
```

After human review:

```text
27 accepted
67 rejected
```

Original v1 Oracle labels:

```text
11 SIMPLE
5 MULTI_HOP
11 UNCERTAIN
```

Oracle v2 later reported:

```text
18 SIMPLE
7 MULTI_HOP
2 UNCERTAIN
9 retrieval-insufficient
```

This is a major reason Compass training is not yet appropriate.

---

# 17. Human Review Is Part of the Benchmark

A generated question is not automatically benchmark truth.

The workflow is:

```text
LLM generation
      ↓
automatic structural/support checks
      ↓
candidate
      ↓
human review
      ↓
accepted benchmark question
```

The human reviewer should reject questions that:

- echo distinctive source wording
- are answerable without the evidence
- are ambiguous
- ask more than one passage when marked SIMPLE
- only need one passage when marked MULTI_HOP
- compare unrelated quantities
- call different quantities "conflicting"
- compare unrelated temporal claims
- make unsupported causal/evaluative claims
- make chain questions answerable from the abstract alone

This review is not optional if the result is to be called a benchmark.

---

# 18. Benchmark V2 Support Audit

V2 added an automatic support audit.

It checks things such as:

```text
answer_supported
needs_all_passages
quantities_comparable
same_quantity
```

For multi-hop / chain questions, the audit also requires substantive passage contributions and a joint reason.

Important caveat:

> The judge is a filter, not ground truth.

The human reviewer remains the final authority.

The audit exists to reduce obvious bad candidates before human review.

---

# 19. Benchmark Problems Already Found

Several accepted questions were found to be problematic.

Examples:

### Curved-ΛCDM simple question

`simple-192b22fb`

The gold chunk did not clearly show the requested curved-ΛCDM H0 value.

Potential gold-evidence mismatch.

---

### Valid but retrieval-hard simple question

`simple-579634ff`

The question asks for three assumptions explicitly represented in a passage.

The benchmark question itself was judged valid, but current retrieval misses the evidence.

This is useful because it demonstrates:

```text
valid benchmark
+
retrieval failure
```

rather than:

```text
invalid benchmark
```

---

### Multi-hop quantity mismatch

`multi_hop-32126f6b`

Compared incompatible quantities.

Should be removed/repaired, not used as evidence.

---

### Multi-hop overclaim

`multi_hop-3cafd9d7`

The answer claimed helium was categorically more effective than deuterium for ruling out solutions.

The passages did not support that broad conclusion.

---

### Temporal mismatch

`temporal-a8985ff7`

The earlier/later passages did not track the same quantity.

---

### Temporal weak evidence

`temporal-c49495fc`

The passages were too generic to establish a controlled earlier/later change.

---

### Chain answerable from abstract

`chain-e650cfbd`

The abstract itself largely answered the generated question, so the later section was unnecessary.

---

# 20. Benchmark V2.1 / Deterministic Pair Sourcing

The current V2 generation direction improves pair sourcing before spending LLM calls.

Current approach:

```text
source chunk
    ↓
dense candidates
+
BM25 candidates
    ↓
union
    ↓
scientific signal filtering
    ↓
specific anchor matching
    ↓
near-duplicate rejection
    ↓
type-specific structural checks
    ↓
LLM generation
    ↓
support audit
    ↓
candidate
```

Relevant file:

```text
src/atlasrag/bench/generate_v2.py
```

The deterministic selector contains logic for:

- scientific signals
- specific scientific signals
- dense + BM25 candidate pools
- duplicate similarity
- complementary evidence
- temporal dates
- temporal update/result cues
- evidence-bearing sections
- chain same-paper checks

This is intentionally conservative.

---

# 21. Scientific Signal / Anchor Idea

The selector attempts to distinguish:

```text
broad topical similarity
```

from:

```text
specific scientific relationship
```

Signals can include:

```text
H0
DESI
BAO
Neff
Ωm
ΛCDM
wCDM
etc.
```

For cross-paper pairs the selector requires:

```text
shared scientific signals
+
shared specific scientific anchor
```

The goal is to reduce false pairing where two passages are both "about cosmology" but do not actually support a shared question.

Do not loosen this simply because generation yield is low.

Low yield may be telling us that the corpus does not contain enough good cross-paper relationships.

---

# 22. Multi-Hop Pair Requirements

A candidate should have:

```text
same scientific topic/object
+
specific anchor
+
shared signals
+
non-duplicate evidence
+
complementary information
```

Both passages need to contribute something distinct.

Bad:

```text
A = definition of X
B = same definition of X
```

Good:

```text
A = reports measurement / constraint
B = reports independent result / parameter relationship
```

and the generated answer genuinely needs both.

---

# 23. Temporal Pair Requirements

Temporal pairs need:

```text
earlier date
+
later date
+
same quantity / claim
+
evidence-bearing sections
+
specific shared anchors
+
actual result/update/refinement/change
```

A later paper discussing a related topic is not enough.

It must support a meaningful temporal comparison.

This is one of the hardest benchmark types and remains incomplete.

---

# 24. Chain Pair Requirements

A valid chain is:

```text
abstract claim
      ↓
later evidence-bearing section
      ↓
specific evidence supporting the claim
      ↓
question requires later evidence
```

Bad:

```text
abstract says X
later section says X again
question asks X
```

Bad:

```text
abstract already contains complete answer
later section irrelevant
```

Good:

```text
abstract claims X
later Results/Methods section gives the measurement/method/result
question asks how X is supported
```

The current chain pilot has not yet produced a reviewed survivor.

---

# 25. Latest Pair Pilot Results

The previous coding agent reported:

## pairpilot

```text
data/bench/questions_v2_pairpilot.jsonl
```

Produced:

```text
1 multi-hop candidate
```

It was manually rejected as a broad-topic pairing.

---

## pairpilot2

```text
data/bench/questions_v2_pairpilot2.jsonl
```

Produced:

```text
1 multi-hop candidate
0 chain candidates
```

The multi-hop survivor was considered structurally credible:

- both excerpts concern baryon-density constraints
- one has direct YHe information
- the other has BAO/CMB correlation behavior

It remained:

```text
candidate
```

not:

```text
accepted
```

Reported rejection counts:

```text
pair_no_shared_specific_signal    9
pair_no_shared_scientific_signal  5
pair_no_evidence_section         21
answer_not_supported              2
not_all_passages_needed           3
missing_joint_reason              3
missing_passage_contributions     2
generator_returned_none           4
```

The rate limit stopped further multi-hop/chain work cleanly.

---

# 26. Important Stale-Pilot Warning

Some older pilot files were generated before the latest structural code.

For example, older pilot candidates may contain:

```text
same_quantity = false
```

for pairings that the current selector would now reject.

Therefore:

> Do not use old pilot artifacts as evidence that the current selector accepts those structures.

They are historical/debug artifacts.

Use the current code + fresh tiny pilots for current behavior.

---

# 27. Test Status

The latest agent-reported test count after the pair-sourcing work was:

```text
55 passed
```

Tests cover:

- structured generation
- missing evidence contributions
- identical passage roles
- comparison without shared quantity
- one-passage-answer rejection
- source-framing rejection
- citation trivia rejection
- temporal validation
- chain validation
- shared scientific signals
- unrelated pairs
- complementary pairs
- near-duplicate rejection
- temporal date requirements
- evidence sections
- chain same-paper requirements
- candidate-pool ranking
- bounded 429 handling

Always rerun tests against the current checkout.

Never assume the reported test count is still current.

---

# 28. Current `llm.py` Instrumentation Gap

There is still an important instrumentation issue.

Current `LLMClient.stats` tracks approximately:

```python
{
    "calls": 0,
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "cache_hits": 0
}
```

This is useful but does not fully persist:

```text
provider API calls
cache misses
retry attempts
RateLimitError count
APIConnectionError count
final rate-limit state
```

This matters because research claims about efficiency need trustworthy accounting.

A logical call can be:

```text
cache hit
```

and therefore produce:

```text
1 logical call
0 provider calls
```

A provider call may also generate multiple physical requests because of retries.

Future instrumentation should distinguish these.

---

# 29. Rate-Limit Reporting Gap

A recent pilot reported:

```text
14 logical calls
15,939 cache-inclusive tokens
```

but cache-hit/provider-call counts were not persisted in the CLI output.

Therefore:

> Do not infer provider-call counts retrospectively from that run.

Future generation commands should persist a machine-readable run summary.

---

# 30. Historical Run 1 Results

Run 1 is frozen.

Evidence-recall results approximately:

```text
A Vanilla       0.52
B Static        0.63
C LLM Router    0.70
E Oracle        0.76
F Always Strong 0.76
G Multi-Hop     0.72
K Static K10    0.65
```

Paired comparisons:

```text
E vs B  +0.13  CI [.04,.26]
F vs B  +0.13  CI [.04,.26]

C vs B  +0.07  CI [-.02,.20]
C vs F  -.06  CI [-.13,0]
G vs F  -.04  CI [-.09,0]
```

Interpretation:

- B substantially improves evidence coverage over A.
- E demonstrates headroom beyond B.
- F performing similarly to E on this benchmark suggests strong retrieval is frequently sufficient.
- C does not yet establish a statistically clear advantage over F.
- C is expensive because routing itself requires LLM calls.
- Correct routing does not automatically solve retrieval/decomposition failures.

Do not overstate these results because:

```text
n = 27
```

and the benchmark is still small.

---

# 31. Cost / Latency History

Approximate reported values:

```text
A:
~0 calls/query
p50 ~0.03s
p95 ~0.08s

B:
~0 calls/query
p50 ~1.92s
p95 ~2.03s

C:
~1.85 calls/query
~444 tokens/query
p50 ~2.93s
p95 ~7.06s

E:
~0.59 calls/query
~145 tokens/query
p50 ~2.10s
p95 ~6.22s

F:
~1 call/query
~242 tokens/query
p50 ~2.21s
p95 ~2.70s
```

Treat these as historical run information.

Do not replace them.

---

# 32. Important Research Interpretation

A key finding from the current benchmark is:

> **Correct multi-hop routing does not automatically solve multi-hop retrieval.**

Some failures occur because:

```text
router chooses MULTI_HOP
        ↓
query decomposition / evidence retrieval
        ↓
still fails to find all gold evidence
```

This means the project must distinguish:

```text
routing failure
```

from:

```text
retrieval/decomposition failure
```

This is a central reason not to train Compass blindly.

---

# 33. Why Route Accuracy Is Not the Main Metric

The LLM router is:

```text
question-semantic classifier
```

The Oracle is:

```text
empirical retrieval-policy selector
```

They do not necessarily predict the same labels for the same theoretical reasons.

Therefore:

```text
route accuracy
```

is a diagnostic.

The more central retrieval metric is:

```text
evidence recall
```

alongside:

```text
paper recall
latency
LLM calls
tokens
cost
```

A route mismatch can still be practically fine if the chosen strategy retrieves all required evidence.

---

# 34. Recommended Evaluation Metrics

The mature evaluation should eventually report:

### Retrieval

```text
evidence recall
paper recall
context precision
context recall
```

### Answer quality

```text
correctness
relevance
faithfulness
citation grounding
```

### Efficiency

```text
LLM calls/query
provider API calls/query
cache-hit rate
prompt tokens
completion tokens
total tokens
latency p50
latency p95
cost/query
```

### Routing

```text
route accuracy
Oracle agreement
over-routing
under-routing
regret vs Oracle
quality/cost frontier
```

Everything important should eventually be stratified by:

```text
SIMPLE
MULTI_HOP
CONFLICTING
TEMPORAL
CHAIN
```

because H4 depends on this breakdown.

---

# 35. H1–H4

Current hypotheses:

### H1

Adaptive retrieval improves answer quality on complex scientific questions compared with a fixed retrieval strategy.

### H2

Compass can approximate an LLM router at substantially lower computational cost.

### H3

Confidence-based escalation can reduce expensive LLM calls while maintaining a predefined quality threshold.

### H4

Adaptive-routing benefits are concentrated in particular question/evidence types rather than uniform across all questions.

H4 is particularly interesting because scientific evidence structures may behave differently.

Do not state these as confirmed findings.

They are hypotheses.

---

# 36. Current Project File Structure

Important implementation areas:

```text
configs/
    default.yaml

src/atlasrag/
    __init__.py
    config.py
    llm.py
    pipeline.py

    ingest/
        ...

    retrieval/
        embedder.py
        index.py
        ...

    routers/
        base.py
        fixed.py
        heuristic.py
        llm_router.py
        oracle.py
        compass.py
        escalating.py

    bench/
        schema.py
        generate.py
        generate_v2.py
        validate.py
        oracle.py
        oracle_v2.py
        experiments.py
        runner.py
        metrics.py
        report.py
        diagnostics.py
        ...

    api/
        main.py

scripts/
    fetch_arxiv.py
    build_index.py
    gen_questions.py
    gen_questions_v2.py
    review_questions.py
    audit_questions.py
    label_oracle.py
    label_oracle_v2.py
    run_experiment.py
    report.py
    route_diagnostics.py
    label_stats.py
    ...

tests/
    test_bench_v2.py
    ...
```

Exact current tree should always be checked in GitHub before editing.

---

# 37. Important Files

## Retrieval

```text
src/atlasrag/retrieval/index.py
src/atlasrag/retrieval/embedder.py
```

## Routing

```text
src/atlasrag/routers/fixed.py
src/atlasrag/routers/llm_router.py
src/atlasrag/routers/oracle.py
src/atlasrag/routers/heuristic.py
src/atlasrag/routers/compass.py
src/atlasrag/routers/escalating.py
```

## Core pipeline

```text
src/atlasrag/pipeline.py
```

## Benchmark

```text
src/atlasrag/bench/schema.py
src/atlasrag/bench/generate.py
src/atlasrag/bench/generate_v2.py
src/atlasrag/bench/validate.py
src/atlasrag/bench/oracle.py
src/atlasrag/bench/oracle_v2.py
src/atlasrag/bench/experiments.py
src/atlasrag/bench/runner.py
```

## Scripts

```text
scripts/gen_questions.py
scripts/gen_questions_v2.py
scripts/review_questions.py
scripts/audit_questions.py
scripts/label_oracle.py
scripts/label_oracle_v2.py
scripts/run_experiment.py
scripts/report.py
```

---

# 38. Current Config

Current main configuration is in:

```text
configs/default.yaml
```

Current important values:

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

reranker:
  model: cross-encoder/ms-marco-MiniLM-L-6-v2

retrieval:
  index_dir: data/index
  dense_k: 20
  bm25_k: 20
  rrf_k: 60

llm:
  model: openai/gpt-oss-20b
```

Do not modify configuration for convenience without checking experimental impact.

---

# 39. Common Commands

PowerShell environment:

```powershell
$env:PYTHONPATH="src"
```

Run tests:

```powershell
python -m pytest -q
```

Run a localized benchmark test:

```powershell
python -m pytest tests/test_bench_v2.py -q
```

Start FastAPI:

```powershell
python -m uvicorn atlasrag.api.main:app --reload --port 8000
```

Fetch papers:

```powershell
python scripts/fetch_arxiv.py --max-papers 30
```

Build index:

```powershell
python scripts/build_index.py
```

Original benchmark generation:

```powershell
python scripts/gen_questions.py --split test --per-type 30
```

V2 benchmark generation:

```powershell
python scripts/gen_questions_v2.py --split test --per-type 20 --types simple multi_hop chain
```

Human review:

```powershell
python scripts/review_questions.py --file data/bench/questions_v2.jsonl --split test --batch 20
```

Audit:

```powershell
python scripts/audit_questions.py --status accepted --split test
```

Oracle v1:

```powershell
python scripts/label_oracle.py --split test --status accepted
```

Oracle v2:

```powershell
python scripts/label_oracle_v2.py --split test --status accepted
```

Experiments:

```powershell
python scripts/run_experiment.py --group run1 --exp A --retrieval-only
python scripts/run_experiment.py --group run1 --exp B --retrieval-only
python scripts/run_experiment.py --group run1 --exp C --retrieval-only
python scripts/run_experiment.py --group run1 --exp E --retrieval-only
```

Report:

```powershell
python scripts/report.py --group run1
```

---

# 40. Git / Reproducibility Rules

GitHub is the shared source of truth.

Repository:

```text
https://github.com/prathamkariya/AtlasRAG
```

Before making changes:

```powershell
git status
git rev-parse HEAD
git log --oneline -5
```

After meaningful changes:

```powershell
git diff
git add <specific files>
git commit -m "clear message"
git push
```

Do not commit:

```text
.env
.venv
raw PDFs
large indexes
temporary zip files
API keys
secrets
```

The `.gitignore` already excludes many of these.

---

# 41. Current GitHub State Warning

A repository verification showed that the visible commit history currently has a baseline commit:

```text
84e891f1b6c010e02733fd2b934b3a724b083044
AtlasRAG benchmark routing baseline
```

At the same time, the current repository tree contains later-looking V2 code such as:

```text
generate_v2.py
test_bench_v2.py
```

Therefore future agents must verify:

```text
current tree
+
current commit history
+
working tree
```

before claiming a change was pushed.

Do not assume an agent's statement:

> "I pushed it"

is sufficient evidence.

---

# 42. Critical Frozen Files

These are historical research assets.

Do not modify without explicit approval:

```text
data/bench/questions.jsonl
data/bench/questions_v1_frozen.jsonl
results/run1/
src/atlasrag/bench/oracle_v2.py
src/atlasrag/bench/experiments.py
```

Also avoid modifying:

```text
embedding model
answering model/provider
```

unless a real bug or controlled experiment requires it.

Historical run1 must remain reproducible.

---

# 43. Current Compass Status

Compass is not trained.

Do not start training immediately.

Reason:

```text
27 accepted test questions
```

is far too small for trustworthy learned routing, especially with:

```text
UNCERTAIN = only 2 questions under Oracle v2
```

and benchmark quality work still in progress.

The Benchmark v2 guide states a training-data gate of approximately:

```text
>=150 labelled training questions
no class under 10%
insufficient share under 25%
v2 vs v2_sufficient decision made
```

Do not train Compass until the data actually satisfies a sensible equivalent of these requirements.

If it does not:

```text
fix the data
```

not:

```text
force the model
```

---

# 44. Why Training Compass Too Early Would Be Bad

With only a tiny, structurally noisy benchmark:

- class distribution can be misleading
- retrieval-insufficient examples can contaminate labels
- temporal/chain/multi-hop examples may be invalid
- the router could learn artifacts instead of query complexity
- test contamination becomes easier
- performance variance becomes huge
- a successful training loss would not mean a useful router

The data-generation pipeline must stabilize first.

---

# 45. Current Highest-Priority Work

The immediate path should be:

```text
CURRENT REPO INSPECTION
        ↓
VERIFY CURRENT TESTS
        ↓
VERIFY V2 PAIR-SOURCING IMPLEMENTATION
        ↓
FIX/ADD PERSISTENT GENERATION INSTRUMENTATION
        ↓
DIAGNOSE CHAIN SOURCING
        ↓
TINY CHAIN PILOT
        ↓
HUMAN REVIEW
        ↓
MULTI-HOP / TEMPORAL / CHAIN BENCHMARK REPAIR
        ↓
MORE CLEAN TRAINING DATA
        ↓
ORACLE LABEL DISTRIBUTION CHECK
        ↓
ONLY THEN COMPASS TRAINING
```

Do not skip directly to Compass.

---

# 46. Chain Sourcing Is the Current Bottleneck

The latest tiny pilots have not produced a reviewed chain survivor.

Possible causes:

```text
candidate-pool sparsity
evidence-section restriction
scientific-overlap restriction
abstract extraction issue
near-duplicate rejection
structured generator rejection
support audit rejection
rate limiting
```

Do not assume which one is responsible.

The next engineering investigation should measure these separately.

---

# 47. What the Next Agent Must Do First

The first response from a new coding agent should NOT be:

> "What would you like me to do?"

The context is already defined.

The agent must first inspect:

```text
https://github.com/prathamkariya/AtlasRAG
```

Then provide:

## Current repository state

```text
branch
commit
working tree state
test count
relevant files
```

## Exact files needing changes

Use a table:

```text
| File | Function/Area | Change | Why | Risk |
```

Only include files that genuinely need modification.

## Files that must remain frozen

Explicitly confirm the frozen list.

## Proposed implementation

Explain:

```text
function
logic
expected behavior
failure modes
tests
```

## Research-safety analysis

State whether the change can affect:

```text
benchmark validity
gold labels
retrieval comparability
historical results
label leakage
generation bias
cost measurement
```

Then, and only then, implement the smallest justified change.

---

# 48. Standard Agent Workflow

The preferred workflow is:

```text
1. Inspect repository
2. Inspect tests
3. Identify problem
4. Explain evidence
5. Identify exact files
6. Propose smallest change
7. Implement
8. Add regression tests
9. Run tests
10. Run tiny pilot if appropriate
11. Inspect generated artifacts
12. Commit
13. Push
14. Report exact commit
```

This prevents agents from wandering into unrelated parts of the project.

---

# 49. "Do Not Do This" List

Never:

```text
train Compass because the current dataset is small
generate hundreds of questions just to increase sample size
loosen validation because survivor yield is low
accept LLM-generated candidates automatically
overwrite v1 benchmark
overwrite run1
change Oracle v2 because its labels are inconvenient
change experiments.py without a real bug
change embedding model before diagnosing the retrieval bottleneck
switch provider/model without a controlled reason
use gold evidence to train the router if it creates leakage
treat old pilot artifacts as current behavior
claim benchmark quality from an automatic judge alone
claim answer-quality gains from retrieval-only metrics
claim route accuracy is the same thing as Oracle agreement
```

---

# 50. Benchmark Versioning Rule

The original benchmark should remain:

```text
v1 / frozen historical benchmark
```

New benchmark work should create a new file/version.

For example:

```text
questions.jsonl
questions_v1_frozen.jsonl
questions_v2.jsonl
```

Never silently replace the historical benchmark.

This makes it possible to compare:

```text
old benchmark
vs
improved benchmark
```

without confusing changes in questions with improvements in the system.

---

# 51. Gold Evidence Definition

Current operational definition:

> Retrieval failure occurs when the retrieved evidence does not contain sufficient information to answer the question correctly.

Gold evidence is the passage/chunk set used to create the question.

Important caveat:

```text
other chunks may also contain enough information
```

so chunk-level gold recall is a conservative metric rather than a perfect measure of answerability.

Do not interpret:

```text
gold recall < 1
```

as automatic proof that the final answer would be wrong.

It means the selected gold evidence was not fully recovered.

---

# 52. Research Experiment Discipline

For any major experiment:

Record:

```text
git commit
Python version
config
corpus version
chunk count
embedding model
reranker
LLM model
benchmark file/version
random seed
cache namespace
experiment code
date/time
```

Do not make post-hoc changes without creating a new experiment group.

---

# 53. Stability Rerun Rule

The project explicitly cares about ordinary benchmark variance.

Every major comparison should eventually have:

```text
run1
run2
```

with a changed cache namespace for a fresh LLM-call path.

Then compare:

```text
ranking stability
metric stability
confidence intervals
```

Do not report one lucky run as definitive.

---

# 54. Future Research Path After Benchmark Stabilization

A reasonable evidence-driven progression is:

```text
A/B/E baseline
     ↓
C analysis
     ↓
benchmark repair
     ↓
C2 Oracle-aligned router experiment, if justified
     ↓
train/test Oracle labels
     ↓
Compass
     ↓
Compass integration
     ↓
stability reruns
     ↓
stratified analysis
     ↓
answer-level evaluation
     ↓
optional V2/V3 extensions
```

The original roadmap is not binding.

Evidence can change the order.

---

# 55. C2 Oracle-Aligned Router Idea

One possible future experiment is to create a separate LLM router whose prompt explicitly targets the empirical Oracle concept.

Instead of asking:

```text
"What is the semantic complexity of this question?"
```

it may ask something closer to:

```text
"Which retrieval strategy is likely sufficient for this question while avoiding unnecessary retrieval?"
```

This should be a new experiment.

Do not overwrite C.

The purpose would be to test whether the gap between:

```text
semantic query-type classification
```

and:

```text
retrieval-policy selection
```

is causing C's current limitations.

---

# 56. Potential Future Compass Dataset

Training examples should eventually look conceptually like:

```text
question
        ↓
Oracle-derived strategy
```

with no answer-context leakage.

Potential classes:

```text
SIMPLE
MULTI_HOP
UNCERTAIN
```

Potential future alternative:

```text
INSUFFICIENT
```

But do not change the label vocabulary without a deliberate experiment/design decision.

The current v2/v2_sufficient distinction should be investigated first.

---

# 57. Long-Term Extensions

After V1 becomes stable:

## V2 — Evidence verification

Question:

> Can a lightweight decision model verify citation support as effectively as an LLM judge?

## V3 — Retrieval-failure prediction

Question:

> Can a lightweight model predict whether the current retrieval policy is likely to fail?

V3 must be trained against gold-evidence definitions, not merely the system's own outputs, to avoid circularity.

---

# 58. Infrastructure

Planned technology stack:

```text
FastAPI
Docker / docker-compose
LangGraph
Weights & Biases
Hugging Face
Kaggle for training
arXiv API
Semantic Scholar
```

But infrastructure is not supposed to become the research variable.

The goal is reproducibility, not Kubernetes complexity.

Kubernetes/k3s is an optional later extension.

---

# 59. Current API

FastAPI is working.

Start locally:

```powershell
$env:PYTHONPATH="src"
python -m uvicorn atlasrag.api.main:app --reload --port 8000
```

Then:

```text
http://localhost:8000/docs
```

The API is a thin layer over the main pipeline.

---

# 60. Corpus Source Strategy

Primary source:

```text
arXiv API
```

Potential metadata augmentation:

```text
Semantic Scholar API
```

The project is focused on scientific papers rather than generic web content.

---

# 61. Important Practical Constraints

This is a student/free-tier project.

Therefore:

- API quota matters
- free-tier rate limits matter
- LLM calls should be cached
- generation should be incremental
- pilots should be small
- expensive answer-level evaluation should happen after retrieval-side validation
- training must fit within affordable/free compute

Do not waste provider quotas on repeated identical prompts.

---

# 62. Why the Current Free LLM Setup Matters

The user has been using free cloud models for development assistance in VS Code.

Current coding-assistant path:

```text
Continue → OpenRouter → free models
```

This is unrelated to experiment results.

The AtlasRAG experiment remains on:

```text
Groq → openai/gpt-oss-20b
```

unless a controlled experiment explicitly changes it.

---

# 63. What Success Would Look Like

A useful future Compass result would show some combination of:

```text
evidence recall close to expensive/stronger routing
+
substantially lower routing cost
+
lower routing latency
+
reasonable Oracle agreement
+
robust performance across question types
```

Especially useful would be evidence that the gains are concentrated in particular scientific evidence structures.

Do not define a numerical "winner" in advance.

Measure it.

---

# 64. What a Negative Result Would Mean

Negative results are useful.

Possible outcomes include:

```text
E ≈ B
```

meaning:

```text
routing provides little additional benefit on this workload
```

or:

```text
C ≈ B
```

meaning:

```text
LLM routing does not add enough value to justify its overhead
```

or:

```text
Compass ≈ C but much cheaper
```

which would support the learned-router idea.

Or:

```text
Compass underperforms
```

which is still useful if the failure is properly diagnosed.

Do not force a positive story.

---

# 65. Resume / Portfolio Framing

Once real results exist, a defensible project description can be:

> Built AtlasRAG, a controlled study of adaptive retrieval routing for scientific-literature QA, extending the Adaptive-RAG paradigm to astrophysics with question-type-stratified evaluation, scientific-evidence failure analysis, and empirical Oracle-ceiling analysis.

After Compass is actually trained and measured, the description can mention:

```text
self-trained LoRA routing model
```

But never invent performance numbers before running the experiments.

---

# 66. Current Open Questions

Still unresolved:

1. Why do temporal benchmark examples remain difficult even under strong retrieval?
2. How much of the multi-hop gap is routing vs decomposition/retrieval?
3. Can chain pairs be sourced reliably from the current corpus?
4. Is the current corpus large/diverse enough for clean scientific evidence types?
5. What is the exact Oracle distribution on a sufficiently large training split?
6. How much label imbalance remains after benchmark repair?
7. Does Oracle-aligned routing outperform semantic complexity routing?
8. What is the cheapest useful strategy under realistic cost constraints?
9. How much benefit remains after answer-level rather than retrieval-only evaluation?
10. Does adaptive routing help uniformly, or only for certain evidence structures?

These are research questions, not assumptions.

---

# 67. Immediate Checkpoint

Current high-level status:

```text
Environment              WORKING
Ingestion                WORKING
Chunking                 WORKING
Index                    WORKING
30 papers                INDEXED
1239 chunks              INDEXED
API                      WORKING
LLM                      WORKING
Run 1                    FROZEN
27 accepted test Qs      EXIST
Oracle v1                EXIST
Oracle v2                EXIST
V2 support audit         EXIST
V2 deterministic pairs   EXIST
Pair pilots              EXIST
Chain survivor           NOT YET
Compass                  NOT TRAINED
Large benchmark          NOT READY
```

The key point is:

> AtlasRAG is past the "basic RAG prototype" stage, but it is not yet at the "train Compass and publish final numbers" stage.

The current bottleneck is benchmark/evidence quality and controlled evaluation.

---

# 68. The Exact Mental Model for a New Agent

Think of AtlasRAG as four layers:

```text
LAYER 1 — RETRIEVAL
Can we recover the required scientific evidence?

LAYER 2 — ROUTING
Can we decide how much retrieval effort is necessary?

LAYER 3 — ANSWERING
Can the answering LLM produce a grounded response?

LAYER 4 — EVALUATION
Can we measure all of this without benchmark contamination?
```

Current project maturity:

```text
Layer 1  → reasonably working, but failures remain
Layer 2  → baseline exists; Compass not yet trained
Layer 3  → working
Layer 4  → actively being hardened
```

The immediate priority is Layer 4 because weak evaluation can make every later result meaningless.

---

# 69. Master Workflow for Continuing the Project

Every new session should follow:

```text
READ THIS MASTER CONTEXT
        ↓
OPEN CURRENT GITHUB REPOSITORY
        ↓
CHECK CURRENT COMMIT + TREE
        ↓
RUN TESTS
        ↓
COMPARE CURRENT CODE TO THIS DOCUMENT
        ↓
IDENTIFY WHAT IS STALE
        ↓
IDENTIFY ONE CURRENT BOTTLENECK
        ↓
PROPOSE EXACT FILE CHANGES
        ↓
IMPLEMENT ONLY AFTER PLAN IS CLEAR
        ↓
RUN REGRESSION TESTS
        ↓
RUN TINY PILOT
        ↓
REVIEW RESULTS
        ↓
COMMIT + PUSH
        ↓
UPDATE PROJECT CONTEXT
```

---

# 70. Final Instruction to Any New AI Agent

You are entering an existing research codebase.

Do not restart the project.

Do not rewrite the architecture because you prefer another framework.

Do not assume the original roadmap is still correct.

Do not assume an older document matches the current repository.

Do not train Compass immediately.

Do not create a huge benchmark immediately.

Do not loosen validation simply to increase candidate yield.

Do not modify historical results.

First inspect the current repository.

Then identify the current real bottleneck.

Then give the exact files/functions that need changing and explain why.

Then make the smallest justified change.

Then test it.

Then run a tiny controlled pilot.

Then commit and push.

The ultimate objective is not simply to make AtlasRAG produce answers.

The objective is to build a **credible, reproducible scientific experiment** that can answer:

> **Can lightweight adaptive retrieval routing improve the evidence-quality/cost tradeoff for scientific literature QA, and are any benefits concentrated in particular scientific evidence structures?**

Everything in future development should serve that question.

---

# 71. Reference Index

## Core prior art

- Adaptive-RAG: https://arxiv.org/abs/2403.14403
- Self-RAG: https://arxiv.org/abs/2310.11511
- FLARE: https://arxiv.org/abs/2305.06983
- RouteLLM: https://arxiv.org/abs/2406.18665
- RouterBench: https://arxiv.org/abs/2403.12031
- Hybrid LLM: https://arxiv.org/abs/2404.14618
- RAGRouter-Bench: https://arxiv.org/abs/2602.00296

## Evaluation

- RAGAS: https://arxiv.org/abs/2309.15217
- ARES: https://arxiv.org/abs/2311.09476

## Parameter-efficient training

- LoRA: https://arxiv.org/abs/2106.09685
- QLoRA: https://arxiv.org/abs/2305.14314

## Frameworks / source repositories

- AtlasRAG: https://github.com/prathamkariya/AtlasRAG
- Adaptive-RAG: https://github.com/starsuzi/Adaptive-RAG
- RouteLLM: https://github.com/lm-sys/RouteLLM
- RAGRouter-Bench: https://github.com/ziqiwang0908/RAGRouter-Bench
- LangGraph: https://github.com/langchain-ai/langgraph
- RAGAS: https://github.com/explodinggradients/ragas
- ARES: https://github.com/stanford-futuredata/ARES

## Data sources

- arXiv API: https://info.arxiv.org/help/api/
- Semantic Scholar API: https://api.semanticscholar.org/

---

# 72. End of Master Context

**Repository:** https://github.com/prathamkariya/AtlasRAG

**Current priority:** benchmark quality + deterministic generation diagnostics + chain sourcing + reproducible cost instrumentation.

**Current forbidden shortcut:** training Compass before the benchmark/training split is sufficiently clean.

**Current principle:** preserve historical evidence, make controlled changes, measure before interpreting.
