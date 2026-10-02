# AtlasRAG V1
### Adaptive Retrieval Routing for Scientific Literature — a Replication and Extension

**Author:** Pratham Kariya ("Megamind")
**Status:** Working paper — Draft v2 (revised scope)
**Domain:** Scientific research papers — starting with Astrophysics (arXiv)
**License target:** MIT (code), CC-BY (writeup)

---

## 1. The research question (revised)

> Does adaptive retrieval routing provide consistent benefits for scientific-literature QA, or are its gains concentrated in particular question types and evidence structures?

This replaces the earlier, broader framing. It is narrower, testable, and — importantly — honest about what is and isn't new (see §2).

---

## 2. Positioning: what is actually novel here

**Adaptive query-complexity routing is established prior art, not a new idea.** Before writing a single line of code, this project is grounded in and explicitly builds on:

- **Adaptive-RAG** (Jeong et al., 2024) — trains a small classifier to route queries among no-retrieval / single-step / multi-step strategies based on predicted complexity. This is structurally the same idea as Compass V1.
- **Self-RAG** (Asai et al., 2024) — embeds retrieval decisions inside generation via reflection tokens.
- **FLARE** (Jiang et al., 2023) — uses generation-probability signals as a retrieval trigger.
- **RAGRouter-Bench** (2026) — a recent baseline study explicitly noting that classifier-based query routing is now a settled pattern; differentiation today comes from domain and implementation, not the mechanism.
- **RouteLLM, FrugalGPT, RouterBench, Hybrid LLM** — the same classifier-routing paradigm applied to *model* selection rather than retrieval-strategy selection, cited here because Compass borrows the same cost/quality-tradeoff framing.

**So the defensible contribution of this project is not "adaptive routing."** It is:

1. Applying the pattern to **scientific literature** — a domain with evidence structure (abstract → methods → results chains, multi-paper conflicts, temporal supersession, tables/equations) that existing adaptive-RAG benchmarks mostly don't test.
2. A **failure taxonomy specific to scientific evidence** (see §8.2).
3. A **stratified evaluation** that reports whether routing helps *uniformly* or only for specific question types (H4, §7) — a breakdown the prior-art papers don't run on this domain.
4. An **Oracle ceiling analysis** (§5) quantifying how much headroom adaptive routing actually has on this domain specifically, rather than assuming the answer.

**Required README/report wording**, to keep this honest everywhere the project is described:

> "Compass implements and extends the adaptive retrieval-routing paradigm established by Adaptive-RAG for scientific literature, with emphasis on question-type-specific behavior and scientific evidence structure."

Never describe Compass or AtlasRAG as inventing adaptive routing. The research question is whether a known pattern holds up, and where it breaks, on a domain it hasn't been rigorously tested against.

---

## 3. A note on Jev — what we're actually building

**Jev is not free.** It's in early access behind a waitlist, priced at $0.042 per million input tokens, with no published free tier or trial credits. A free-tier student project can't be built directly on it today.

So AtlasRAG doesn't call Jev. We build our own small decision model, **Compass** — a frozen small base model + LoRA adapter + lightweight scoring head, the publicly documented Kev-style recipe. Fully open, fully free, fully ours.

---

## 4. Compass V1 — scope, deliberately reduced

Compass V1 has **one job only**: query routing.

```
Question: "What is the main finding of this paper?"
Compass:  SIMPLE        confidence = 0.94

Question: "Compare the evidence for X across these papers."
Compass:  MULTI_HOP     confidence = 0.87
```

Output: a class (`SIMPLE` / `MULTI_HOP` / `UNCERTAIN`) with a confidence score. Nothing else, in V1.

**Why this matters:** if routing, evidence verification, and failure prediction were all introduced at once, a bad final answer would be undiagnosable — you couldn't tell which of three new components caused it. With routing as the only variable, the experiment stays clean: *does adaptive routing itself help?*

Evidence verification and retrieval-failure prediction are deferred to V2/V3 (§10) — built only after V1 produces interpretable results, not in parallel with it.

---

## 5. System architecture — one pipeline, a swappable router

