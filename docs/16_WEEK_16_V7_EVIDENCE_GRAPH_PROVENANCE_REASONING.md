# AtlasRAG — Week 16: V7 Evidence Graph & Provenance-Aware Scientific Reasoning

## 1. Purpose

Week 15 moved AtlasRAG from plain prose-oriented retrieval toward explicit scientific evidence structures:

```text
prose
table
equation
numeric evidence
temporal structure
```

That creates an important next question.

Even if the system can retrieve the right evidence units, the answer may still require understanding how those units are related.

For example:

```text
Paper A
  ↓
defines parameter X

Paper B
  ↓
measures X

Paper C
  ↓
compares X with Y
```

A flat top-k retrieval result does not explicitly represent this chain.

Similarly:

```text
Paper A → earlier estimate
Paper B → later estimate
Paper C → conflicting estimate
```

The retrieval system may find all three passages but leave the relationship between them implicit.

V7 therefore explores whether scientific evidence should be represented not only as:

```text
independent evidence units
```

but also as:

```text
connected evidence with explicit provenance and relationships
```

The core transition is:

```text
V1
question-aware retrieval

        ↓

V2
claim/evidence verification

        ↓

V3
retrieval-state-aware failure prediction

        ↓

V4
larger benchmark

        ↓

V5
cross-domain transfer

        ↓

V6
scientific-structure-aware evidence

        ↓

V7
evidence graph + provenance-aware reasoning
```

The objective is not to build a giant knowledge graph.

The objective is to test one narrow scientific hypothesis:

> **Can explicit relationships between evidence units improve retrieval completeness, multi-hop evidence acquisition, temporal/conflict reasoning, and citation provenance under controlled RAG experiments?**

Do not assume the answer is yes.

A graph can also introduce:

```text
extraction errors
spurious edges
higher latency
larger storage
query expansion noise
```

The experiment must establish whether the additional structure is worth it.

---

# 2. Why V7 follows V6

V6 answers approximately:

```text
Does the type of evidence matter?
```

V7 asks:

```text
Does the relationship between evidence units matter?
```

These are different problems.

Consider:

```text
table → parameter/value

equation → defines parameter

paragraph → interprets parameter

later paper → updates parameter
```

V6 can make each object easier to retrieve.

V7 asks whether the system can explicitly connect:

```text
equation
   ↓ defines
parameter
   ↓ measured_in
table
   ↓ interpreted_by
result paragraph
   ↓ updated_by
later paper
```

This is particularly relevant for question types such as:

```text
MULTI_HOP
TEMPORAL
CONFLICTING
CHAIN
```

A genuine multi-hop question often depends on relationships, not only similarity.

Therefore V7 should be motivated by the final V6 failure taxonomy.

Do not implement graph reasoning merely because graphs are interesting.

The first task is:

```text
inspect V6
↓
identify relationship-heavy failures
↓
confirm the bottleneck
↓
freeze V6
↓
design the smallest graph experiment that directly tests it
```

If V6 shows no meaningful relationship-related failure class, V7 may be deferred.

---

# 3. V7 primary research question

Primary question:

> **Can an evidence graph that explicitly represents relationships among scientific evidence units improve retrieval and provenance-aware answering compared with a strong structure-aware retrieval baseline?**

Secondary questions:

```text
1. Does graph expansion improve genuine multi-hop retrieval?

2. Does explicit temporal linkage improve temporal evidence retrieval?

3. Can contradiction edges improve conflicting-evidence retrieval?

4. Does provenance become more complete and precise?

5. Does graph-assisted retrieval reduce retrieval-state failures?

6. How much graph construction error can the system tolerate?

7. Does graph assistance outperform simple top-k retrieval under the same context budget?

8. Which graph relationships provide the largest marginal improvement?

9. Can the graph be useful without requiring a large generative model?

10. Does the benefit transfer to unseen papers/domains?
```

These are hypotheses.

They must not be written as results before measurement.

---

# 4. V7 conceptual architecture

The baseline after V6 is approximately:

```text
Question
   ↓
retrieval
   ↓
structured evidence units
   ↓
reranking
   ↓
context
   ↓
answer
```

V7 introduces explicit relations:

```text
Question
   ↓
initial retrieval
   ↓
evidence nodes
   ↓
graph traversal / graph reranking
   ↓
related evidence
   ↓
evidence set
   ↓
answer
   ↓
citation verification
```

More explicitly:

```text
                 Question
                    |
                    v
             Initial retrieval
                    |
                    v
              Seed evidence
                    |
                    v
            Evidence graph
          /        |         \
       defines   supports   precedes
         |         |          |
         v         v          v
      related   related     related
      evidence  evidence    evidence
          \        |        /
           \       |       /
                final
             evidence set
                    |
                    v
                 Answer
                    |
                    v
             V2 verification
```

The important design principle is:

```text
graph = retrieval aid
```

not:

```text
graph = unquestionable truth
```

Every graph-derived edge should retain provenance and confidence.

---

# 5. V7 independent variable

The clean independent variable is:

```text
evidence relationship / graph-assisted retrieval
```

Where feasible, freeze:

```text
benchmark
corpus
answer model
answer prompt
generation settings
embedding model
reranker model
chunking / structure representation
evaluation definitions
```

A first experiment matrix can be:

```text
R0
V6 baseline retrieval

R1
graph node retrieval only

R2
one-hop graph expansion

R3
relation-aware reranking

R4
relation-specific expansion

R5
combined graph-assisted retrieval
```

Do not begin with R5.

The goal is to determine:

```text
which graph mechanism causes any observed improvement
```

---

# 6. What is an evidence graph?

For AtlasRAG, the graph should be narrowly defined.

A node represents a scientific evidence object.

Possible nodes:

```text
PAPER
SECTION
PROSE_BLOCK
TABLE
TABLE_ROW
EQUATION
FIGURE_CAPTION
PARAMETER
VALUE
UNIT
METHOD
OBSERVATION
CLAIM
```

An edge represents a relationship that can be useful during retrieval or provenance analysis.

Possible edges:

```text
CONTAINS
DEFINES
REPORTS
SUPPORTS
REFERS_TO
USES_METHOD
HAS_VALUE
HAS_UNIT
PRECEDES
UPDATES
CONTRADICTS
COMPARES_WITH
DERIVED_FROM
```

Do not implement every edge immediately.

A smaller schema is preferable.

---

# 7. Minimum viable V7 graph

The first graph should probably contain only relationships that directly affect the current benchmark.

A reasonable minimum is:

```text
EVIDENCE
PARAMETER / ENTITY
CLAIM
PAPER
```

with edges such as:

```text
paper → contains → evidence

evidence → mentions → parameter

evidence → supports → claim

claim → cites → evidence

paper A → precedes → paper B

claim A → conflicts_with → claim B
```

The exact node/edge schema must be derived from actual V6 failures.

Do not create a large ontology before the benchmark demonstrates the need.

---

# 8. Provenance is central

A graph edge should not exist as an unexplained fact.

It should retain provenance.

For example:

```json
{
  "source_node":"claim-123",
  "edge":"supports",
  "target_node":"table-044",
  "source_paper":"paper-17",
  "source_page":8,
  "source_span":"...",
  "method":"deterministic",
  "confidence":0.91
}
```

The exact schema should match repository conventions.

The important rule is:

```text
every important graph assertion
↓
must be traceable to source evidence
```

This prevents the graph from becoming an opaque secondary knowledge base.

---

# 9. Graph provenance vs answer citations

These are related but different.

Graph provenance answers:

```text
Why does this edge exist?
```

Answer citation answers:

```text
Which source supports this answer claim?
```

A good V7 system should preserve both.

Conceptually:

```text
source paper
   ↓
evidence node
   ↓
graph edge
   ↓
retrieved evidence path
   ↓
answer claim
   ↓
citation
```

This creates a stronger provenance chain than:

```text
question
   ↓
top-k chunks
   ↓
answer
```

Do not claim citation improvement merely because graph metadata exists.

Measure citation quality directly.

---

# 10. Why multi-hop questions are the first target

Multi-hop questions naturally require multiple evidence units.

For example:

```text
Evidence A:
defines a parameter

Evidence B:
reports its measured value

Evidence C:
compares it with another result
```

A flat retriever can retrieve:

```text
A
B
C
```

without understanding that they form a useful chain.

A graph can potentially provide:

```text
A
 ↓ defines
X
 ↓ measured_in
B
 ↓ compared_in
C
```

The graph therefore offers a possible mechanism for structured evidence acquisition.

This is a hypothesis to test.

---

# 11. Temporal reasoning target

Temporal questions can also benefit from explicit relations.

Example:

```text
Paper A
2021
reports estimate X

      ↓ PRECEDES

Paper B
2024
updates estimate X
```

The question may ask:

```text
How did estimate X change over time?
```

Simple semantic retrieval may find both papers.

The graph can encode:

```text
A → PRECEDES → B
```

and:

```text
A → REPORTS → X = value_1

B → REPORTS → X = value_2
```

This creates an evidence path:

```text
value_1
   ↓
earlier estimate
   ↓
later estimate
   ↓
value_2
```

Do not infer temporal order from filenames or arbitrary index order.

Use explicit metadata:

```text
publication date
version date
experiment date
observation date
```

depending on the question.

---

# 12. Conflict reasoning target

Conflict is another graph-friendly structure.

Example:

```text
Claim A:
estimate = 67.4 ± 1.2

Claim B:
estimate = 73.0 ± 1.0
```

Potential relation:

```text
Claim A → CONFLICTS_WITH → Claim B
```

But the edge must not be created merely because:

```text
numbers differ
```

The system should consider:

```text
same quantity
same units
same or comparable condition
same observable
relevant context
```

A difference in unrelated quantities is not a contradiction.

This is an important benchmark-quality safeguard.

---

# 13. Claim-level graph nodes

V2 already introduced claim-level verification.

V7 can reuse that conceptual layer.

For example:

```text
Question

↓ retrieval

Evidence nodes

↓ graph relations

Claim candidates

↓ verification

SUPPORTED
PARTIALLY_SUPPORTED
UNSUPPORTED
```

This means V7 does not replace V2.

Instead:

```text
V6
better evidence representation

+

V7
better evidence relationships

+

V2
claim-level verification
```

can eventually form a stronger provenance pipeline.

---

# 14. Do not make V7 an answer-generation experiment first

The first V7 experiment should remain retrieval-centric.

Measure:

```text
Did the graph improve recovery of required evidence?
```

before asking:

```text
Did the LLM write a better answer?
```

This isolates the mechanism.

Only after retrieval gains are established should end-to-end answer evaluation be expanded.

---

# 15. Graph construction strategies

There are several ways to construct edges.

### Strategy A — deterministic rules

Use:

```text
metadata
section structure
citations
explicit identifiers
equation references
table/figure references
publication dates
```

Advantages:

```text
cheap
reproducible
interpretable
```

Disadvantages:

```text
limited coverage
domain-specific rules
```

### Strategy B — embedding similarity

Create edges when:

```text
semantic similarity > threshold
```

Advantages:

```text
easy to scale
```

Disadvantages:

```text
similarity ≠ relation
```

This can create many false edges.

### Strategy C — LLM relation extraction

Ask an LLM whether two evidence units have a relation.

Advantages:

```text
potentially better semantic coverage
```

Disadvantages:

```text
cost
latency
hallucinated relations
provider variability
reproducibility challenges
```

### V7 recommendation

Start with:

```text
deterministic relations
+
existing metadata
```

Then introduce model-based relation extraction only as a measured extension.

---

# 16. Do not let the graph become a hidden LLM cache

Bad architecture:

```text
LLM reads whole corpus
↓
LLM builds giant graph
↓
graph is treated as truth
```

This makes evaluation difficult because the graph itself may contain generated information.

Better:

```text
source evidence
↓
controlled extraction
↓
edge
↓
source provenance retained
```

When LLM extraction is used, persist:

```text
model
prompt version
input identifiers
output
confidence
timestamp
provider
token usage
```

The graph must remain reproducible.

---

# 17. Graph extraction audit

Before using the graph for retrieval:

```text
sample graph edges
↓
human review
↓
precision estimate
↓
error taxonomy
```

Possible edge errors:

```text
wrong entity
wrong quantity
wrong direction
wrong temporal order
false support
false contradiction
duplicate edge
cross-paper mismatch
```

Do not skip this stage.

A graph with low precision can make retrieval worse while looking sophisticated.

---

# 18. Minimum graph audit sample

A practical pilot can review:

```text
50–200 edges
```

depending on corpus size and available time.

The sample should be stratified by:

```text
edge type
paper
section
difficulty
```

when feasible.

For each edge record:

```text
correct
incorrect
ambiguous
not-checkable
```

and optionally:

```text
error reason
```

The audit is not meant to provide perfect graph certification.

It is meant to detect catastrophic extraction problems before retrieval experiments.

---

# 19. Graph node identity

Every node needs a stable identifier.

Examples:

```text
paper:abc123

section:abc123:results

table:abc123:7

equation:abc123:12

claim:abc123:claim004
```

The exact format can differ.

The core requirement is:

```text
stable IDs
+
no accidental collisions
```

Do not use array positions that can change whenever indexing order changes.

---

# 20. Node provenance

Each node should point back to:

```text
paper
page
section
source span / source object
```

For structured units:

```text
table ID
equation ID
row ID
column ID
```

when available.

This allows:

```text
graph node
↓
original evidence
```

to be reconstructed.

---

# 21. Edge direction matters

These are not equivalent:

```text
A DEFINES B
```

and:

```text
B DEFINES A
```

Similarly:

```text
A PRECEDES B
```

is directional.

Store direction explicitly.

For undirected similarity relationships:

```text
similar_to
```

may be symmetric.

Do not infer symmetry where the relation is actually directional.

---

# 22. Graph relation confidence

Not all edges should have equal status.

A useful conceptual representation:

```text
edge_type
confidence
provenance
extractor
```

For example:

```text
PRECEDES
1.0
metadata

MENTIONS
1.0
deterministic parser

SUPPORTS
0.82
LLM extractor
```

Confidence should not automatically be treated as calibrated probability.

Call it:

```text
edge confidence score
```

until calibration is demonstrated.

---

# 23. Initial retrieval before graph traversal

Graph traversal should begin from retrieved seed nodes.

Example:

```text
question
  ↓
dense/BM25 retrieval
  ↓
top-5 seed evidence
  ↓
graph neighbors
```

This is safer than:

```text
question
  ↓
search entire graph
```

because it keeps the graph bounded around evidence that is already semantically relevant.

---

# 24. One-hop expansion

The simplest graph-assisted retrieval is:

```text
retrieve seeds
↓
expand each seed by one relation
↓
rerank all candidates
↓
select final evidence
```

Example:

```text
seed:
table-17

neighbors:
parameter-X
claim-44
caption-17
paper-A
equation-9
```

The reranker decides which neighbors are useful.

This should be the first graph experiment.

---

# 25. Why one-hop first

One-hop expansion is:

```text
easy to reason about
easy to benchmark
bounded
cheap
```

Multi-hop graph traversal can explode.

For example:

```text
seed
 ↓
neighbors
 ↓
neighbors of neighbors
 ↓
...
```

The candidate count can grow rapidly.

Do not start with arbitrary deep traversal.

---

# 26. Graph expansion budget

Define a strict budget such as:

```text
maximum seed nodes
maximum neighbors per seed
maximum graph hops
maximum final evidence units
```

Example:

```text
seed_k = 5
max_hops = 1
neighbor_cap = 8
final_k = 10
```

The exact values should be selected experimentally.

The key rule is:

```text graph retrieval must have an explicit budget
```

Otherwise cost and latency comparisons become unfair.

---

# 27. Context-budget fairness

Suppose baseline uses:

```text 10 evidence chunks
```

and graph system uses:

```text 40 evidence units
```

An improvement may simply come from reading more evidence.

Therefore track:

```text final evidence count
total context tokens
unique papers
```

and ideally compare under:

```text equal context budget
```

or:

```text fixed retrieval budget
```

This is essential.

---

# 28. Relation-aware reranking

Instead of only scoring:

```text similarity(question,evidence)
```

a graph-aware score can conceptually combine:

```text semantic relevance
+
edge relevance
+
path usefulness
```

For example:

```text score =
α * semantic_score
+
β * relation_score
```

The exact equation should be implemented only after defining the measurable components.

Do not introduce unexplained magic weights.

---

# 29. Relation-specific retrieval

Different questions may need different relations.

For example:

```text MULTI_HOP
→ DEFINES / REPORTS / SUPPORTS

TEMPORAL
→ PRECEDES / UPDATES

CONFLICTING
→ CONTRADICTS / COMPARES_WITH

CHAIN
→ DERIVED_FROM / SUPPORTS
```

This suggests a future adaptive policy:

```text question type
↓
relation family
↓
graph retrieval
```

But do not make the graph router complex on the first experiment.

First show that relation-specific retrieval helps.

---

# 30. Graph and Compass

Compass can potentially remain unchanged.

Current concept:

```text
question
↓
Compass
↓
retrieval strategy
```

V7 can instead add graph support after initial retrieval:

```text
question
↓
Compass
↓
initial retrieval
↓
graph-assisted expansion
```

This isolates graph effects from routing effects.

Do not retrain Compass simultaneously unless a later experiment specifically tests graph-aware routing.

---

# 31. Graph and V3 failure detector

V3 predicts:

```text
is the current retrieval probably insufficient?
```

The graph creates additional evidence candidates.

A possible later architecture is:

```text
initial retrieval
↓
V3 failure detector
↓
if likely failure:
    graph expansion
↓
new evidence set
```

However, this should not be the first V7 experiment.

First determine whether:

```text graph retrieval itself
```

produces useful evidence gains.

Then integrate with V3.

---

# 32. Graph and V2 verifier

V2 evidence verification is a natural downstream consumer.

Potential pipeline:

```text
Question
 ↓
retrieval
 ↓
graph expansion
 ↓
answer
 ↓
claim extraction
 ↓
citation mapping
 ↓
graph/provenance verification
```

The graph can help verify relationships such as:

```text claim cites table row
claim cites equation
claim compares two papers
claim describes temporal change
```

But again:

```text retrieval first
verification second
```

for the primary V7 experiment.

---

# 33. V7 experiment hierarchy

Use a controlled ladder.

### V7-A — V6 baseline

```text
current best structure-aware retrieval
```

Purpose:

```text quality reference
```

### V7-B — graph indexing only

Build graph but do not use it for retrieval.

Purpose:

```text isolate graph construction overhead
```

### V7-C — one-hop graph expansion

Use retrieved seed nodes to expand candidates.

Purpose:

```text first graph retrieval test
```

### V7-D — relation-aware reranking

Use relation features when ranking candidates.

Purpose:

```text test whether relational information improves candidate ordering
```

### V7-E — relation-specific expansion

Use question/evidence type to prioritize relevant edge types.

Purpose:

```text test targeted graph retrieval
```

### V7-F — combined graph system

Combine the best justified mechanisms.

Purpose:

```text practical upper candidate
```

### V7-G — V7 + V2 verification

Only after retrieval gains are established.

Purpose:

```text end-to-end provenance/citation impact
```

Do not jump directly to V7-F/G.

---

# 34. Primary benchmark emphasis

V7 should oversample or deliberately include:

```text MULTI_HOP
TEMPORAL
CONFLICTING
CHAIN
```

because those are the categories where relationships are most likely to matter.

SIMPLE questions remain necessary as controls.

A method that improves only difficult questions but damages SIMPLE retrieval may not be useful operationally.

---

# 35. Benchmark design principle

Do not create graph-specific questions that are impossible without your graph implementation.

The benchmark should test scientific evidence requirements.

For example:

```text bad:
\"What graph relationship connects X and Y?\"

good:
\"How did later work revise the earlier estimate of X?\"
```

The second question is scientifically meaningful independent of the implementation.

---

# 36. Multi-hop benchmark audit

For each MULTI_HOP question, verify:

```text at least two evidence contributions
both are necessary
they are distinct
they are not near-duplicates
the answer depends on their combination
```

A graph system should not get an artificial advantage from questions whose answer is already directly stated in one passage.

---

# 37. Temporal benchmark audit

For each TEMPORAL question, verify:

```text at least two time-distinct evidence points
same scientific quantity / claim family
actual temporal relationship
answer requires comparison across time
```

Also record:

```text publication dates
relevant experiment/observation dates
```

when the question depends on them.

---

# 38. Conflict benchmark audit

For each CONFLICTING question, verify:

```text same scientific target
different claims/results
contextually comparable
difference is scientifically meaningful
```

Do not treat:

```text X = 5
Y = 7
```

as conflict when:

```text X and Y
```

are different quantities.

---

# 39. Chain benchmark audit

For each CHAIN question, verify:

```text step 1
→ step 2
→ final conclusion
```

and make sure no single source passage trivially contains the whole answer.

This is particularly important because earlier benchmark work identified cases where supposedly multi-stage reasoning was directly available in an abstract.

The V7 benchmark must not repeat that problem.

---

# 40. Gold evidence definition

The benchmark should allow:

```text one or more valid evidence sets
```

where practical.

Do not force:

```text exact chunk IDs
```

when an alternative passage genuinely supports the answer.

Still preserve exact gold chunks where they are part of the historical benchmark for continuity.

Record the distinction:

```text exact_gold_recall
```

versus:

```text evidence_set_sufficiency
```

when both are available.

---

# 41. Oracle reference

V1/V2 used Oracle-v2 retrieval semantics.

For V7:

```text graph-assisted conditions
```

can change which evidence is retrievable.

Therefore recompute a V7-aware reference only if the benchmark or retrieval universe materially changes.

Do not silently compare:

```text old Oracle
```

against:

```text new retrieval universe
```

as though the conditions were identical.

Maintain both:

```text historical Oracle
```

and:

```text current experiment reference
```

where necessary.

---

# 42. Graph search vs Oracle

The strongest possible reference remains useful.

For example:

```text always strongest current retrieval
```

can tell you:

```text quality ceiling under current infrastructure
```

The graph experiment asks:

```text can we approach that quality more efficiently or recover cases missed by flat retrieval?
```

This aligns the graph experiment with the broader AtlasRAG goal:

```text evidence quality
+
efficiency
```

rather than novelty for its own sake.

---

# 43. Graph construction cost

Measure graph construction separately from query-time cost.

Important quantities:

```text papers processed
nodes created
edges created
time
CPU / memory
LLM calls if any
tokens if any
failures
```

Do not hide offline indexing cost.

A graph can be worthwhile even if indexing is expensive when:

```text query cost decreases
```

or:

```text evidence quality improves substantially
```

but the tradeoff must be shown.

---

# 44. Query-time graph cost

Measure:

```text graph traversal time
candidate count
reranking time
memory / cache access
```

and compare against:

```text baseline retrieval latency
```

At minimum report:

```text p50
p95
```

when enough samples exist.

---

# 45. Storage overhead

Record:

```text baseline index size
graph index size
additional metadata size
```

This is especially important if graph construction creates:

```text many nodes
many edges
duplicate evidence representations
```

A large overhead may be acceptable, but must be documented.

---

# 46. Graph density

Track:

```text nodes
edges
edges/node
```

by edge type.

Extremely dense graphs can become noisy.

Extremely sparse graphs may provide little benefit.

Graph density should therefore be treated as an engineering diagnostic, not as an optimization target by itself.

---

# 47. Failure taxonomy

V7 failure analysis should distinguish:

```text graph extraction failure
graph linking failure
retrieval failure
graph expansion failure
reranking failure
answer-generation failure
citation failure
```

Examples:

```text correct evidence exists
but wrong edge
→ graph linking failure

correct edge exists
but not traversed
→ graph retrieval failure

correct graph evidence retrieved
but answer incorrect
→ generation failure
```

This separation prevents misleading conclusions.

---

# 48. Graph false-positive edges

A major V7 risk:

```text incorrect edge
→ wrong evidence expansion
→ distractor context
→ answer degradation
```

Measure this explicitly.

Possible metric:

```text graph edge precision
```

and investigate whether:

```text higher graph precision
```

correlates with:

```text better retrieval recall
```

Do not assume more edges are better.

---

# 49. Graph false-negative edges

The opposite failure:

```text real relation
exists in source

but graph misses it
```

can prevent useful traversal.

Possible categories:

```text extraction missed relation
identifier mismatch
normalization failure
temporal metadata missing
cross-paper linkage missing
```

This is especially important for:

```text multi-hop
temporal
conflicting
```

benchmarks.

---

# 50. Entity normalization

A graph needs consistent identities.

Scientific text may use:

```text
H0
H_0
Hubble constant
Hubble parameter
```

or analogous variants in other domains.

Do not blindly merge them.

