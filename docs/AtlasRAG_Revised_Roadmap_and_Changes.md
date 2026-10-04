# AtlasRAG --- Revised Roadmap & Scope

## What changed from the original roadmap?

The original AtlasRAG roadmap is a strong **master plan**, but after
reviewing the project from a feasibility, research, and resume
perspective, it is too large to treat as the first implementation
target.

The new approach is:

> **Build a small, falsifiable research project first. Add advanced
> components only when the results justify them.**

The original roadmap should therefore be treated as a long-term roadmap,
not a V1 checklist.

------------------------------------------------------------------------

# 1. The core idea stays the same

The strongest part of the original proposal should remain unchanged:

> **Can a small, purpose-built decision model choose retrieval/reasoning
> strategy per query so that a scientific RAG system improves the
> quality/efficiency tradeoff?**

The project should still be more than a chatbot.

The important deliverable remains:

-   A working scientific RAG system.
-   A lightweight decision model.
-   Controlled comparisons against baselines.
-   A reproducible benchmark.
-   Actual measured results.

The original document correctly framed the contribution as a measured
answer to a research question rather than simply a RAG application.

------------------------------------------------------------------------

# 2. Major change: reduce Compass V1

## Original roadmap

Compass was planned to perform three jobs:

1.  Query routing.
2.  Evidence verification.
3.  Retrieval-failure prediction.

This is technically interesting, but too much for the first version.

## Revised plan

### Compass V1 should only be a query/retrieval router.

Its initial output should be something like:

``` text
SIMPLE
MULTI_HOP
UNCERTAIN
```

with a confidence score.

Example:

``` text
Question:
"What is the main finding of this paper?"

Compass:
SIMPLE
confidence = 0.94
```

Another:

``` text
Question:
"Compare the evidence for X across these papers."

Compass:
MULTI_HOP
confidence = 0.87
```

This gives Compass one clear responsibility:

> **Choose how much retrieval/reasoning the query needs.**

------------------------------------------------------------------------

# 3. Why simplify Compass?

If routing, verification, and failure prediction are all introduced
simultaneously, a bad final answer becomes difficult to diagnose.

A failure could come from:

``` text
Compass
   ↓
retrieval
   ↓
reranker
   ↓
evidence verification
   ↓
LLM
```

With only routing in V1, the experiment becomes much cleaner.

You can ask:

> **Does adaptive routing itself improve the system?**

If the answer is yes, additional capabilities can be added later.

If the answer is no, you have learned something meaningful without
spending weeks building unnecessary infrastructure.

------------------------------------------------------------------------

# 4. The benchmark becomes the heart of the project

The original roadmap already had four systems:

1.  Vanilla RAG.
2.  Static advanced RAG.
3.  LLM-based router.
4.  AtlasRAG with Compass.

Keep these.

However, add an optional fifth system:

## Oracle Router

The oracle represents an idealized router that always knows the best
retrieval strategy.

Its purpose is not deployment.

Its purpose is answering:

> **How much theoretical benefit is even available from adaptive
> routing?**

Example:

``` text
Static RAG       82%
LLM Router       84%
Compass          83%
Oracle           91%
```

This tells us that routing has substantial potential, but Compass is
only capturing part of it.

If instead:

``` text
Static RAG       82%
Oracle           83%
```

then adaptive routing may not be particularly valuable for that
workload.

This makes the experiment much more informative.

------------------------------------------------------------------------

# 5. Revised experiment structure

The project should use controlled experiments rather than simply
comparing two finished systems.

### Experiment A --- Baseline

``` text
Vanilla RAG
```

### Experiment B --- Strong static RAG

``` text
Hybrid retrieval
+
Reranking
+
LLM
```

### Experiment C --- LLM router

``` text
LLM
 ↓
retrieval strategy
 ↓
RAG
```

### Experiment D --- Compass router

``` text
Compass
 ↓
retrieval strategy
 ↓
RAG
```

### Experiment E --- Oracle

``` text
Perfect strategy selection
 ↓
RAG
```

This lets the project determine whether the benefit comes from:

-   Better retrieval.
-   Routing itself.
-   The type of router.
-   Or simply adding more computation.

------------------------------------------------------------------------

# 6. Revised architecture

The original architecture should be simplified for V1.

``` text
                         SCIENTIFIC QUERY
                                │
                                ▼
                           ┌─────────┐
                           │ Compass │
                           │ Router  │
                           └────┬────┘
                                │
               ┌────────────────┼────────────────┐
               ▼                ▼                ▼
            SIMPLE          MULTI-HOP        UNCERTAIN
               │                │                │
               ▼                ▼                ▼
         Dense Search      Query Rewrite     LLM Router
                                │
                                ▼
                         Adaptive Retrieval
                                │
                                ▼
                            Reranker
                                │
                                ▼
                               LLM
                                │
                                ▼
                         Answer + Citations
                                │
                                ▼
                           Evaluation
```

