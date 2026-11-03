# AtlasRAG — Week 2: Benchmark Construction, Repair, Oracle Labels, and V2 Generation

**Project:** AtlasRAG  
**Repository:** `https://github.com/prathamkariya/AtlasRAG`  
**Week:** 2  
**Focus:** Benchmark construction, benchmark validation, Oracle labeling, retrieval sufficiency, deterministic evidence-pair sourcing, and safe generation of a new benchmark version.

> **Status note:** This file is a continuation of the AtlasRAG master context and Week 1 foundation. It records what actually happened during Week 2, not just the original plan. Historical results, current code, pilots, and future work are explicitly separated so that a new AI agent does not confuse planned work with completed work.

---

## 0. Purpose of This File

Week 2 is the methodological center of AtlasRAG.

The retrieval pipeline was already functioning by the start of this week. The central problem became different:

> How do we construct a benchmark that can actually measure adaptive retrieval/routing without teaching the router artifacts produced by a weak or structurally invalid question set?

The original benchmark generation approach relied too heavily on generic semantic nearest-neighbor pairing. That was enough to produce questions, but not enough to guarantee that two passages represented two pieces of evidence that genuinely needed to be joined.

During Week 2, the project therefore moved through several stages:

```text
original question generation
        ↓
human review
        ↓
27 accepted questions
        ↓
Oracle v1
        ↓
baseline routing experiments
        ↓
failure analysis
        ↓
Oracle v2
        ↓
support audit
        ↓
structured V2 generation
        ↓
conservative validation gates
        ↓
deterministic pair sourcing
        ↓
tiny pilots
```

The important conclusion is that benchmark quality became a prerequisite for Compass training. Compass must not be trained against the current 27-question set merely because labels exist.

---

# 1. Week 2 Research Objective

The original high-level AtlasRAG research direction was adaptive routing between different retrieval strategies.

The useful empirical question that emerged from the Week 1/run-1 results is better expressed as:

> **Can a lightweight learned router retain the evidence quality of a strong retrieval policy while reducing unnecessary retrieval/LLM cost, approaching an empirical cheapest-sufficient oracle?**

This matters because the baseline results did **not** show a simple story such as “LLM routing wins.”

The important frozen result was approximately:

```text
A Vanilla       0.52 evidence recall
B Static        0.63
K Static K10    0.65
C LLM Router    0.70
G Always Multi  0.72
F Always Strong 0.76
E Oracle        0.76
```

The exact run-1 artifacts remain frozen under `results/run1/`.

The benchmark must therefore distinguish at least four things:

```text
question validity
        ↓
gold evidence validity
        ↓
retrieval sufficiency
        ↓
routing quality
```

A routing model cannot be judged fairly when one or more of these layers is broken.

---

# 2. Starting Point: The Original 27-Question Benchmark

The first benchmark generation/review process produced:

```text
94 generated candidates
27 accepted test questions
67 rejected
```

Generation by type originally produced roughly:

```text
simple       30 / 30
multi_hop    30 / 30
conflicting   1 / 30
temporal     17 / 30
chain        16 / 30
```

After human review, only 27 questions remained accepted.

The benchmark was manually reviewed using:

```powershell
python scripts/review_questions.py --batch 20
```

The review process reached:

```text
0 candidates remaining
```

This original benchmark is now treated as **v1**.

Important files:

```text
data/bench/questions.jsonl

data/bench/questions_v1_frozen.jsonl
```

`questions.jsonl` is the original benchmark file.  
`questions_v1_frozen.jsonl` is an explicit frozen copy made so later benchmark repair cannot silently rewrite the baseline.

### Critical rule

Never overwrite v1 to make the benchmark look cleaner.

Future repaired/generated benchmark versions belong in separate files such as:

```text
data/bench/questions_v2.jsonl
```

This preserves the scientific interpretability of the original experiment.

---

# 3. Benchmark Question Types

AtlasRAG originally considered multiple question structures because routing behavior should differ according to the information need.

## 3.1 SIMPLE

A simple question should be answerable from one relevant evidence passage.

Conceptually:

```text
question
   ↓
one evidence-bearing passage
   ↓
answer
```

Examples can ask for a reported value, stated assumption, model property, or a scientific result.

However, a simple question should not degenerate into citation trivia such as:

```text
According to paper X, what is the title?
```

or a purely source-framed question where the question itself is about the document rather than the science.

The V2 generator therefore adds quality checks for these patterns.

---

## 3.2 MULTI_HOP

A true multi-hop question must require information from at least two passages.

A useful structure is:

```text
Passage A → scientific fact/result A
Passage B → scientific fact/result B
             ↓
         joint reasoning
             ↓
           answer
```

A merely related pair is not enough.

Bad structure:

```text
A = definition of X
B = same definition of X
question = what is X?
```

The first passage alone already answers the question.

Better structure:

```text
A = measurement/constraint/model result
B = independent result or parameter relationship
question = compare/combine/derive an answer that needs both
```

The generator must therefore verify not only similarity, but complementarity.

---

## 3.3 TEMPORAL

A temporal question requires meaningful comparison across time.

Required structure is approximately:

```text
earlier evidence
      ↓
shared scientific quantity/claim
      ↓
later evidence
      ↓
change / update / refinement / revised constraint
```

Simply having:

```text
older paper
+
newer paper
+
same word
```

is not a valid temporal relationship.

A valid temporal pair should normally contain:

```text
different publication dates
same or tightly corresponding quantity/claim
specific scientific anchor(s)
evidence-bearing sections
result/update/refinement language
```

Temporal generation has been one of the weakest parts of the current corpus and remains incomplete.

---

## 3.4 CONFLICTING

Conflicting questions were intended to compare sources that disagree or expose genuine tension.

A valid conflict requires:

```text
same quantity or claim
+
compatible meaning/units
+
genuine disagreement or tension
```

This must not be reduced to “the numbers are different.”

For example, the earlier generator produced a bad comparison involving:

```text
H0 ≈ 73 km/s/Mpc
vs
contamination ≈ 76%
```