The critical design correction from the original draft: **every experiment must be structurally identical except for who makes the routing decision.** If every branch eventually performs the same hybrid retrieval regardless of router output, the router isn't actually being tested.

```
                         SCIENTIFIC QUERY
                                │
                                ▼
                     ┌───────────────────┐
                     │   ROUTER (swap)   │   ← the only thing that changes
                     │  across A–E below  │      between experiments
                     └─────────┬─────────┘
                                │
               ┌────────────────┼────────────────┐
               ▼                ▼                 ▼
            SIMPLE          MULTI-HOP         UNCERTAIN
               │                │                 │
               ▼                ▼                 ▼
         Dense Retrieval   Query Decomposition  (escalate — see
                                │                 experiment def.)
               └────────────────┼─────────────────┘
                                ▼
                         Hybrid Retrieval
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
               Evaluation (stratified by question type)
```

---

## 6. Five experiments

Controlled, not just "compare two finished systems" — each one isolates a different variable.

| | Experiment | Router | Purpose |
|---|---|---|---|
| **A** | Vanilla RAG | None — naive dense retrieval only | Absolute floor |
| **B** | Strong static RAG | None — fixed hybrid + rerank for every query | Isolates "better retrieval" from "routing" |
| **C** | LLM router | A full LLM decides SIMPLE/MULTI_HOP/UNCERTAIN | Upper bound on router *quality*, at full router *cost* |
| **D** | Compass router | Our self-trained LoRA router | The actual system under test |
| **E** | Oracle | Perfect strategy selection using gold labels | Theoretical ceiling — how much benefit is even available |

**Why the Oracle matters:** it tells you whether routing is worth pursuing *at all* on this domain, independent of how good any particular router is.

```
Static RAG       82%
LLM Router       84%
Compass          83%
Oracle           91%        ← routing has real headroom; Compass captures some of it

vs.

Static RAG       82%
Oracle           83%        ← routing isn't worth much here, for this workload
```

This lets the project attribute any observed benefit to one of: better retrieval (B vs. A), routing itself (E vs. B), router quality (D vs. C vs. E), or just more computation.

---

## 7. Hypotheses

- **H1** — Adaptive retrieval improves answer quality on complex scientific questions compared with a fixed retrieval strategy.
- **H2** — A lightweight decision model (Compass) can approximate an LLM router while requiring substantially less computation.
- **H3** — Confidence-based escalation can reduce expensive LLM calls while maintaining a predefined quality threshold.
- **H4** — The benefit of adaptive routing is concentrated in particular question types and evidence structures rather than uniform across all queries.

H4 is the most important hypothesis in this project — it's the one most likely to produce a genuinely new finding, because it's the one dimension the prior-art papers (§2) don't test on this domain.

---

## 8. Benchmark design

### 8.1 Metrics tracked
| Category | Metric |
|---|---|
| Answer quality | Correctness, relevance |
| Retrieval quality | Context precision, context recall |
| Grounding | Faithfulness score |
| Efficiency | Latency (p50/p95), LLM calls, tokens, $/query |
| Routing quality | Router accuracy vs. gold-labeled "correct path," measured per router (C/D vs. E) |

### 8.2 Question set — stratified by type (the core analysis axis)
- Simple factual lookup (single paper, single fact)
- Multi-hop (evidence from 2+ papers)
- Conflicting findings (does the system surface the conflict, or silently pick one?)
- Temporal (which finding is more recent / superseded?)
- Abstract → methodology → results chains

Every metric in §8.1 is reported **both overall and broken down by these five categories** — the breakdown is what tests H4, and it's the project's main source of a genuinely new finding.

### 8.3 On gold evidence (needed for Oracle and later V3)
Define retrieval failure rigorously, to avoid circularity later:

> Retrieval failure occurs when the retrieved evidence does not contain sufficient information to answer the question correctly.

This requires a gold-labeled set of (question, known supporting passages) pairs, built during benchmark construction — not inferred from the system's own outputs.

### 8.4 On benchmark honesty
Published comparisons of model-routing systems have shown rankings **flip between two identical runs** of the same benchmark from ordinary variance alone. Before any number goes in the README: run the full benchmark twice, check whether the ranking across experiments A–E holds, and report the stable findings prominently — and the unstable ones honestly.