The important correction is that the routing decision must actually
change the computational path.

If every branch eventually performs exactly the same hybrid retrieval,
the router does not provide much value.

------------------------------------------------------------------------

# 7. Evidence verification becomes V2

The original roadmap included Compass-based evidence verification.

Keep it, but move it to a later version.

After V1 proves that routing works, add:

``` text
Generated claim
      ↓
Evidence verifier
      ↓
Supported / Unsupported
```

This can become a second research experiment:

> Can a lightweight decision model verify citation support as
> effectively as an LLM judge?

Do not build this before the routing experiment is stable.

------------------------------------------------------------------------

# 8. Retrieval-failure prediction becomes V3

The original proposal included predicting retrieval failure before
retrieval.

This is potentially one of the most interesting parts of the entire
project, but it requires a rigorous definition of "retrieval failure."

A useful definition would be:

> Retrieval failure occurs when the retrieved evidence does not contain
> sufficient information to answer the question correctly.

The benchmark then needs gold evidence.

For example:

``` text
Question
   +
Known supporting passages
        ↓
Did top-k retrieval contain sufficient evidence?
        ↓
YES / NO
```

Only after establishing this ground truth should Compass be trained to
predict retrieval failure.

This prevents the system from becoming circular.

------------------------------------------------------------------------

# 9. Do not hard-code the confidence thresholds

The original roadmap proposed starting thresholds such as:

``` text
> 0.90 → automatic
0.70–0.90 → log/review
< 0.70 → LLM
< 0.50 → human review
```

Keep these only as experimental starting points.

Do not present them as scientifically justified values.

Instead, test multiple thresholds:

``` text
0.50
0.60
0.70
0.80
0.90
```

Then measure:

-   Answer quality.
-   Routing accuracy.
-   LLM calls.
-   Latency.
-   Token usage.
-   Cost.

The goal is to find a useful quality/efficiency tradeoff.

------------------------------------------------------------------------

# 10. Add explicit hypotheses

The revised project should explicitly test hypotheses.

## H1

Adaptive retrieval improves answer quality on complex scientific
questions compared with a fixed retrieval strategy.

## H2

A lightweight decision model can approximate an LLM router while
requiring substantially less computation.

## H3

Confidence-based escalation can reduce expensive LLM calls while
maintaining a predefined quality threshold.

## H4

The benefit of adaptive routing is concentrated in particular question
types rather than being uniform across all queries.

H4 is especially interesting because the final result might show that
routing helps multi-hop questions but provides little benefit for simple
factual questions.

------------------------------------------------------------------------

# 11. Keep the scientific-paper domain

The original choice of scientific literature should remain.

Scientific papers naturally provide:

-   Long documents.
-   Technical terminology.
-   Tables.
-   Equations.
-   Multi-hop questions.
-   Conflicting findings.
-   Temporal differences.
-   Evidence spread across sections or papers.

However, do not start with all scientific literature.

## Start with one field.

A practical choice is:

### Astrophysics

This gives the project a focused corpus while also connecting it to the
broader scientific-ML/astronomy direction.

Possible future expansion:

``` text
Astrophysics
    ↓
Other sciences
    ↓
Cross-domain scientific literature
```

------------------------------------------------------------------------

# 12. Revised project scope

## V1 --- Required

``` text
Scientific paper corpus
        ↓
Baseline RAG
        ↓
Hybrid retrieval
        ↓
Reranking
        ↓
Compass router
        ↓
Adaptive retrieval
        ↓
LLM
        ↓
Citations
        ↓
Benchmark
```

## V2 --- Optional

``` text
Evidence verification
+
Confidence calibration
```

## V3 --- Optional

``` text
Retrieval-failure prediction
+
Human escalation
```

## V4 --- Optional

``` text
Docker
Kubernetes
Observability
CI/CD
Cloud deployment
```

## V5 --- Optional

``` text
Technical report
+
Public benchmark
+
Research submission
```

Do not make V2--V5 prerequisites for considering the project complete.

------------------------------------------------------------------------

# 13. Revised timeline

The original roadmap estimated approximately 9 weeks when including the
cloud/DevOps phase.

That is reasonable for the full version, but too large for the first
deliverable.

## Realistic V1

### Week 1 --- Corpus + baseline

-   Choose one scientific field.
-   Download papers.
-   Build section-aware chunking.
-   Implement embeddings.
-   Implement BM25.
-   Add hybrid retrieval.
-   Add reranking.
-   Produce baseline answers.

### Week 2 --- Benchmark

-   Define question categories.
-   Create an initial evaluation set.
-   Establish baseline metrics.
-   Make sure the benchmark is reproducible.

### Week 3 --- Compass

-   Create labeled routing data.
-   Fine-tune the small model with LoRA.
-   Evaluate routing accuracy separately.
-   Do not integrate it until it works independently.

### Week 4 --- Adaptive system