Those numbers are not the same scientific quantity, so the pair cannot form a valid numerical comparison.

The V2 validator explicitly guards against this class of error.

There was little useful accepted conflicting data in the original test set, so this type should not be treated as a mature benchmark category yet.

---

## 3.5 CHAIN

A chain question is different from ordinary two-passage multi-hop.

The intended structure is:

```text
abstract / early claim
        ↓
later evidence-bearing section
        ↓
concrete measurement / method / result
        ↓
question requiring the later evidence
```

Bad chain:

```text
abstract says X
later section says X again
question asks X
```

The abstract already contains the answer.

Another bad chain:

```text
abstract says X
later section discusses unrelated Y
question asks X
```

Good chain:

```text
abstract says X
later Results/Analysis/Methods section reports the actual evidence
question asks how X is supported or what concrete evidence establishes X
```

The current corpus has not yet yielded a reviewed chain survivor from the newest deterministic sourcing implementation.

---

# 4. Oracle v1: What It Did and Why It Became a Problem

After the 27 accepted questions were frozen, Oracle v1 was run using:

```powershell
python scripts/label_oracle.py --split test --status accepted
```

Observed result:

```text
n = 27
SIMPLE = 11
MULTI_HOP = 5
UNCERTAIN = 11
insufficient = 9
```

The important issue was the meaning of `UNCERTAIN`.

Under the v1 implementation, if no strategy in the retrieval ladder achieved gold evidence recall of at least `1.0`, the final label could fall through to `UNCERTAIN` and the question would be marked `oracle_sufficient=false`.

Therefore the single label:

```text
UNCERTAIN
```

could combine two different phenomena:

```text
semantic/routing uncertainty
+
retrieval insufficiency under the benchmark metric
```

Those are not the same thing.

A router should not be trained to interpret retrieval failure as a semantic intent class.

This was one of the main methodological reasons for Oracle v2.

---

# 5. Oracle v2

Oracle v2 preserves the recall achieved by **every strategy** instead of collapsing everything into one final label.

Relevant file:

```text
src/atlasrag/bench/oracle_v2.py
```

Core logic:

```python
best=max(recs.values())
q.ladder_recalls=recs
q.gold_route_v2=next(l for l in ladder if recs[l]>=best-eps)
q.oracle_sufficient=best>=1.0-eps
```

The conceptual process is:

```text
retrieve with every ladder strategy
        ↓
store every evidence recall
        ↓
find best observed recall
        ↓
choose the cheapest strategy within ε of best
        ↓
mark whether any strategy was fully sufficient
```

This changes the interpretation from:

```text
“What label happened to be selected first?”
```

to:

```text
“What retrieval strategy can satisfy the evidence requirement at the lowest observed cost?”
```

That is much closer to the research problem.

---

# 6. Oracle v2 Results on the Existing 27 Questions

Oracle v2 produced approximately:

```text
SIMPLE       18
MULTI_HOP     7
UNCERTAIN     2
```

and separately:

```text
insufficient = 9
```

The correct interpretation is:

```text
18 questions → at least one strategy reaches full gold evidence recall
9 questions  → no tested strategy fully reaches the gold evidence requirement
```

The `2 UNCERTAIN` questions are **not** the same as the 9 insufficient questions.

This distinction is fundamental for any future training set.

The preferred future Oracle training scheme is:

```text
v2_sufficient
```

because it excludes questions for which no strategy can fully satisfy the current gold evidence requirement.

This does not mean the 9 insufficient questions are useless. They can remain valuable as evaluation/debugging examples, but they should not be treated as clean supervised routing labels.

---

# 7. Why Retrieval Sufficiency Matters

Suppose the benchmark says:

```text
Gold chunks = A + B
```

but the corpus/index makes it impossible for any current strategy to retrieve A or B.

Then a router cannot solve the problem simply by choosing:

```text
SIMPLE
MULTI_HOP
UNCERTAIN
```

The evidence is unavailable under the current retrieval system.

This gives a useful distinction:

```text
ROUTING FAILURE
    ↓
wrong strategy chosen

RETRIEVAL FAILURE
    ↓
correct strategy still cannot recover the required evidence

BENCHMARK FAILURE
    ↓
gold passage/question/answer relationship itself is invalid or misaligned
```

The week-2 workflow exists to separate these cases.

---

# 8. Support Audit

A support audit was added to inspect whether generated or existing questions have a defensible relationship between:

```text
question
reference answer
passage 1
passage 2
```

Command used for the accepted test set:

```powershell
python scripts/audit_questions.py --status accepted --split test
```

Observed result:

```text
19 / 27 passed
8 / 27 flagged
```

Reported reason counts were:

```text
not_all_passages_needed = 7
answer_not_supported    = 2
different_quantity       = 1
```

The audit can produce fields such as:

```text
answer_supported
unsupported_claims
needs_all_passages
quantities_comparable
same_quantity
problems
```

### Important interpretation

The audit is a **filter**, not ground truth.

Human review remains the final benchmark gate.

An audit failure means:

```text
inspect carefully
```

not automatically:

```text
automatically delete
```

Likewise, an audit pass does not prove a question is scientifically perfect.

---

# 9. Existing Benchmark Issues Found During Failure Inspection

The original benchmark exposed several concrete issues.

These are historical observations used to guide V2 construction.

## 9.1 `simple-192b22fb`

The question asked for a curved-ΛCDM/H0-related value, while the displayed gold chunk was a table concerning items such as:

```text
ΔNeff
SIDR
WZDR
DRMD
```

The gold evidence did not clearly match the requested curved-ΛCDM value.

This is a possible benchmark/gold-alignment issue rather than a straightforward retrieval failure.

It requires exact evidence review before deciding its final status.

---

## 9.2 `simple-579634ff`

This question asks for three explicit assumptions. The supporting passage states the relevant assumptions, including:

```text
local gravitational source is quiescent
black hole is non-rotating
universe is spatially flat on large scales
```

This is a useful example of a question that can be retrieval-hard while still being structurally valid.

Do not delete valid hard examples merely because the current retriever misses them.

---