---

## 9. Build phases — realistic V1 timeline

### Week 1 — Corpus + baseline
Choose one field (Astrophysics). Download papers via the arXiv API. Build section-aware chunking that keeps tables/equations intact. Implement embeddings, BM25, hybrid retrieval, reranking. Produce baseline (Experiment A/B) answers.

### Week 2 — Benchmark
Define the five question categories (§8.2). Build the initial evaluation set with gold evidence labels (§8.3). Establish baseline metrics. Confirm reproducibility.

### Week 3 — Compass
Build labeled routing data. Fine-tune the LoRA router on Kaggle's free GPU tier. Evaluate routing accuracy **in isolation** — do not integrate until it works independently.

### Week 4 — Adaptive system integration
Integrate Compass into the shared architecture (§5) via LangGraph. Implement query decomposition for the multi-hop path. Run Experiments C, D, E alongside A/B, keeping every path structurally identical except the router.

### Week 5 — Evaluation + polish
Run all five experiments. Rerun the full benchmark a second time (§8.4). Analyze results stratified by question type (H4). Build charts, clean the repo, write the short report.

> **3 weeks = minimum serious prototype. 4–5 weeks = strong, polished V1.**

### V2 (optional, after V1 is stable) — Evidence verification
> Can a lightweight decision model verify citation support as effectively as an LLM judge?

### V3 (optional, after V2) — Retrieval-failure prediction
Trained only against the gold-evidence definition in §8.3, to avoid circularity.

---

## 10. Cloud / DevOps — infrastructure from day one, not a research variable

Per the explicit decision for this project: infrastructure is built in from the start, but it stays infrastructure — it never becomes something the research question depends on, and Kubernetes-scale complexity is deliberately kept out of V1.

**In V1, from Week 1:**
- **Containerized from day one** — `docker-compose` with separate services for retrieval, Compass, and the LLM gateway. Every experiment (A–E) runs from the same containers; only the router component swaps.
- **Experiment tracking from day one** — every run (and every rerun, per §8.4) logged to Weights & Biases, so results are reproducible and comparable across the five experiments without manual spreadsheet-wrangling.
- **API exposed from day one** — a thin FastAPI layer in front of the pipeline, so the system is a callable service, not just a notebook, from the first working version.
- **Reproducible deployment** — pinned dependencies, a single `docker-compose up` reproduces the full benchmark run. This is the actual DevOps skill being demonstrated in V1: not infrastructure scale, but reproducibility discipline.

**Deferred to a later, explicitly optional extension (not required to call V1 complete):**
- Kubernetes (k3s on Oracle Cloud Always Free), canary rollout, drift detection, CI-gated regression testing on every commit.
- These remain valuable and are still part of the long-term roadmap — they're just not allowed to become the project itself, or to delay the actual research in §1.

---

## 11. Tech stack — 100% free tier

| Layer | Tool | When | Cost |
|---|---|---|---|
| Orchestration | LangGraph | V1, Week 4 | Free, open-source |
| Decision model | Compass (self-trained LoRA) | V1, Week 3 | Free (Kaggle GPU) |
| Embeddings | Cohere Embed v3 trial / bge-large (self-hosted) | V1, Week 1 | Free |
| Reranking | Cohere Rerank v3 trial / bge-reranker | V1, Week 1 | Free |
| LLM calls | Groq free tier + Gemini free tier | V1 | Free, no card |
| Vector store | Supabase pgvector / Chroma self-hosted | V1, Week 1 | Free |
| Training compute | Kaggle (30 GPU-hrs/week) | V1, Week 3 | Free |
| Containerization | Docker / docker-compose | V1, Week 1 (from the start) | Free |
| API layer | FastAPI | V1, Week 1 (from the start) | Free |
| Experiment tracking | Weights & Biases | V1, Week 1 (from the start) | Free tier |
| Model hosting | Hugging Face Hub | V1, Week 3+ | Free |
| Eval framework base | Ragas / ARES | V1, Week 2 | Free, open-source |
| CI/CD | GitHub Actions | Extension (post-V1) | Free, public repos |
| Deployment at scale | Oracle Cloud Always Free + k3s | Extension (post-V1) | Free, permanent |