Normalization should consider:

```text alias
symbol
context
section
paper
```

The first implementation may use conservative matching.

False merges can be worse than missed links.

---

# 51. Quantity normalization

For numeric relationships, preserve:

```text value
unit
uncertainty
scale
sign
direction
context
```

For example:

```text 5 km/s/Mpc
```

must not silently become:

```text 5
```

without its unit.

Likewise:

```text 5 ± 1
```

must not be represented as:

```text 5
```

when uncertainty matters.

This connects V7 directly to V6 numeric structure work.

---

# 52. Equation relationships

Equations may define:

```text parameter
relationship
derived quantity
```

A useful graph can include:

```text equation E
   ↓ defines
parameter X
```

or:

```text equation E
   ↓ derives
quantity Y
```

But do not attempt symbolic theorem proving in the first V7 experiment.

The initial goal is:

```text retrieval relationship
```

not:

```text mathematical verification
```

---

# 53. Table relationships

Structured tables can create edges such as:

```text table row
→ reports
parameter value

table caption
→ describes
table

result paragraph
→ refers_to
table
```

This can connect prose interpretation to numeric evidence.

That may be especially useful for questions such as:

```text What value did the authors report, and how did they interpret it?
```

The evidence chain becomes:

```text table
↓
value
↓
result paragraph
↓
interpretation
```

---

# 54. Citation graph

Scientific papers already contain a citation network.

A simple paper-level graph may encode:

```text Paper A → CITES → Paper B
```

This can provide useful retrieval hints.

But:

```text citation
≠ support
```

A paper may cite another work for:

```text background
method
historical context
comparison
```

without supporting the answer to the user's question.

Therefore paper citation edges should be treated as navigation signals, not evidence assertions.

---

# 55. Cross-paper evidence links

Cross-paper edges are especially risky.

A paper mentioning:

```text Hubble constant
```

does not automatically support a claim about another paper's value.

A cross-paper relation should require explicit evidence such as:

```text cited parameter
explicit comparison
named previous result
direct update
stated disagreement
```

Conservative linking is preferable.

---

# 56. Graph traversal strategies

Possible policies:

### Breadth-first

```text
seed
→ all one-hop neighbors
```

Simple and predictable.

### Relation-filtered

```text
seed
→ only relevant relation types
```

Potentially more precise.

### Weighted

```text edge importance
+
semantic relevance
```

More flexible but harder to interpret.

### Path-aware

```text find paths satisfying
specific evidence relation sequence
```

Powerful for chain questions.

V7 should progress in this order rather than starting with complex path search.

---

# 57. Path patterns

Useful path templates may include:

### Definition → value

```text evidence
→ DEFINES
→ parameter
→ HAS_VALUE
→ table/evidence
```

### Earlier → later

```text evidence A
→ PRECEDES
→ evidence B
→ REPORTS
→ same parameter
```

### Claim → support

```text claim
→ SUPPORTED_BY
→ evidence
```

### Conflict

```text claim A
→ CONFLICTS_WITH
→ claim B
```

### Chain

```text observation
→ METHOD_RESULT
→ intermediate conclusion
→ FINAL_CLAIM
```

The actual edge names should follow the implemented schema.

---

# 58. Do not hard-code scientific answers into graph rules

Bad:

```text if H0 appears
then retrieve H0 table
```

This merely memorizes the domain.

Better:

```text detect scientific identifier
↓
link to evidence objects
↓
retrieve according to relation
```

The representation should be general enough to test transfer.

---

# 59. V7 transfer question

If V5 established a target-domain benchmark, V7 can test:

```text graph construction on source domain
```

and then:

```text graph retrieval on unseen domain
```

But this should come only after the within-domain experiment is stable.

First:

```text does graph retrieval work?
```

Then:

```text does it transfer?
```

Otherwise two uncertainties become entangled.

---

# 60. Graph construction under domain shift

Different domains may have different relation patterns.

For example:

```text astrophysics
parameter ↔ measurement ↔ model

biomedicine
intervention ↔ population ↔ outcome

materials science
material ↔ process ↔ property
```

The shared abstraction is:

```text scientific evidence relationships
```

but the concrete ontology differs.

V7 should therefore record:

```text relation reuse
relation mismatch
domain-specific edges
```

rather than assuming one universal ontology.

---

# 61. Start with relation families

A practical cross-domain abstraction is:

```text structural
    contains
    defines

evidential
    supports
    reports

comparative
    compares
    conflicts

temporal
    precedes
    updates
```

This is more likely to transfer than domain-specific scientific symbols.

---

# 62. V7 data layout

Recommended structure:

```text
data/v7/
    graph/
    nodes/
    edges/
    audits/
    questions/
    retrieval_states/
    manifests/
    results/
```

Possible experiment outputs:

```text
experiments/v7/
    v7-a-baseline/
    v7-b-index-only/
    v7-c-one-hop/
    v7-d-rerank/
    v7-e-relation-specific/
    v7-f-combined/
```

Use repository conventions when they already exist.

Do not create redundant directories merely for naming aesthetics.

---

# 63. Graph schema versioning

Graph schemas will evolve.

Record something like:

```text
graph_schema_version
```

and maintain:

```text
v1
v2
```

rather than changing edge semantics silently.

A result generated with:

```text
graph_schema_v1
```

must remain reconstructable after:

```text
graph_schema_v2
```

is introduced.

---

# 64. Graph manifest

A graph manifest should record:

```text
corpus hash
paper count
node count
edge count
schema version
extractor version
embedding model if used
LLM model if used
prompt version if used
construction timestamp
code commit
```

This prevents:

```text
\"Which graph produced this result?\"
```

from becoming impossible to answer.

---

# 65. Reproducibility rule

A graph should be rebuildable from:

```text
corpus
+
code
+
configuration
+
model versions
```

where license/access permits.

If external LLM extraction prevents deterministic reproduction, save:

```text raw extractor outputs
```

as research artifacts.

Do not rely on rerunning a provider call to recreate the graph.

---

# 66. Graph extraction caching

If relation extraction uses an LLM:

```text cache by stable input hash
```

Persist:

```text input hash
model
prompt version
output
tokens
timestamp
```

This reduces cost and allows repeated analysis.

The cache itself should be versioned.

---

# 67. Provider failure handling

The current AtlasRAG LLM layer already has bounded retry behavior for provider failures.

V7 extraction should preserve the same principle:

```text bounded retries
finite attempts
explicit failure state
persisted run summary
```

Do not allow a benchmark-building script to run indefinitely under:

```text 429
connection failures
timeouts
```

A failed extraction should be:

```text recorded
```

not silently converted into:

```text missing edge = no relation
```

because that would bias the graph.

---

# 68. Instrumentation requirements

For each V7 construction or evaluation run, persist:

```text logical calls
provider API calls
cache hits
cache misses
retry attempts
rate-limit errors
connection errors
prompt tokens
completion tokens
latency
final status
```

The current project previously had instrumentation gaps around these quantities.

V7 should close them rather than repeating the same limitation.

---

# 69. Logical calls vs provider calls

Track them separately.

Example:

```text logical relation extraction requests = 200

provider calls = 137

cache hits = 63
```

This is different from:

```text 200 provider calls
```

Never infer provider usage from logical request count.

---

# 70. Cost accounting

For each graph experiment report:

```text offline graph construction cost
+
online query cost
```

If graph construction is one-time, say so.

A fair operational analysis might compare:

```text baseline total cost over N queries
```

against:

```text graph construction amortized over N queries
+
graph query cost
```

For multiple deployment scales:

```text N = 100
N = 1,000
N = 10,000
```

can show when graph construction becomes worthwhile.

Use actual measured provider pricing/configuration rather than hard-coding a stale price.

---

# 71. Latency accounting

Separate:

```text retrieval latency
graph traversal latency
reranking latency
answer generation latency
```

Report:

```text p50
p95
```

when sample size permits.

If a graph makes retrieval 10% slower but evidence recall rises substantially, that can still be a useful result.

The tradeoff must be quantified.

---

# 72. Primary retrieval metrics

At minimum:

```text gold evidence recall
evidence-set recall
top-k recall
MRR / ranking metric where appropriate
```

For graph-specific analysis also consider:

```text graph path recall
required relation coverage
```

Do not use graph metrics as substitutes for actual evidence recovery.

---

# 73. Evidence completeness

For a question requiring:

```text A + B + C
```