## 9.3 `multi_hop-32126f6b`

The question effectively compared incompatible quantities, including H0 and contamination percentages.

Decision direction:

```text
remove / do not carry into a clean V2 benchmark
```

---

## 9.4 `multi_hop-a55a4306`

One passage provides values/notation around:

```text
page
eta
E = H/H0
```

Another provides:

```text
xi_ide
Q = xi_ide H rho_de
```

The pairing had a potentially repairable scientific relationship, but the original reference answer was malformed or over-specific.

Decision direction:

```text
repair / re-source
```

---

## 9.5 `multi_hop-3cafd9d7`

The question involved helium precision and D/H constraints.

The source pairing was potentially useful, but the reference answer overclaimed that helium was categorically more effective at ruling out models.

The issue is not necessarily the topic; it is the unsupported evaluative/causal wording.

Decision direction:

```text
repair wording/evidence
```

---

## 9.6 `multi_hop-3e7379ed`

This involved LBT helium calibration and D/H constraints.

The pairing may contain useful complementary evidence, but the broad causal conclusion in the answer was not cleanly grounded.

Decision direction:

```text
repair / re-source
```

---

## 9.7 `multi_hop-c1b11062`

The question tried to identify a common cosmological quantity across DM-DR tight coupling and a DM-DE interaction.

The second passage clearly contains:

```text
Q = xi_ide H rho_ide
```

but the displayed first passage did not clearly establish the corresponding counterpart.

The relationship therefore needed stronger sourcing.

Decision direction:

```text
repair / re-source
```

---

## 9.8 `temporal-a8985ff7`

The earlier/later passages did not track the same quantity or claim cleanly.

Decision direction:

```text
remove
```

---

## 9.9 `temporal-c49495fc`

The question asks about evolution of the Hubble-tension statistical significance, but the passages were generic introductory statements instead of a controlled earlier/later evidence pair.

This is not a meaningful temporal benchmark relationship.

Decision direction:

```text
remove or regenerate
```

---

## 9.10 `chain-505459d1`

The question concerned evidence supporting a claim about a model being the only one with a decelerated phase, while the displayed conclusion chunk focused on AIC/BIC/GDE/singularity-related material.

The later evidence did not clearly support the exact generated claim.

Decision direction:

```text
repair / re-source
```

---

## 9.11 `chain-e650cfbd`

The abstract explicitly stated a claim involving DES-DOVEKIE and a distance-ladder H0 determination. The figure caption supplied related details.

However, the generated question could already be answered from the abstract itself.

That violates the core chain requirement:

```text
abstract claim
        ↓
later evidence
        ↓
question needs later evidence
```

Decision direction:

```text
repair
```

---

# 10. Working Benchmark V2 Files

The benchmark versioning scheme now uses separate files.

Current important files:

```text
data/bench/questions.jsonl
```

Original v1 benchmark.

```text
data/bench/questions_v1_frozen.jsonl
```

Explicit frozen baseline copy.

```text
data/bench/questions_v2.jsonl
```

Working V2 benchmark copy that can be repaired without touching v1.

```text
data/bench/questions_v2_backup_before_repair.jsonl
```

Backup created before benchmark-repair changes.

```text
data/bench/audit.jsonl
```

Support-audit output.

```text
data/bench/v2_review_manifest.json
```

Manifest used to organize audit/retrieval-sufficiency review.

Do not confuse pilot files with the main V2 benchmark.

---

# 11. V2 Review Manifest

The accepted 27-question set was partitioned using audit status and Oracle-v2 sufficiency.

The review manifest recorded four broad groups:

```text
15 audit-passed + retrieval-sufficient
3  audit-failed  + retrieval-sufficient
5  audit-failed  + retrieval-insufficient
4  audit-passed  + retrieval-insufficient
```

An important finding was that the clean intersection:

```text
15 audit-passed
AND
retrieval-sufficient
```

was composed entirely of `SIMPLE` questions.

That means the existing 27-item benchmark did not contain a healthy clean training/evaluation mixture across difficult routing types.

This is another reason not to train Compass yet.

---

# 12. Why Compass Training Was Frozen

Compass is intended as the cheap learned routing component.

The conceptual design is:

```text
question only
    ↓
frozen small base model
    ↓
LoRA adapter + classification head
    ↓
route class
```

Compass must **not** see:

```text
answer
retrieved context
gold evidence
oracle labels inside the input
```

Otherwise the router leaks evaluation information and no longer represents a genuine pre-retrieval routing policy.

The current benchmark has only:

```text
27 accepted questions
```

and only:

```text
2 Oracle-v2 UNCERTAIN
```

plus substantial structural noise in multi-hop, temporal, and chain examples.

Training a LoRA adapter now would risk learning benchmark artifacts.

### Explicit gate

```text
Benchmark clean enough?       NO
Enough validated examples?    NO
Compass training?             DO NOT START
```

---

# 13. Week 2d: Structured Generation

The generic V2 generation work was expanded to require structured scientific metadata from the LLM.

For non-simple generation, a candidate is expected to contain approximately:

```json
{
  "question": "...",
  "reference_answer": "...",
  "passage_1_contribution": "...",
  "passage_2_contribution": "...",
  "joint_reason": "...",
  "same_quantity": true
}
```

The fields serve distinct roles:

### `question`

The natural-language benchmark question.

### `reference_answer`

The answer that the passages jointly support.

### `passage_1_contribution`

What passage 1 contributes that is necessary or materially useful.

### `passage_2_contribution`

What passage 2 contributes.

### `joint_reason`

Why the answer needs both evidence pieces rather than one.

### `same_quantity`

Used especially for comparison/temporal/conflicting structures to prevent accidental comparison of unrelated numerical or scientific quantities.

These fields make generation more auditable than asking the LLM for a question and answer alone.

---

# 14. Week 2d Structural Validation Rules

The V2 validation philosophy is intentionally conservative.

For multi-hop/chain:

```text
both passages must contribute
+
contributions must be explicit
+
joint reasoning must be explicit
+
question must not be answerable from one passage alone
```

For temporal/conflicting:

```text
same quantity/claim
+
compatible meaning
+
valid pair relationship
```

For simple questions:

```text
scientific content required
+
reject source trivia
+
reject citation-only questions
```

For all generated candidates:

```text
reference answer must be supported
```

Do not loosen these gates merely because candidate yield is low.

A low yield may indicate:

```text
insufficient genuinely related evidence in the corpus
```

which is itself useful information.

---

# 15. Bounded 429 / Provider Retry Handling

During large-ish generation attempts, Groq rate limits appeared.

The LLM client was adjusted so provider retries are bounded instead of potentially continuing indefinitely.

Current pattern in `src/atlasrag/llm.py` is approximately:

```python
OpenAI(...,max_retries=0)
```

with application-level retry configuration around:

```text
max_retries = config value, default about 2
retry_base_seconds = 1.0
retry_max_seconds = 4.0
```

The result is roughly:

```text
initial attempt
→ bounded retry
→ bounded retry
→ raise LLMRateLimitExceeded
```

The implementation retries relevant provider failures such as:

```text
RateLimitError
APIConnectionError
```

### Research/safety point

A rate-limited generation run must stop cleanly and report the failure.

Do not hide the failure by infinitely retrying.

Do not manufacture missing candidates after a rate-limit event.

Do not interpret an interrupted run as evidence of zero candidate availability.

---

# 16. Current Instrumentation Gap

The existing `LLMClient.stats` tracks approximately:

```python
{
    "calls":0,
    "prompt_tokens":0,
    "completion_tokens":0,
    "cache_hits":0
}
```

This is useful but still does **not** fully preserve:

```text
provider API calls
cache misses
retry attempts
RateLimitError count
APIConnectionError count
final rate-limit state
```

This matters because a logical LLM request is not necessarily one physical provider request.

For example:

```text
logical call = 1
cache hit = yes
provider calls = 0
```

or:

```text
logical call = 1
cache hit = no
provider calls = 3
```

because of retries.

Efficiency claims need these to be distinguishable.

### Historical pilot instrumentation

One recent pilot reported approximately:

```text
14 logical calls
15,939 cache-inclusive tokens
```

but per-run cache-hit/provider-call counts were not persisted in a way that allows honest reconstruction.

Therefore:

> Never infer exact provider-call counts retrospectively from that pilot.

Future generation runs should persist a machine-readable run summary with at least:

```text
logical_calls
provider_calls
cache_hits
cache_misses
prompt_tokens
completion_tokens
retry_attempts
rate_limit_errors
connection_errors
final_status
```

---

# 17. Why Generic Nearest-Neighbor Pairing Failed

The original neighbor approach was conceptually close to:

```python
sims=self.ix.emb @ self.ix.emb[i]
```

followed by choosing a semantically nearby passage, often from another paper.

This sounds reasonable, but semantic similarity answers:

```text
“Are these passages about similar things?”
```

while benchmark construction requires:

```text
“Can these passages support a joint scientific question that genuinely needs both?”
```

Those are different tasks.

Observed failure classes included:

```text
related topic, incompatible quantity
related topic, one passage unnecessary
related topic, duplicate evidence
related topic, abstract already answers chain question
same keyword, but no temporal relationship
same broad field, but no specific cross-paper relationship
```

This is why Week 2 shifted from:

```text
nearest neighbor → LLM
```

to:

```text
dense + BM25 candidate retrieval
        ↓
scientific signal filtering
        ↓
specific anchor matching
        ↓
duplicate rejection
        ↓
type-specific structural checks
        ↓
LLM generation
        ↓
validation/audit
```

---

# 18. Deterministic Pair Sourcing: Current V2 Direction

Relevant implementation:

```text
src/atlasrag/bench/generate_v2.py
```

Supporting files:

```text
src/atlasrag/bench/generate.py
scripts/gen_questions_v2.py
tests/test_bench_v2.py
```

The selector now uses the existing index rather than introducing a separate expensive retrieval architecture.

The index already provides:

```text
dense embeddings
BM25
chunk text
paper_id
section
```

and APIs such as:

```python
dense(qvec,k)
bm25(query,k)
```

The candidate-pool logic can therefore combine both semantic and lexical/scientific evidence.

---

# 19. Candidate-Pool Construction

The current conceptual pipeline is:

```text
source chunk
    ↓
Dense candidate pool
    +
BM25 candidate pool
    ↓
union / deduplicate
    ↓
scientific signal overlap
    ↓
specific anchor match
    ↓
near-duplicate rejection
    ↓
type-specific pair gates
    ↓
LLM generation
```

### Why use both dense and BM25?

Dense retrieval is good at semantic similarity.

BM25 can recover exact scientific terms, symbols, named surveys, acronyms, and identifiers that may matter even when the surrounding language differs.

The union provides a broader candidate pool without requiring a second expensive learned model.

---

# 20. Scientific Signal Extraction

The selector extracts conservative scientific signals from chunk text.

Signals can include:

```text
symbols
quantities
acronyms
named surveys
model names
parameter names
datasets
cosmological observables
scientific terms
numbers attached to scientific concepts
```

Examples seen in the project context include:

```text
H0
DESI
BAO
Neff
Ωm
ΛCDM
wCDM
YHe
D/H
Pantheon+
CMB
```

The goal is **not** to construct a giant hand-written cosmology dictionary.

The selector should generalize beyond the current 30-paper corpus.

Generic topical words such as:

```text
cosmology
model
paper
result
universe
```

must not be sufficient evidence for a pair.

---

# 21. Specific Scientific Anchors

A second filtering layer looks for more precise shared anchors.

These can include:

```text
acronym
parameter symbol
model symbol/name
observable identifier
specific survey/dataset identifier
```

For cross-paper pairing, the current direction requires something like:

```text
shared scientific signals
+
shared specific scientific anchor
```

This is deliberately stricter than generic semantic similarity.

Example:

```text
A mentions H0 + BAO + DESI
B mentions H0 + DESI + a specific model constraint
```

is more promising than:

```text
A mentions cosmology + galaxy
B mentions cosmology + galaxy
```