### What your student email is actually useful for
Qualifies you for the **GitHub Student Developer Pack** — bundled credits and tier upgrades across partner tools. Worth claiming in Week 1, since some offers are one-time and tied to account age.

---

## 12. Getting started — account checklist

- [ ] Kaggle account (GPU quota)
- [ ] Hugging Face account (model hosting)
- [ ] GitHub account + Student Developer Pack claimed with university email
- [ ] Groq API key (free, no card)
- [ ] Gemini API key (free tier)
- [ ] Cohere trial key (Embed + Rerank)
- [ ] Supabase account (free-tier Postgres/pgvector)
- [ ] Weights & Biases account (free tier)
- [ ] Docker installed locally
- [ ] Oracle Cloud account (Always Free tier — for the post-V1 extension only)

---

## 13. Related resources & references

**Direct prior art (cite explicitly in the report):**
- Adaptive-RAG — Jeong et al., 2024. https://arxiv.org/abs/2403.14403 · code: https://github.com/starsuzi/Adaptive-RAG
- Self-RAG — Asai et al., 2024.
- FLARE — Jiang et al., 2023.
- RAGRouter-Bench (2026) — baseline study on lightweight query routing.

**Model-routing analogues (cited for the cost/quality-tradeoff framing):**
- RouteLLM, FrugalGPT, RouterBench, Hybrid LLM.

**Frameworks used directly:**
- LangGraph — https://github.com/langchain-ai/langgraph
- Ragas — https://github.com/explodinggradients/ragas
- ARES — https://github.com/stanford-futuredata/ARES

**Data sources:**
- arXiv API — https://info.arxiv.org/help/api/
- Semantic Scholar API — https://api.semanticscholar.org/

**Training recipe:**
- Kev-style LoRA + scoring-head recipe — the template for training Compass cheaply.

---

## 14. FAQ

**Is this a novel contribution, or a replication?**
Both, honestly. The routing *mechanism* (Compass) replicates Adaptive-RAG's established pattern. The *contribution* is applying it rigorously to scientific literature, with a question-type-stratified evaluation and an Oracle ceiling analysis that quantify exactly where it does and doesn't help — on a domain the prior-art papers don't test.

**Do we use Jev?**
No — it's paid and waitlist-gated. We build our own equivalent (Compass), which is free and a stronger portfolio story.

**Why five experiments instead of four?**
The Oracle (Experiment E) answers a different question than the other four: not "which router is best" but "how much is there to gain from routing at all, on this domain." Without it, a weak result could mean either "routing doesn't help here" or "our router is bad" — you can't tell which.

**What if I run out of free GPU hours?**
Compass is small enough that a full training run fits comfortably inside Kaggle's 30 free hours/week. Embedding and reranking are CPU-friendly at this corpus size.

**Does the Docker/API/tracking layer delay the research?**
No — it's lightweight by design specifically so it doesn't. Kubernetes-scale infrastructure is what's deferred, not basic reproducibility tooling.

**What happens if H1–H3 come back negative?**
That's still a real, reportable result (see §6's Oracle-ceiling logic) — a negative finding on H1 with a well-run Oracle analysis is more credible than an inflated positive claim.

---

## 15. Resume / LinkedIn framing

> "Built AtlasRAG V1, a controlled study of adaptive retrieval-routing (extending Adaptive-RAG) for scientific-literature QA — implementing a self-trained LoRA router (Compass) and comparing it against static, LLM-routed, and oracle-ceiling baselines across five structurally identical pipelines, with results stratified by question type. Containerized and tracked from day one (Docker, FastAPI, W&B) for full reproducibility."

Once real experiments produce numbers, replace the generic claim with specifics, e.g.:

> "Found adaptive routing reduced LLM calls by [X]% with [Y]% quality retention overall — concentrated almost entirely in multi-hop and conflicting-evidence questions, with negligible benefit on simple lookups."

Never invent X or Y before running the experiment.