-   Integrate Compass with LangGraph.
-   Implement different retrieval paths.
-   Compare Compass against the LLM router.

### Week 5 --- Evaluation + polish

-   Run all systems.
-   Perform ablations.
-   Repeat experiments.
-   Analyze failures.
-   Build charts.
-   Create demo.
-   Clean GitHub repository.

So:

> **3 weeks = minimum serious prototype.**

> **4--5 weeks = strong polished project.**

> **6--9+ weeks = extended research + infrastructure version.**

------------------------------------------------------------------------

# 14. Cloud / DevOps is no longer a requirement for V1

The original roadmap had Kubernetes, Oracle Cloud, k3s, GitHub Actions,
etc.

These remain useful, but they should be treated as extensions.

Do not delay the actual research because you are configuring Kubernetes.

A good order is:

``` text
Research result
      ↓
Working system
      ↓
Benchmark
      ↓
Demo
      ↓
Docker
      ↓
Cloud
      ↓
Kubernetes
```

If the project is already strong after the benchmark, stop there or move
to the next project.

------------------------------------------------------------------------

# 15. You do NOT need to publish a paper

There are three useful levels.

## Level 1 --- Project

``` text
GitHub
+
Demo
+
Benchmark
+
README
```

Enough for a resume.

## Level 2 --- Technical report

Write a short paper-style report:

``` text
AtlasRAG:
Adaptive Retrieval for Scientific Literature
```

It can live inside the repository.

No publication is required.

## Level 3 --- Actual publication

Optional:

-   arXiv.
-   Workshop.
-   Student research venue.
-   Conference.

Do this only if the results are strong and you genuinely want the
research experience.

------------------------------------------------------------------------

# 16. Revised resume positioning

Do not claim:

> Published a research paper on AtlasRAG

unless it is actually published.

Instead:

## AtlasRAG --- Adaptive Scientific Literature RAG

`Python · PyTorch · LangGraph · BM25 · Vector Search · LoRA`

Potential final bullets:

> Built an adaptive RAG system for scientific literature using a
> lightweight LoRA-finetuned decision model to route queries between
> retrieval strategies.

> Developed a benchmark covering simple, multi-hop, conflicting-evidence
> and temporal questions, comparing static RAG, LLM-based routing and
> lightweight model routing across answer quality, groundedness,
> citation correctness and efficiency.

> Implemented hybrid BM25+dense retrieval, cross-encoder reranking and
> reproducible evaluation pipelines.

Once actual experiments produce meaningful results, replace generic
claims with real numbers.

For example:

``` text
Reduced LLM calls by X%
while maintaining Y% of baseline answer quality.
```

Never invent X or Y before running the experiment.

------------------------------------------------------------------------

# 17. What makes the project impressive

The project should ultimately demonstrate:

``` text
RAG
+
Retrieval
+
Small-model fine-tuning
+
Decision systems
+
Evaluation
+
Experimental methodology
+
Systems engineering
```

The impressive part is not:

> "I used Jev."

It is:

> "I investigated whether a lightweight decision model can intelligently
> allocate retrieval/reasoning resources, built the model myself, and
> experimentally compared it against static and LLM-based approaches."

------------------------------------------------------------------------

# 18. What NOT to do

Do not start by implementing:

``` text
RAG
+
Agents
+
Memory
+
Knowledge Graph
+
Multimodal
+
Kubernetes
+
20 models
+
Human review
+
Three Compass heads
```

That creates a large system where it becomes impossible to identify what
actually caused an improvement.

Instead:

> **One research question → one clear decision model → controlled
> experiments.**

------------------------------------------------------------------------

# 19. Final recommendation

The original AtlasRAG roadmap should remain as the **master roadmap**.

But the actual project should begin as:

# AtlasRAG V1

> **Does a lightweight learned router improve the quality/efficiency
> tradeoff of scientific RAG compared with static RAG and LLM-based
> routing?**

Build:

``` text
Scientific corpus
       ↓
Baseline RAG
       ↓
Compass
       ↓
Adaptive retrieval
       ↓
4-way comparison
       ↓
Evaluation
       ↓
Demo + GitHub
```

Then let the results determine whether V2 is worth building.

This makes the project:

-   Feasible.
-   Realistic.
-   Research-flavored.
-   Resume-worthy.
-   Measurable.
-   Much easier to explain in interviews.
-   Much less likely to become an endless engineering project.

------------------------------------------------------------------------

# Bottom line

**The original roadmap was not wrong. It was simply too ambitious as a
starting scope.**

Keep the original document as the **long-term AtlasRAG roadmap**.

Use this revised version as the **actual build plan**.

The first milestone is not:

> "Build a production-grade RAG platform."

It is:

> **"Build a controlled experiment that can answer whether our
> lightweight decision model actually makes RAG better."**

If the answer is yes, expand it.

If the answer is no, analyze why.

Either outcome gives you a legitimate technical result.