The second pair has topical overlap but no demonstrated specific relationship.

---

# 22. Near-Duplicate Rejection

Two chunks can be highly similar while still being poor benchmark pairs.

Example:

```text
A = definition of H0
B = near-identical definition of H0
```

A multi-hop benchmark built from these does not test multi-hop reasoning.

Therefore the selector penalizes or rejects near-duplicate pairs.

The desired pair has:

```text
shared anchor
+
shared scientific context
+
different information roles
```

not:

```text
shared anchor
+
identical evidence
```

---

# 23. Multi-Hop Pair Requirements in the Current Selector

A valid pair should satisfy:

```text
same scientific object/topic
+
shared scientific signals
+
shared specific anchor
+
non-duplicate evidence
+
complementary roles
```

Then the generated question should satisfy:

```text
Passage 1 contributes something specific
Passage 2 contributes something specific
The final answer genuinely needs both
```

The validator now checks for missing passage contributions and a missing joint reason.

This prevents the LLM from writing a nice-looking question around two passages when only one is actually necessary.

---

# 24. Temporal Pair Sourcing in the Current Direction

Temporal pairing is more difficult because dates alone are not enough.

The intended intermediate representation is:

```text
paper
publication date
chunk
scientific signals
section role
```

Then candidate construction looks like:

```text
earlier chunk
+
later chunk
+
shared precise scientific relationship
```

The current temporal gates also emphasize evidence-bearing sections and result/update cues.

Good sections can include:

```text
Results
Analysis
Discussion
Observations
Measurements
Methods
Conclusions
```

depending on what the passage is actually doing.

A generic introduction is normally weak temporal evidence.

A valid temporal question should reveal an actual:

```text
change
refinement
updated measurement
revised constraint
new interpretation
```

rather than simply saying that two papers discuss the same topic.

---

# 25. Chain Sourcing in the Current Direction

The chain source is same-paper by design.

The basic process is:

```text
paper abstract
      ↓
identify a concrete abstract claim
      ↓
search later sections in same paper
      ↓
rank by scientific overlap
      ↓
require evidence-bearing section
      ↓
ensure later passage adds substantive evidence
      ↓
LLM generates question
```

The later section should contain something the abstract does not fully provide, such as:

```text
measurement
method
observational evidence
quantitative result
parameter constraint
analysis detail
```

This makes the chain test genuinely about following evidence from claim to support.

---

# 26. Current Pair-Sourcing Implementation Details

The latest reported implementation in `generate_v2.py` includes concepts/functions such as:

```text
scientific_signals()
specific_scientific_signals()
_signal_similarity()
_has_temporal_evidence()
assess_cross_paper_pair()
assess_chain_pair()
_candidate_pool()
_rank_cross_paper_candidates()
_rank_chain_candidates()
_choose_neighbor()
```

The current candidate pool is formed by combining dense and BM25 results.

The selector then ranks candidates rather than randomly choosing a semantically related neighbor.

This is an important methodological change because benchmark generation becomes more deterministic and more inspectable before LLM calls are spent.

---

# 27. Pair-Sourcing Tests

Deterministic tests were added using synthetic chunks, because these checks should not consume provider quota.

The latest reported suite reached:

```text
55 passed in 3.99s
```

Tests cover areas including:

```text
structured generation
missing passage contributions
identical passage roles
comparison without shared quantity
one-passage-answer rejection
source-framing rejection
citation trivia rejection
temporal validation
chain validation
shared scientific signals
unrelated pairs
complementary pairs
near-duplicate rejection
temporal date requirements
evidence-bearing sections
chain same-paper requirements
candidate-pool ranking
bounded 429 handling
```

Always rerun the suite against the current checkout before treating this count as current.

The count is a historical reported checkpoint, not a substitute for a fresh test run.

---

# 28. Latest Pair Pilot: `pairpilot`

Historical pilot file:

```text
data/bench/questions_v2_pairpilot.jsonl
```

Result:

```text
1 multi-hop candidate
```

Manual outcome:

```text
rejected
```

Reason:

```text
broad-topic pairing
```

The candidate was semantically related but did not satisfy the stronger scientific pair relationship expected of a multi-hop benchmark.

This was a useful result because it demonstrated that the stricter gates were preventing an obviously weak pair from becoming part of V2.

---

# 29. Latest Pair Pilot 2: `pairpilot2`

Historical pilot file:

```text
data/bench/questions_v2_pairpilot2.jsonl
```

Result:

```text
1 multi-hop candidate
0 chain candidates
```

The surviving multi-hop candidate was reported as structurally credible because:

```text
both excerpts concern baryon-density constraints
one excerpt provides direct YHe information
another provides BAO/CMB correlation behavior
```

However, the candidate remained:

```text
candidate
```

not:

```text
accepted
```

Human review is still required.

Reported rejection counts from this pilot were:

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

These counts are useful diagnostic evidence about the selector, but they do not prove that every rejected pair was scientifically invalid. Representative manual review is still necessary before changing thresholds.

---

# 30. Stale Pilot Warning

Some older pilot files were generated before the latest structural validation and deterministic pair sourcing.

For example, stale artifacts included candidates with stored values such as:

```text
same_quantity = false
```

that would now be rejected by the current comparison-pair logic.

Therefore:

> **Do not use stale pilot artifacts as evidence that the current generator accepts those structures.**

For current behavior, use:

```text
current repository code
+
current tests
+
fresh tiny pilot
```

Historical pilot files are useful for chronology/debugging only.

---

# 31. Rate Limiting During Pair Generation

The newest pair pilot did not scale to a large run.

Groq `429` rate limits interrupted further multi-hop/chain generation.

The bounded retry changes caused the generator to stop cleanly instead of hanging indefinitely.

A recent run reported approximately:

```text
14 logical calls
15,939 cache-inclusive tokens
```

but provider-call/cache-hit counts were not persisted in a sufficiently detailed machine-readable record.

Therefore the correct statement is:

```text
14 logical calls were observed
```

not:

```text
14 provider API calls
```