measure:

```text 0/3
1/3
2/3
3/3
```

when the benchmark supports this annotation.

This is often more informative than binary:

```text passed / failed
```

for multi-hop and chain questions.

---

# 74. Relation coverage metric

For graph-targeted questions, define whether all required relations were available.

For example:

```text required:
A → defines → X
B → reports → X
C → updates → X

retrieved:
A
B
missing C
```

Then:

```text relation coverage = 2/3
```

This should be treated as a diagnostic, not automatically as a gold standard.

---

# 75. Answer-level metrics

Once retrieval results are locked, evaluate:

```text correctness
relevance
groundedness
citation correctness
citation completeness
unsupported claim rate
```

Use the same definitions established in earlier weeks where possible.

Do not change evaluation criteria solely because they favor V7.

---

# 76. Citation provenance metrics

Potential measures:

```text citation precision
citation completeness
source-span correctness
claim-to-source alignment
```

A citation is stronger when:

```text cited source actually contains the supporting evidence
```

not merely:

```text cited source discusses the same topic
```

This distinction is critical in scientific RAG.

---

# 77. Human audit subset

Automatic metrics are not enough.

Select a representative subset covering:

```text graph success
graph failure
baseline success
baseline failure
ambiguous cases
```

Review:

```text evidence sufficiency
graph relation correctness
answer correctness
citation correctness
```

Blind review is preferable when practical.

---

# 78. Paired evaluation

V7 should compare the same questions under:

```text baseline
vs
graph-assisted retrieval
```

Use paired per-question results.

This gives stronger evidence than comparing unrelated averages.

Relevant summaries:

```text mean difference
median difference
bootstrap confidence interval
sign test / paired nonparametric test
```

The exact statistical method should match sample size and metric type.

---

# 79. Question-type breakdown

Report:

```text SIMPLE
MULTI_HOP
CONFLICTING
TEMPORAL
CHAIN
```

separately.

A graph may have:

```text no benefit on SIMPLE
large benefit on MULTI_HOP
moderate benefit on TEMPORAL
```

That is a useful result.

Do not collapse everything into one score.

---

# 80. Failure rescue analysis

One of the strongest V7 diagnostics is:

```text baseline failed
graph succeeded
```

Inspect those cases.

Likewise:

```text baseline succeeded
graph failed
```

These expose:

```text rescue behavior
```

and:

```text regression behavior
```

A graph should not be judged only by overall average improvement.

---

# 81. Regression rate

Define:

```text baseline correct
graph incorrect
```

as a regression.

Also record:

```text baseline incorrect
graph correct
```

as a rescue.

Then compute:

```text rescue count
regression count
net change
```

This makes the graph effect concrete.

---

# 82. Context pollution

Graph expansion may introduce unrelated evidence.

Measure:

```text fraction of retrieved evidence judged relevant
```

and inspect cases where:

```text graph expands from correct seed
→ adds distractor
→ reranker selects distractor
```

A graph that retrieves more evidence but lowers precision can be harmful.

---

# 83. Relation-aware reranking ablation

Test:

```text semantic only
```

against:

```text semantic + relation features
```

while keeping candidate pool fixed.

This isolates whether the gain comes from:

```text candidate recall
```

or:

```text better ranking
```

Both are important but different.

---

# 84. Graph expansion ablation

Test:

```text no expansion
one-hop expansion
two-hop expansion
```

only if one-hop produces useful evidence.

The expected risk is:

```text two-hop
→ more candidates
→ more noise
→ higher latency
```

Do not assume deeper traversal is better.

---

# 85. Relation-family ablation

Run one family at a time:

```text structural
evidential
temporal
comparative
```

This answers:

```text which relationship information is actually useful?
```

A result such as:

```text temporal edges help
generic similarity edges do not
```

is scientifically more useful than:

```text graph helps by +X
```

with no explanation.

---

# 86. Graph-free control

A particularly important control:

```text retrieve top-N additional semantically similar chunks
```

with the same candidate/context budget.

Why?

Because otherwise graph retrieval may look better simply because it expands the search space.

Compare:

```text semantic expansion
vs
graph-guided expansion
```

under matched budgets.

This is one of the most important V7 controls.

---

# 87. Random graph control

A weaker but useful sanity check:

```text preserve graph size
randomize edges
```

Then compare:

```text real graph
vs
random graph
```

If performance remains identical, the relational structure may not be contributing meaningfully.

This should be a secondary diagnostic, not the main experiment.

---

# 88. Retrieval-only first

The first V7 result table should ideally look like:

```text
Condition
Evidence recall
Context size
Latency
Cost
```

Only after that:

```text Answer accuracy
Groundedness
Citation metrics
```

This separation tells you whether the graph helps:

```text retrieval
```

before it helps:

```text generation
```

---

# 89. Possible outcomes

### Outcome A

```text graph improves evidence recall
and
improves answer/citation quality
```

Strongest case.

### Outcome B

```text graph improves retrieval
but answer quality unchanged
```

Possible explanation:

```text generation bottleneck
```

### Outcome C

```text graph retrieval unchanged
but citation provenance improves
```

Still potentially useful for V2/V3 integration.

### Outcome D

```text graph hurts retrieval
```

Potential explanation:

```text edge noise
context pollution
bad normalization
```

### Outcome E

```text graph only helps narrow question types
```

Then scope the claim accordingly.

---

# 90. Graph quality vs retrieval quality

Do not assume:

```text graph precision ↑
→ retrieval quality ↑
```

There may be a tradeoff.

For example:

```text very sparse graph
→ high precision
→ poor recall

dense graph
→ high recall
→ noisy retrieval
```

This can produce a useful graph-quality curve.

---

# 91. Graph confidence calibration

If edges have confidence scores, evaluate whether confidence is meaningful.

Possible diagnostics:

```text reliability bins
precision by confidence band
Brier score
calibration error
```

Do not call an edge score:

```text 0.9 probability
```

unless calibrated evidence supports that interpretation.

---

# 92. Error propagation

Graph systems introduce a new error chain:

```text source
↓
extraction
↓
entity normalization
↓
edge creation
↓
traversal
↓
retrieval
↓
answer
```

A failure at the beginning can propagate downstream.

Track:

```text first incorrect stage
```

where possible.

This is more informative than simply saying:

```text answer was wrong
```

---

# 93. Graph provenance inspection tool

A useful debugging utility should allow:

```text node ID
→ source evidence
```

and:

```text edge ID
→ source evidence for relation
```

and:

```text retrieved evidence path
→ all contributing nodes/edges
```

This will make failure analysis much easier.

A CLI such as:

```powershell
python scripts/inspect_graph.py --node <id>
python scripts/inspect_graph.py --edge <id>
python scripts/inspect_graph.py --question <id>
```

is a useful design target.

Use the actual script name only after implementation.

---

# 94. Graph visualization

A visualization can help during debugging, but it is not itself evidence.

A useful graph view can show:

```text query
→ seed evidence
→ neighbors
→ final selected evidence
```

Use it for:

```text debugging
presentation
failure inspection
```

Do not rely on visually appealing graph diagrams as a substitute for quantitative analysis.

---

# 95. Avoid giant graph screenshots

The graph should remain interpretable.

Prefer:

```text one question
one path
small local neighborhood
```

rather than:

```text entire corpus graph
```

A whole-corpus graph often becomes visually meaningless.

---

# 96. Graph path explanation

For successful retrieval, preserve the path that caused candidate inclusion.

Example:

```text seed = table-17

table-17
  ↓ REPORTS
parameter-X
  ↓ DEFINED_BY
equation-9
  ↓ INTERPRETED_BY
result-42
```

This can later support explanations such as:

```text retrieved because it is connected to the initial evidence through a relevant scientific relationship
```

Do not expose internal graph details to users automatically unless the product design calls for it.

---

# 97. User-facing explanation

A future UI could optionally show:

```text Evidence path
```

rather than only:

```text Source 1
Source 2
Source 3
```

For example:

```text Result
↓
reported in Table 4
↓
defined by Eq. 7
↓
compared with Study B
```

But V7 should first establish that the graph is correct.

Presentation comes after evidence.

---

# 98. Graph + citation correctness

A graph can support a stronger citation workflow:

```text answer claim
↓
retrieved evidence
↓
graph provenance
↓
original source
```

Potentially this makes it easier to detect:

```text citation points to related but non-supporting source
```