or any other retrospective provider-call estimate.

---

# 32. What the Low Pair Yield Means

Low multi-hop/chain yield should **not** automatically lead to weaker validation.

There are at least three possible explanations:

```text
A. selector too strict
B. corpus has few genuine evidence pairs
C. generator/provider budget is too constrained
```

The current evidence does not justify assuming A.

Indeed, some earlier accepted questions were clearly structurally weak, so strong filtering is justified.

The appropriate workflow is:

```text
measure rejection reasons
        ↓
inspect representative examples
        ↓
determine false-negative vs correct rejection
        ↓
only then modify the gate
```

Any threshold change should add or update a regression test and be recorded as a methodological change.

---

# 33. Benchmark Repair Decisions: Current Working Guidance

The current guidance derived from the audited 27 is:

## Clearly remove from a clean V2 benchmark

```text
multi_hop-32126f6b
temporal-a8985ff7
```

## Repair or re-source

```text
multi_hop-0760df1d
multi_hop-a55a4306
multi_hop-3cafd9d7
multi_hop-3e7379ed
multi_hop-c1b11062
chain-505459d1
chain-e650cfbd
```

## Potentially valid but retrieval-hard

```text
simple-579634ff
```

and possibly:

```text
simple-192b22fb
```

subject to exact evidence review because its displayed gold passage looked suspicious.

These are working decisions, not immutable labels.

Every final V2 decision must be based on the actual current benchmark file and evidence.

---

# 34. V1 vs V2: Keep the Distinction Explicit

A new AI agent must understand these are different layers.

## V1

```text
data/bench/questions.jsonl
```

The original accepted benchmark used for the historical run-1 results.

Its value is reproducibility.

Do not silently edit it.

## V1 frozen copy

```text
data/bench/questions_v1_frozen.jsonl
```

Protection against accidental rewriting.

## V2 working benchmark

```text
data/bench/questions_v2.jsonl
```

The intended repaired/improved benchmark.

Its value is methodological quality, not continuity with the original question generation artifacts.

## Oracle v1

Historical labeling implementation.

Useful for documenting how the original results were produced.

## Oracle v2

Current preferred labeling logic for future work.

Stores all ladder recalls and distinguishes retrieval insufficiency from the selected routing class.

---

# 35. Exact Commands for Week 2 Work

The project uses a `src/` layout.

In PowerShell, set:

```powershell
$env:PYTHONPATH="src"
```

### Run tests

```powershell
python -m pytest -q
```

### Generate/review original benchmark history

Original review command:

```powershell
python scripts/review_questions.py --batch 20
```

### Oracle v1

```powershell
python scripts/label_oracle.py --split test --status accepted
```

### Oracle v2 / v2 labels

Inspect the current scripts first, then use the repository's v2 labeling command rather than inventing a new one. The implementation lives in:

```text
src/atlasrag/bench/oracle_v2.py
```

### Support audit

```powershell
python scripts/audit_questions.py --status accepted --split test
```

### Label statistics

```powershell
python scripts/label_stats.py --split test
```

Remember that this can include generated/rejected candidate inventory depending on script semantics. Always distinguish:

```text
candidate count
```

from:

```text
accepted labelled count
```

### Failure inspection

```powershell
python scripts/inspect_failures.py --split test
```

Use the current script's exact CLI options if they have changed.

### Candidate V2 generation

Historical pilot pattern:

```powershell
python scripts/gen_questions_v2.py --split test --per-type 2 --types multi_hop chain --attempts 4 --out data/bench/questions_v2_pairpilot.jsonl
```

Do not blindly rerun a stale pilot filename.

For a fresh pilot, use a new output path and make the run size intentionally tiny.

---

# 36. Fresh-Pilot Workflow for a New AI Agent

When continuing Week 2, the correct order is:

```text
1. inspect current git state
2. run tests
3. inspect current generate_v2.py
4. inspect validate.py
5. inspect test_bench_v2.py
6. inspect llm.py
7. inspect current benchmark files
8. inspect current audit/manifest
9. understand current pair selector
10. only then edit code
11. rerun tests
12. make a tiny fresh pilot
13. manually inspect every survivor
14. record rejection reasons
15. only then expand generation
```

Do not begin by generating hundreds of questions.

The provider budget should be spent only after deterministic selection and structural validation have shown that the pipeline is producing plausible candidates.

---

# 37. Required Current Repository Checks

The latest handoff explicitly requires checking the actual repository rather than trusting prior agent reports.

Repository:

```text
https://github.com/prathamkariya/AtlasRAG
```

Verify:

```text
current branch
current commit
current commit history
current generate_v2.py
current generate.py
current validate.py
current test_bench_v2.py
current llm.py
current experiments.py
current oracle_v2.py
current .gitignore
```

Also check local status:

```powershell
git status
```

and history:

```powershell
git log --oneline --decorate -10
```

A previous repository inspection showed an apparent mismatch between the visible one-commit history and later-looking code. Resolve that discrepancy from the actual current tree/history.

Do not invent commit history.

---

# 38. Files That Must Remain Untouched During Benchmark Repair

Unless a future experiment explicitly requires a new controlled version, preserve these:

```text
data/bench/questions.jsonl

data/bench/questions_v1_frozen.jsonl

results/run1/

src/atlasrag/bench/oracle_v2.py

src/atlasrag/bench/experiments.py
```

`results/run1/` is the frozen development/control checkpoint.

Changing those files retroactively would make it harder to interpret the historical results.

---

# 39. Current Week 2 Test-Safety Rule

Do not spend provider quota on deterministic validation.

Tests for:

```text
scientific signal overlap
anchor matching
near-duplicate rejection
same-quantity constraints
temporal gates
chain same-paper constraints
passage contribution requirements
numeric compatibility
```

should use synthetic fixtures or mocks.

Only genuine generation pilots should consume Groq calls.

---

# 40. How to Evaluate a New Benchmark Candidate

Every candidate should be manually inspected using this checklist.

### Question validity

Ask:

```text
Is this a meaningful scientific question?
```

Not merely:

```text
Can I parse the sentence?
```