Again, this must be measured through V2-style verification.

---

# 99. V7 benchmark expansion

Do not immediately create thousands of questions.

Start with:

```text high-quality relationship-heavy questions
```

A smaller clean benchmark is more useful than a large noisy one.

Potential initial target:

```text 50–150 high-quality questions
```

depending on available papers and review capacity.

This is a planning range, not a required number.

---

# 100. Human review workload

Graph-oriented benchmark review is expensive.

Prioritize review of:

```text multi-hop
temporal
conflict
chain
```

and automatically generated relation structures.

Create a rejection taxonomy such as:

```text one-passage answer
wrong relation
same-quantity mismatch
temporal false positive
conflict false positive
duplicate evidence
unsupported answer
```

This should build on prior benchmark lessons.

---

# 101. Targeted hard negatives

Graph experiments need hard negatives such as:

```text same entity
wrong relation

same parameter
wrong time

same topic
wrong quantity

same paper
wrong section

same value
wrong unit/context
```

These are much better than random unrelated chunks.

They test whether graph retrieval actually understands relations.

---

# 102. Avoid gold-edge leakage

At inference time, the system must not receive:

```text gold relation type
gold path
gold node ID
gold edge ID
```

The graph itself may contain relations extracted from source documents.

But:

```text benchmark annotation
```

must remain separate.

A gold answer should never be used to decide which graph path to traverse.

---

# 103. Negative evidence

Scientific retrieval can require understanding:

```text no evidence found
```

or:

```text the source explicitly reports no effect
```

Do not treat negative claims as missing evidence.

Represent concepts such as:

```text reports_no_effect
rules_out
fails_to_detect
```

only if the corpus and benchmark clearly require them.

Do not build a broad negation ontology prematurely.

---

# 104. Uncertainty propagation

Scientific evidence often contains:

```text ± uncertainty
confidence interval
credible interval
upper limit
lower limit
```

Graph relations involving values should preserve these distinctions.

For example:

```text reports
X = 5 ± 1
```

is different from:

```text upper_limit
X < 5
```

A graph should not collapse these into generic:

```text HAS_VALUE
```

without preserving semantics.

---

# 105. Unit consistency

Before linking numeric evidence:

```text check unit compatibility
```

when feasible.

Potential normalization:

```text km → m
eV → MeV
```

can be useful.

But conversions must be deterministic and auditable.

Do not use an LLM to perform silent scientific unit conversion.

---

# 106. Numeric comparison safety

For conflict or temporal graphs, two values should be compared only when:

```text same quantity
same unit or valid conversion
same relevant condition
```

Potential differences:

```text observed vs predicted
raw vs corrected
local vs global
one experiment vs another
```

must remain explicit.

A graph edge saying:

```text CONFLICTS_WITH
```

is a strong claim.

Use conservative criteria.

---

# 107. Graph indexing implementation

The implementation should ideally separate:

```text graph construction
graph storage
graph query
graph-assisted retrieval
```

Do not embed graph logic into the main retriever in one giant function.

A conceptual module boundary:

```text src/atlasrag/graph/
    schema.py
    build.py
    store.py
    query.py
    provenance.py
```

The exact structure should follow the existing project architecture.

---

# 108. Graph store choice

The first implementation does not necessarily need Neo4j or another external graph database.

A simple local representation may be enough:

```text JSONL
SQLite
DuckDB
NetworkX
in-memory adjacency maps
```

The choice should prioritize:

```text reproducibility
simplicity
query speed for benchmark size
easy inspection
```

Do not introduce infrastructure just for appearance.

---

# 109. When an external graph database is justified

Only consider a dedicated graph database if measurements show a need such as:

```text graph too large for simple local storage
query patterns become expensive
interactive traversal needed
deployment requirements justify it
```

For a research benchmark, a lightweight local graph is often easier to reproduce.

Do not migrate early.

---

# 110. Graph cache invalidation

If:

```text corpus changes
schema changes
extractor changes
normalizer changes
```

the graph should be considered stale.

Use a graph manifest or hash to detect:

```text source mismatch
```

A graph built from:

```text corpus commit A
```

must not be silently reused for:

```text corpus commit B
```

if evidence changed.

---

# 111. Exact graph provenance record

A robust edge record can conceptually contain:

```json
{
  "edge_id":"edge-000123",
  "source_node":"claim-12",
  "relation":"supports",
  "target_node":"table-44",
  "paper_id":"paper-07",
  "section":"Results",
  "page":8,
  "source_span":"...",
  "extractor":"deterministic_rule_v1",
  "confidence":1.0
}
```

This is an example schema only.

Do not copy it blindly if repository conventions differ.

---

# 112. Graph query API

Potential internal operations:

```text
get_node(id)

get_neighbors(id,relation_type)

expand(seed_ids,hops,max_nodes)

find_paths(source,target,max_hops)

get_provenance(edge_id)
```

Keep them deterministic where possible.

The retrieval layer should call graph APIs rather than accessing storage internals directly.

---

# 113. Retrieval-state instrumentation

For each query, log:

```text seed IDs
seed scores
expanded IDs
edge types traversed
candidate counts
final selected IDs
graph traversal time
```

This makes it possible to answer:

```text Did the graph actually contribute?
```

A result cannot be trusted if the system claims graph assistance but most final evidence came from the baseline seeds.

---

# 114. Graph contribution metric

A useful diagnostic is:

```text graph-added evidence fraction
```

For example:

```text baseline seeds = 5
final context = 10
graph-added = 3
```

Then:

```text graph-added fraction = 3/10
```

Also measure:

```text graph-added evidence that was gold/supporting
```

This separates:

```text graph activity
```

from:

```text graph usefulness
```

---

# 115. Graph rescue metric

Define:

```text cases where baseline misses required evidence
and graph expansion recovers it
```

This directly tests the central motivation.

For example:

```text baseline recall = 0
graph recall = 1
```

is a clear rescue.

Aggregate:

```text rescue rate
```

over relationship-heavy questions.

---

# 116. Graph regression metric

Likewise:

```text baseline retrieves all required evidence
graph loses required evidence
```

This can happen when:

```text fixed final_k
graph candidates crowd out baseline evidence
```

A graph that has high theoretical recall but causes regressions is not automatically useful.

---

# 117. Final-k competition

One key design issue:

```text graph-added candidates
compete with baseline candidates
```

If final_k is fixed, graph expansion can displace good evidence.

Test policies such as:

```text preserve top baseline seeds
+
add graph candidates
```

versus:

```text globally rerank all candidates
```

This is a meaningful ablation.

Do not silently choose the version that looks better.

---

# 118. Context assembly policy

Possible strategies:

### Preserve seeds

Always retain the top few baseline results.

### Global ranking

Rerank all graph-expanded candidates.

### Diversity-aware selection

Prevent too many nearly duplicate nodes.

### Path coverage

Prefer candidates that complete missing evidence paths.

Start with:

```text preserve seeds
```

because it is easy to interpret.

---

# 119. Graph path completion

A more advanced mechanism:

```text question requires A + B

retrieval finds A
graph shows relation to B
B is added
```

This is a particularly clean demonstration of graph utility.

But the system must not use:

```text gold knowledge that the question requires B
```

at inference time.

The path should arise from:

```text retrieved evidence
+
graph relations
```

not benchmark labels.

---

# 120. Evidence graph vs knowledge graph distinction

The V7 graph is not intended to be:

```text universal knowledge graph
```

It is better described as:

```text provenance-aware evidence graph
```

because nodes and edges should remain grounded in the source corpus.

The difference matters.

A generic knowledge graph may contain:

```text facts
```

that are detached from:

```text exact source context
```

AtlasRAG should preserve the source.

---

# 121. Research claim boundaries

A positive V7 result supports something like:

```text explicit evidence relationships improved retrieval under the evaluated scientific benchmark and configuration
```

It does not automatically support:

```text graphs solve scientific RAG
```

or:

```text graph reasoning is universally better
```

Scope the claim to:

```text evaluated corpus
benchmark
graph schema
retrieval stack
```

and broader domains only when actually tested.

---

# 122. Novelty framing

Before writing a paper or public claim, perform a fresh literature review covering:

```text graph RAG
knowledge graph RAG
graph-based retrieval
provenance-aware RAG
scientific knowledge graphs
evidence graphs
multi-hop scientific QA
citation-aware RAG
```

Separate:

```text established techniques
```

from:

```text AtlasRAG's empirical configuration
```

A contribution can be valuable even when:

```text graph retrieval
```

itself is not new.

The novelty may instead be:

```text controlled evaluation
+
scientific benchmark
+
relationship-specific ablations
+
retrieval/citation analysis
```

Do not claim originality without current evidence.

---

# 123. V7 failure taxonomy for paper writing

Create final categories such as:

```text F1 extraction error
F2 entity normalization error
F3 relation false positive
F4 relation false negative
F5 graph traversal miss
F6 candidate crowding
F7 reranker miss
F8 evidence ambiguity
F9 generation failure
F10 citation failure
```

This allows a stronger discussion section.

---

# 124. V7 ablation matrix

A compact final matrix can look like:

```text
Condition                  Graph   Expansion   Relation rerank
--------------------------------------------------------------
V7-A baseline              No      No          No
V7-B graph index only      Yes     No          No
V7-C one-hop               Yes     Yes         No
V7-D relation rerank       Yes     Yes         Yes
V7-E relation-specific     Yes     filtered    Yes
V7-F combined              Yes     Yes         Yes
```

Add:

```text context budget
latency
cost
```

to every row.

---

# 125. Additional control: larger semantic retrieval

To ensure graph benefits are not merely:

```text more candidates
```

run a matched semantic expansion control.

Example concept:

```text baseline k=10

semantic expanded candidate pool = 20

graph candidate pool = 20
```

Then compare under:

```text same candidate budget
same final context budget
```

This is essential to attribute gains to graph structure itself.

---

# 126. Additional control: metadata-only

A simpler control can use:

```text paper date
section
citation metadata
```

without graph relations.

This answers:

```text does the improvement come from relationships
or simply from richer metadata?
```

This is optional but useful if metadata becomes heavily used.

---

# 127. Graph-aware benchmark diagnostics

For each question, persist:

```text relation_required
relation_family
minimum_path_length
number_of_required_evidence_units
```

These are benchmark annotations.

They must not be supplied to the live retrieval model.

They are for:

```text analysis
stratification
evaluation
```

only.

---

# 128. Minimum required path length

A useful diagnostic:

```text 0
single-node evidence

1
one relation needed

2
two-step relationship

3+
longer chain
```

Do not force all questions into the graph.

Some scientific questions are genuinely one-hop.

The benchmark should reflect that.

---

# 129. Graph usefulness by path length

A meaningful analysis is:

```text path length = 0
graph gain

path length = 1
graph gain

path length = 2+
graph gain
```

This can reveal:

```text graph only helps complex questions
```

or:

```text graph helps even simple relationship retrieval
```

Both are informative.

---

# 130. Graph usefulness by relation type

Likewise:

```text DEFINES
REPORTS
SUPPORTS
PRECEDES
UPDATES
CONFLICTS_WITH
```

can be analyzed separately.

The goal is:

```text identify where graph structure actually contributes
```

rather than treating all edges equally.

---

# 131. V7 integration with adaptive routing

Only after the graph-alone experiment is stable, consider:

```text Question
↓
Compass
↓
initial retrieval
↓
V3 failure prediction
↓
graph escalation
↓
answer
```

Potential policy:

```text simple / high-confidence
→ baseline retrieval

difficult / likely failure
→ graph-assisted retrieval
```

This creates a selective graph system.

However, it adds another variable.

Therefore it should be a later experiment.

---

# 132. Selective graph escalation

A future policy might use:

```text failure probability > threshold
```

to trigger graph retrieval.

Metrics:

```text graph escalation coverage
graph rescue rate
unnecessary graph invocation
cost
latency
```

This directly connects V7 to the original AtlasRAG goal:

```text spend additional computation only when it is useful
```

Do not optimize the threshold on the test set.

---

# 133. Graph + V2 + V3 full architecture

A mature combined architecture could become:

```text
                 Question
                    |
                    v
             Pre-retrieval route
                    |
                    v
             Initial retrieval
                    |
                    v
        Retrieval-state features
                    |
                    v
            V3 failure detector
             /              \
        sufficient          failure
           |                  |
           |                  v
           |           graph-assisted
           |             retrieval
           |                  |
           └──────────┬───────┘
                      v
                 evidence set
                      |
                      v
                    answer
                      |
                      v
                V2 verification
                      |
             claim/citation audit
```

This is a future architecture, not the first V7 experiment.

---

# 134. Do not stack everything simultaneously

Avoid the implementation:

```text Compass
+
V3
+
graph
+
V2
+
new embedding
+
new reranker
```

in one experiment.

If the result changes, attribution becomes impossible.

Use:

```text one new variable at a time
```

whenever practical.

---

# 135. V7 statistical strategy

For retrieval metrics:

```text paired bootstrap
```

is useful.

For binary question success:

```text paired sign test
McNemar's test
```

may be appropriate.

For continuous latency/cost:

```text paired differences
bootstrap confidence intervals
```

can be used.

Choose one coherent statistical plan before looking at final results.

---

# 136. Multiple comparisons

V7 may contain many conditions.

Avoid cherry-picking the one comparison that looks strongest.

Define:

```text primary comparison
```

before analysis.

A good primary comparison is:

```text V7-A baseline
vs
best pre-registered / predefined graph condition
```

Other experiments should be treated as:

```text ablations
diagnostics
secondary analyses
```

This reduces accidental overclaiming.

---

# 137. Primary success criteria

Do not define success as:

```text graph recall > baseline
```

alone.

A better operational criterion could require:

```text evidence quality improvement
```

without an unacceptable:

```text cost/latency increase
```

For example:

```text graph improves difficult-question evidence recall
while maintaining reasonable context and latency
```

The exact threshold must be chosen before results where feasible.

---

# 138. Negative result policy

If:

```text graph does not improve retrieval
```

record:

```text REJECT / DEFER
```

and preserve the analysis.

Potential explanation:

```text structure-aware retrieval already captures the needed relationships
```

or:

```text graph extraction quality was insufficient
```

or:

```text benchmark lacks relationship-heavy failures
```

A negative V7 result is not wasted work.

It can refine the research roadmap.

---

# 139. Positive result policy

If the graph improves:

```text evidence recall
```

but not:

```text answer quality
```

the conclusion should be:

```text graph improves retrieval evidence acquisition,
but generation remains a bottleneck under this evaluation
```

That is more precise than saying:

```text graph improves RAG performance
```

without qualification.

---

# 140. V7 experiment order

Exact recommended order:

```text 1. inspect V6 final decision

2. freeze V6 artifacts

3. identify relationship-heavy failure categories

4. inspect current repository architecture

5. define minimum graph schema

6. define provenance schema

7. implement deterministic graph construction

8. build small pilot graph

9. manually audit nodes/edges

10. benchmark graph construction cost

11. freeze graph schema version

12. create V7 benchmark subset / additions

13. human-review benchmark

14. lock benchmark

15. run V7-A baseline

16. run V7-B graph index only

17. run V7-C one-hop expansion

18. run semantic-expansion control

19. run V7-D relation-aware reranking

20. run relation-family ablations

21. run V7-E relation-specific expansion if justified

22. run V7-F combined condition

23. analyze rescue/regression cases

24. run answer evaluation

25. run citation/provenance evaluation

26. integrate V2 only if retrieval effect is established

27. integrate V3 only if graph-alone effect is established

28. compute paired statistics

29. lock raw outputs

30. write V7 decision
```

Do not skip directly to the combined architecture.

---

# 141. Repository inspection commands

Begin with:

```powershell
cd <AtlasRAG-repo>

$env:PYTHONPATH="src"

python -m pytest -q

git status --short
git log --oneline --decorate -10

Get-ChildItem src/atlasrag
Get-ChildItem src/atlasrag/bench
Get-ChildItem src/atlasrag/retrieval
Get-ChildItem scripts
```

Then inspect V6 artifacts.

Do not assume module names from this roadmap are already present.

---

# 142. Suggested module boundaries

Only if the current architecture has no equivalent abstraction:

```text
src/atlasrag/graph/
    __init__.py
    schema.py
    build.py
    store.py
    query.py
    provenance.py
```

Potential scripts:

```text
scripts/build_graph.py
scripts/audit_graph.py
scripts/inspect_graph.py
scripts/run_v7.py
scripts/analyze_v7.py
```

Use the project's actual naming conventions.

Do not create duplicate functionality.

---

# 143. Tests