### Passage necessity

Ask:

```text
Does passage 1 contribute something required?
Does passage 2 contribute something required?
```

For multi-hop/temporal/conflicting/chain, a “decorative” second passage is a failure.

### Scientific relationship

Ask:

```text
Do the passages share a precise scientific relationship?
```

Not merely the same broad topic.

### Reference-answer support

Check every substantive claim in the reference answer against the supplied evidence.

Do not accept unsupported conclusions.

### Numeric correctness

For comparisons, verify:

```text
same quantity
compatible units
compatible definitions
compatible measurement meaning
```

### Temporal validity

Verify:

```text
earlier evidence
later evidence
same claim/quantity
actual update/change/refinement
```

### Chain validity

Verify:

```text
same paper
abstract claim
later evidence
later evidence adds something substantive
question requires later evidence
```

### Simple validity

Verify the question is about scientific content rather than document trivia.

---

# 41. What Not to Do During Week 2

Do not:

```text
train Compass now
```

because the benchmark is not clean or large enough.

Do not:

```text
replace BGE-small immediately
```

because benchmark construction is currently the more important uncertainty.

Do not:

```text
increase generation scale just because survivor yield is low
```

because a low-yield but clean generator is more useful than a high-yield noisy generator.

Do not:

```text
weaken validation thresholds without rejection analysis
```

because this can reintroduce the exact benchmark problems Week 2 is fixing.

Do not:

```text
modify run1 outputs
```

because they are the historical baseline.

Do not:

```text
call stale pilots “current behavior”
```

because some were generated under earlier code.

Do not:

```text
invent provider-call counts from cache-inclusive logical statistics
```

because instrumentation does not currently support that inference.

---

# 42. Current Engineering Priority at the End of Week 2

The latest engineering handoff identified the following sequence:

```text
verify current repository
        ↓
inspect current V2 selector
        ↓
diagnose chain sourcing
        ↓
verify/improve instrumentation
        ↓
tiny chain-only pilot
        ↓
review outcome
        ↓
only then consider additional benchmark regeneration
```

The chain path is currently the weakest unresolved part because the latest deterministic selector has not yet produced a reviewed chain survivor.

This does **not** prove that the chain concept is impossible.

It means the current evidence is insufficient to scale chain generation confidently.

---

# 43. Recommended Immediate Agent Task

A new coding agent should first report an engineering plan rather than immediately editing files.

The first response should establish:

```text
current commit
current branch
fresh test result
relevant source files verified
```

Then list only the files that actually need changes.

A useful table format is:

| File | Exact change | Reason | Risk |
|---|---|---|---|
| `path/to/file.py` | function/logic change | benchmark or instrumentation reason | low/medium/high |

Then explicitly confirm the historical files that remain untouched.

Then describe:

```text
exact function(s)
logic change
expected behavior
failure modes
tests to add/update
```

This prevents broad rewrites and accidental regression.

---

# 44. Research Integrity Requirements

The benchmark is part of the scientific contribution, not just test data.

Therefore every benchmark change should preserve:

```text
versioning
provenance
reproducibility
manual reviewability
clear inclusion/exclusion criteria
```

When a candidate is rejected, preserve enough information to explain why.

Useful rejection labels include:

```text
pair_no_shared_specific_signal
pair_no_shared_scientific_signal
pair_no_evidence_section
answer_not_supported
not_all_passages_needed
missing_joint_reason
missing_passage_contributions
different_quantity
generator_returned_none
```

Do not collapse all failures into a single “bad candidate” category.

Failure-mode counts are valuable evidence for improving the benchmark generator.

---

# 45. Interpreting Benchmark Size

The test benchmark contains only:

```text
27 accepted questions
```

This is enough for a development baseline and paired diagnostic work, but not enough to support strong broad-generalization claims.

The current clean intersection of audited + retrieval-sufficient questions is even smaller.

Therefore future reporting should use language such as:

```text
on this evaluated benchmark
```

rather than implying that the measured route behavior generalizes to all scientific QA workloads.

The benchmark should eventually grow, but quality comes before scale.

---

# 46. Relationship to Week 1

Week 1 established the retrieval infrastructure:

```text
corpus
→ parsing
→ chunking
→ embeddings
→ dense retrieval
→ BM25
→ hybrid retrieval
→ reranking
→ LLM client
→ API
→ tests
```

Week 2 uses that infrastructure as a measurement instrument.

In particular, benchmark generation now benefits from the same retrieval primitives already implemented for the application.

This is preferable to introducing a disconnected benchmark-generation retrieval stack unless an experiment later proves that a separate mechanism is required.

---

# 47. Relationship to Week 3 / Compass

Compass should come only after the benchmark has a usable training/evaluation distribution.

The planned transition is:

```text
V2 benchmark validation
        ↓
train-set construction
        ↓
Oracle-v2 sufficient labels
        ↓
class-balance inspection
        ↓
Compass training
        ↓
Compass retrieval-only evaluation
```

Do not jump directly from:

```text
27 test questions
```

to:

```text
LoRA training
```

The training set should be independently generated and should not reuse the test questions as training instances.

---

# 48. Final Week 2 Snapshot

The current state of the benchmark work is:

```text
Original generated candidates        94
Original accepted test questions     27
Original rejected candidates         67

Oracle v1:
  SIMPLE      11
  MULTI_HOP    5
  UNCERTAIN   11
  insufficient 9

Oracle v2:
  SIMPLE      18
  MULTI_HOP    7
  UNCERTAIN    2
  insufficient 9

Support audit:
  pass        19/27
  flagged      8/27

Latest pair-sourcing test checkpoint:
  55 tests passed

Latest pairpilot:
  1 multi-hop generated
  manually rejected

Latest pairpilot2:
  1 multi-hop candidate
  0 chain candidates
  multi-hop candidate remains unaccepted

Rate limit:
  Groq 429 observed
  bounded handling implemented

Compass:
  not trained

Run 1:
  frozen
```

---

# 49. The Core Lesson of Week 2

The main Week 2 lesson is:

> **A benchmark that merely looks plausible is not enough. It must establish that the question is valid, that the evidence is sufficient, that all claimed passages contribute when required, and that the intended routing class reflects the information need rather than retrieval failure.**

The project therefore moved from:

```text
“generate more questions”
```

toward:

```text
construct trustworthy evidence relationships first
```

That shift is important for the research credibility of AtlasRAG.

---

# 50. Compact New-Agent Handoff Prompt

Paste the following into a new AI coding chat when continuing from this file:

```text
You are continuing AtlasRAG Week 2 benchmark construction.

Repo:
https://github.com/prathamkariya/AtlasRAG

Read the project context before editing anything.

Current benchmark situation:
- Original v1 test benchmark: 27 accepted questions.
- Preserve data/bench/questions.jsonl and data/bench/questions_v1_frozen.jsonl.
- Preserve results/run1/.
- Current Oracle v2 labels over the 27 are approximately SIMPLE=18, MULTI_HOP=7, UNCERTAIN=2, with 9 questions retrieval-insufficient under the exact gold-evidence metric.
- Support audit: 19/27 pass, 8/27 flagged.
- The audited failures include weak multi-hop, temporal, and chain relationships.
- Do not train Compass yet.
- Do not replace the embedding model yet.

Current V2 direction:
source chunk
→ dense + BM25 candidate pools
→ union
→ scientific signal overlap
→ specific scientific anchor matching
→ near-duplicate rejection
→ type-specific structural gates
→ structured LLM generation
→ validation
→ support audit
→ human review

Relevant code:
- src/atlasrag/bench/generate_v2.py
- src/atlasrag/bench/generate.py
- src/atlasrag/bench/validate.py
- tests/test_bench_v2.py
- scripts/gen_questions_v2.py
- src/atlasrag/llm.py
- src/atlasrag/bench/oracle_v2.py

Latest reported test checkpoint:
55 passed.
Run pytest against the actual current checkout before trusting this number.

Latest pair pilot:
- pairpilot: 1 multi-hop candidate, manually rejected as broad-topic.
- pairpilot2: 1 multi-hop candidate, 0 chain candidates; multi-hop candidate remains unaccepted.
- Groq 429 stopped further generation; bounded retry behavior now exists.

Important stale-pilot warning:
Older pilot files may contain candidates that current validation would reject. Do not treat them as current behavior.

Current engineering priority:
1. verify repository state/history;
2. run tests;
3. inspect current pair selector;
4. diagnose chain sourcing;
5. verify instrumentation for logical/provider calls, cache hits/misses, retries, and rate-limit events;
6. run a tiny fresh chain-focused pilot;
7. manually review every survivor;
8. only then consider further benchmark generation.

Do not relax validation merely to increase yield.
Do not overwrite v1 or run1.
Do not invent provider-call counts from logical-call/token statistics.

Before editing, report:
A. current repository state
B. exact files that need changes
C. files that must remain untouched
D. exact implementation plan
E. tests to add/update
F. research-safety risks
```

---

# 51. Week 2 Exit Criteria

Week 2 should be considered complete only when the following are true:

```text
[ ] v1 benchmark frozen and reproducible
[ ] v1 Oracle results preserved
[ ] Oracle v2 available
[ ] retrieval insufficiency separated from routing class
[ ] support audit available
[ ] V2 generation uses structured scientific evidence fields
[ ] multi-hop requires both passages
[ ] temporal requires genuine same-quantity/claim relationship
[ ] chain requires later same-paper evidence
[ ] incompatible numerical comparisons are rejected
[ ] deterministic pair sourcing uses dense + BM25 + scientific signals
[ ] specific anchors are enforced for cross-paper pairs
[ ] near-duplicates are rejected
[ ] bounded provider retries are tested
[ ] current test suite passes
[ ] at least one fresh high-quality multi-hop/temporal/chain path has been manually reviewed before scaling
[ ] benchmark versioning is preserved
[ ] Compass remains frozen until training data quality is sufficient
```

The final checkbox is intentionally conservative. It is better to end Week 2 with an incomplete benchmark than to train the router on invalid evidence relationships.

---

# 52. File Map for Week 2

```text
DATA / BENCHMARK
----------------
data/bench/questions.jsonl
    original v1 benchmark

data/bench/questions_v1_frozen.jsonl
    frozen v1 copy

data/bench/questions_v2.jsonl
    working V2 benchmark

data/bench/questions_v2_backup_before_repair.jsonl
    pre-repair backup

data/bench/audit.jsonl
    support-audit output

data/bench/v2_review_manifest.json
    V2 review grouping

GENERATION
----------
src/atlasrag/bench/generate.py
    generic generation helpers / evidence-section detection

src/atlasrag/bench/generate_v2.py
    structured generation + deterministic pair sourcing

scripts/gen_questions_v2.py
    V2 generation CLI

VALIDATION / ORACLE
-------------------
src/atlasrag/bench/validate.py
    candidate validation logic

src/atlasrag/bench/oracle_v2.py
    full-ladder recall + cheapest-within-epsilon labeling

scripts/audit_questions.py
    support audit

scripts/label_stats.py
    label/candidate statistics

EXPERIMENTS
-----------
src/atlasrag/bench/experiments.py
    experiment mapping; preserve historical mappings

results/run1/
    frozen historical baseline

TESTS
-----
tests/test_bench_v2.py
    V2 generation/validation/pair sourcing/retry tests

LLM
---
src/atlasrag/llm.py
    provider client, cache, token statistics, bounded retries
```

---

# 53. Final Instruction to Future Agents

Treat this Week 2 file as a methodological record, not as a command to blindly repeat every historical step.

The project has already learned from the failed benchmark structures.

The correct behavior is:

```text
inspect evidence
→ preserve what is valid
→ repair what is repairable
→ remove what is structurally invalid
→ regenerate only when needed
→ test deterministically
→ spend LLM quota sparingly
→ preserve all historical results
```

The benchmark is not merely a collection of questions. It is the experiment's measurement instrument.

A cleaner measurement instrument is more valuable than a larger but noisy dataset.