Minimum test groups:

```text graph schema validation
node ID stability
edge direction
provenance preservation
entity normalization
one-hop traversal
neighbor caps
hop limits
context budget
graph cache correctness
graph/source mismatch detection
failed extraction handling
```

Add regression tests for every bug found during development.

Do not rely only on one end-to-end test.

---

# 144. Deterministic tests

A deterministic fixture should contain a tiny graph such as:

```text A --defines--> X
X --reported_by--> B
B --precedes--> C
C --updates--> X
```

Then verify:

```text one-hop expansion
relation filtering
path retrieval
directionality
provenance
```

This makes graph behavior independently testable.

---

# 145. Benchmark fixture

Create a minimal benchmark fixture with:

```text one SIMPLE
one MULTI_HOP
one TEMPORAL
one CONFLICTING
one CHAIN
```

when each type is meaningful.

Use it to validate:

```text graph construction
retrieval
evaluation
```

before running the full corpus.

---

# 146. Graph/source consistency test

A useful invariant:

```text every graph node points to an existing source evidence object
every important edge points to valid nodes
```

If not:

```text graph is invalid
```

Do not silently drop broken references during evaluation.

---

# 147. Manifest checksum

Hash:

```text graph schema
node file
edge file
corpus manifest
benchmark
configuration
```

A final V7 experiment manifest should contain enough information to detect accidental mixing of versions.

---

# 148. Final result tables

Recommended retrieval table:

```text
Condition
Evidence recall
Multi-hop recall
Temporal recall
Conflict recall
Chain recall
Context tokens
p50 latency
p95 latency
Cost
```

Recommended answer table:

```text
Condition
Answer correctness
Groundedness
Citation precision
Citation completeness
Unsupported claim rate
Cost
Latency
```

Recommended graph table:

```text
Graph version
Nodes
Edges
Edge precision
Build time
Storage
Provider calls
Tokens
```

Do not report only one headline number.

---

# 149. Failure analysis table

Recommended fields:

```text
question_id
type
baseline_result
graph_result
graph_rescued
graph_regressed
root_cause
edge_type
source_provenance
notes
```

This makes failure analysis reproducible.

---

# 150. V7 decision framework

At the end, choose:

```text KEEP
```

when graph retrieval produces meaningful, repeatable evidence gains with acceptable operational cost.

Choose:

```text KEEP WITH QUALIFIERS
```

when improvements are concentrated in specific categories.

Choose:

```text REJECT
```

when the graph adds complexity without useful evidence improvement.

Choose:

```text DEFER
```

when graph construction quality or benchmark size is insufficient to make a reliable decision.

---

# 151. Potential V7 outcomes and roadmap effects

### If graph helps multi-hop

Next direction may focus on:

```text path-aware retrieval
```

### If graph helps temporal questions

Next direction may focus on:

```text temporal evidence models
```

### If graph helps citation provenance

Next direction may focus on:

```text evidence-graph verification
```

### If graph mainly increases noise

Next direction may focus on:

```text graph confidence filtering
```

### If graph adds little

The next step may return to:

```text V3 selective escalation
```

or another evidence-supported bottleneck.

The roadmap should be evidence-driven.

---

# 152. V7 contribution framing

Possible contribution types include:

```text empirical retrieval finding
```

or:

```text provenance-aware retrieval architecture
```

or:

```text controlled evaluation of evidence graphs for scientific RAG
```

The exact claim must follow the measured result.

Do not claim:

```text \"new graph RAG architecture\"
```

unless the implementation and literature support that level of novelty.

---

# 153. Resume / portfolio framing

Do not update the resume before results are locked.

Possible wording after successful measurement:

```text
Designed and evaluated provenance-aware evidence graphs for scientific RAG, improving retrieval of multi-hop and structured evidence under controlled benchmarks.
```

Only retain:

```text provenance-aware
multi-hop
structured evidence
improved retrieval
```

if each was actually implemented and measured.

---

# 154. Documentation deliverables

Suggested documents:

```text
01_V7_GRAPH_SCHEMA.md
02_V7_GRAPH_EXTRACTION_AUDIT.md
03_V7_BENCHMARK_SPEC.md
04_V7_EXPERIMENT_MATRIX.md
05_V7_RESULTS.md
06_V7_FAILURE_ANALYSIS.md
07_V7_PROVENANCE_ANALYSIS.md
08_V7_DECISION.md
```

Raw outputs:

```text
data/v7/
experiments/v7/
```

Follow existing project conventions if they differ.

---

# 155. Minimal V7 pilot

If time or data is limited, the smallest useful pilot is:

```text one relationship-heavy question type

one relation family

small audited graph

one-hop expansion

semantic expansion control

frozen V6 baseline

retrieval-only metrics

manual failure analysis
```

A MULTI_HOP-only pilot is acceptable if V6 clearly identifies multi-hop evidence as the dominant bottleneck.

Do not build the entire graph ontology for a pilot.

---

# 156. What not to do

Do not:

```text build a giant knowledge graph first

use an LLM to infer every edge without auditing

treat citation links as support links

collapse all scientific entities into one namespace

ignore units and uncertainty

use publication order as temporal truth

use gold paths at inference time

expand unlimited graph hops

increase context budget without reporting it

change embedding/reranker/answer model simultaneously

train graph extraction on the target benchmark test set

hide graph construction cost

overwrite frozen V6 results

claim universal scientific reasoning
```

---

# 157. V7 mental model

Think of the evolution as:

```text
V1
Question
  ↓
choose retrieval strategy

V2
Answer claims
  ↓
verify evidence

V3
Retrieval state
  ↓
predict failure

V4
larger benchmark
  ↓
retest assumptions

V5
new scientific domain
  ↓
test transfer

V6
scientific evidence structures
  ↓
preserve tables/equations/numeric structure

V7
evidence relationships
  ↓
connect those structures
  ↓
retrieve evidence paths
  ↓
preserve provenance
  ↓
verify answer
```

The key question is:

```text
Does knowing how scientific evidence is connected
help us acquire the evidence more reliably?
```

Not:

```text
Can we build a graph?
```

---

# 158. Scientific interpretation rule

A graph result is strongest when the mechanism is understandable.

For example:

```text
baseline missed result paragraph

graph retrieved table
because the table was linked to the result section
through an explicit reference

answer improved
```

That is a useful scientific explanation.

By contrast:

```text
graph model got +4%
```

without understanding why is weaker.

The final analysis should prioritize:

```text mechanism
failure mode
tradeoff
```

over raw score.

---

# 159. Reproducibility release checklist

Before any public release:

```text [ ] graph schema version recorded
 [ ] graph build manifest saved
 [ ] graph extraction outputs preserved
 [ ] corpus version recorded
 [ ] benchmark version recorded
 [ ] train/validation/test split recorded
 [ ] retrieval configuration recorded
 [ ] answer model recorded
 [ ] graph configuration recorded
 [ ] provider instrumentation saved
 [ ] raw per-question results saved
 [ ] graph audit results saved
 [ ] statistical analysis saved
 [ ] final Git commit recorded
 [ ] historical V1–V6 artifacts preserved
```

Do not release only:

```text final numbers
```

without the evidence needed to reconstruct them.

---

# 160. Final rule for the next AI agent

Start with the actual repository and the final V6 decision.

Do not assume graph retrieval is justified.

Do not assume the current V6 system needs a graph.

Do not create a large ontology before identifying relationship-heavy failures.

Do not treat generated graph edges as truth.

Do not lose source provenance.

Do not mix graph construction, retrieval, routing, verification, and answer generation into one opaque experiment.

Do not give the graph a larger context budget without a matched control.

Do not use gold graph paths or benchmark annotations at inference time.

Do not silently change the V6 baseline.

Do not hide graph construction cost.

Do not claim graph reasoning is universally beneficial.

The correct workflow is:

```text
inspect V6
↓
confirm relationship bottleneck
↓
freeze V6
↓
define minimal graph schema
↓
build deterministic pilot
↓
audit edges
↓
measure graph quality/cost
↓
freeze graph version
↓
lock V7 benchmark
↓
run baseline
↓
run one-hop graph
↓
run semantic expansion control
↓
run relation-aware ablations
↓
analyze rescues/regressions
↓
evaluate answer + citations
↓
integrate V2/V3 only after graph-alone evidence
↓
lock raw results
↓
write V7 decision
```

That is Week 16.
