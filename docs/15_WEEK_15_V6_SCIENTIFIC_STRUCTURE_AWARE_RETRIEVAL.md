# AtlasRAG — Week 15: V6 Scientific-Structure-Aware Retrieval & Evidence Representation

## 1. Purpose

Week 14 treated AtlasRAG as a transfer problem:

> **Does an adaptive retrieval methodology learned or designed in one scientific domain retain useful behavior under domain shift?**

Week 15 moves to the next research question only if the evidence from V5 justifies it.

The focus is no longer only:

```text
Which chunks are semantically relevant?
```

but:

```text
What kind of scientific evidence is contained inside those chunks?
```

Scientific papers are not ordinary prose documents.

Important evidence can live inside:

```text
tables

equations

figures / captions

units

parameter-value pairs

experimental conditions

temporal relationships

method/result/conclusion structures
```

A plain text chunker may separate these pieces or destroy some of their relationships.

V6 therefore asks whether retrieval quality can improve when AtlasRAG becomes explicitly aware of scientific evidence structure.

The intended progression is:

```text
V1
question-aware retrieval routing

        ↓

V2
claim/evidence verification

        ↓

V3
retrieval-state-aware failure prediction

        ↓

V4
larger scientific benchmark

        ↓

V5
cross-domain transfer

        ↓

V6
scientific-structure-aware retrieval
```

The goal is not to immediately build a giant multimodal scientific RAG system.

The goal is to isolate one representation problem at a time and determine whether explicit structure improves evidence acquisition.

---

# 2. Why V6 should follow V5 rather than precede it

V6 should not be implemented merely because tables and equations sound interesting.

The V5 failure analysis should determine whether structural evidence is actually a major bottleneck.

For example, suppose V5 shows that difficult cases disproportionately involve:

```text
table rows

equations

parameter/value pairs

temporal comparisons
```

Then V6 has a clear motivation.

If instead V5 shows that most failures come from:

```text
poor benchmark quality

PDF extraction corruption

vocabulary mismatch

weak answer generation
```

then a table/equation retrieval system may be the wrong next experiment.

The first action in Week 15 is therefore:

```text
inspect V5 failure taxonomy
↓
confirm structural-evidence bottleneck
↓
freeze the V5 evidence
↓
only then design V6
```

Do not retroactively reinterpret V5 failures to justify V6.

---

# 3. V6 primary research question

Primary question:

> **Can scientific-structure-aware evidence representations improve retrieval of answer-critical information compared with a conventional prose-chunk retrieval baseline?**

Secondary questions:

```text
1. Are table-aware representations useful for quantitative questions?

2. Are equation-aware representations useful for formula / parameter questions?

3. Does preserving units and parameter-value relationships improve retrieval?

4. Does temporal structure improve retrieval of changing scientific claims?

5. Which structural representation provides the largest marginal gain?

6. Does structure-aware retrieval reduce retrieval failures without increasing cost excessively?

7. Does the benefit survive on unseen papers and unseen domains?

8. Can the structural evidence layer be added without rebuilding the entire AtlasRAG architecture?
```

These are hypotheses.

Do not state them as established results until measured.

---

# 4. Core idea

The baseline representation is approximately:

```text
PDF
 ↓
text extraction
 ↓
section text
 ↓
fixed-size chunks
 ↓
embedding / BM25 / reranking
```

V6 introduces structured evidence units:

```text
PDF
 ↓
scientific document parser
 ↓
 ├─ prose blocks
 ├─ tables
 ├─ equations
 ├─ captions
 ├─ metadata
 └─ temporal / section relationships
        ↓
structured evidence index
        ↓
retrieval
```

The key concept is:

```text
retrieve evidence units
```

rather than assuming that every useful fact is naturally represented by a prose chunk.

---

# 5. V6 must remain a retrieval experiment

Do not change everything at once.

The clean first experiment should keep as much as possible frozen:

```text
question benchmark
answer model
answer prompt
LLM generation settings
initial routing policy
reranker model
metrics
```

The primary independent variable should be:

```text
evidence representation / retrieval strategy
```

For example:

```text
R0 = current prose chunking
R1 = prose + table units
R2 = prose + equation units
R3 = prose + structured numeric units
R4 = prose + temporal links
R5 = combined structure-aware retrieval
```

Do not begin with R5.

Start with isolated components so that causal interpretation remains possible.

---

# 6. Scientific evidence unit taxonomy

Define the evidence representation before implementation.

A useful first taxonomy is:

```text
PROSE

TABLE

EQUATION

FIGURE_CAPTION

NUMERIC_RESULT

METHOD_BLOCK

TEMPORAL_RELATION
```

Not every category must be implemented immediately.

The minimum practical first version could be:

```text
PROSE
TABLE
EQUATION
NUMERIC_RESULT
```

Temporal reasoning can be added as a separate stage if the benchmark shows sufficient demand.

---

# 7. Why tables deserve separate treatment

Tables frequently contain the most precise information in a paper.

A prose paragraph may say:

```text
The model agrees well with the observations.
```

while a table may contain:

```text
parameter | estimate | uncertainty
H0        | ...      | ...
Ωm        | ...      | ...
```

A prose-only chunking strategy can fail when:

```text
table text is dropped

columns become disconnected

row labels lose association

units are separated

notes are detached from values
```

Therefore V6 should represent a table as a structured object rather than merely flattening it into arbitrary text.

---

# 8. Minimum table representation

A table retrieval record might contain:

```json
{
  "type":"table",
  "paper_id":"paper-001",
  "section":"Results",
  "caption":"Parameter constraints",
  "headers":["Parameter","Estimate","Uncertainty"],
  "rows":[
    ["X","1.23","0.04"]
  ],
  "units":{},
  "source_page":7
}
```

The exact schema should follow the existing repository style.

The important principle is:

```text
row identity
+
column identity
+
unit/context
```

must remain recoverable.

---

# 9. Table serialization for retrieval

A table still needs a searchable textual representation.

A controlled serialization could look like:

```text
TABLE: Parameter constraints
Columns: Parameter | Estimate | Uncertainty
Row: X | 1.23 | 0.04
```

The serialization should be deterministic.

Avoid verbose natural-language generation just to convert tables into text.

That would introduce an unnecessary LLM dependency and make reproduction harder.

The structured source record should remain authoritative.

The serialized form exists for retrieval.

---

# 10. Table-aware query routing

Do not assume every numeric question needs table retrieval.

A query may mention:

```text
"What value did the authors report?"
```

but the answer may appear in:

```text
abstract

results paragraph

caption

table
```

Therefore the first table-aware system should support:

```text
prose candidates
+
table candidates
```

and let retrieval ranking determine relevance.

A later experiment can test explicit table routing as a separate policy.

---

# 11. Equation evidence

Equations present a different problem.

A scientific answer can depend on:

```text
symbol definitions

functional relationship

constants

units

assumptions
```

Flattening an equation into broken PDF text can produce retrieval noise such as:

```text
Q = xi H rho
```

becoming disconnected fragments.

The representation should preserve the equation as one evidence unit whenever extraction quality allows it.

---

# 12. Minimum equation record

Example conceptual schema:

```json
{
  "type":"equation",
  "paper_id":"paper-001",
  "section":"Model",
  "latex":"Q = \\xi H \\rho",
  "number":"(4)",
  "context":"interaction rate",
  "source_page":5
}
```

Do not claim full mathematical understanding from this record.

The initial objective is more modest:

```text
retrieve the correct equation and its context
```

before attempting symbolic reasoning.

---

# 13. Equation-context coupling

The equation alone may not answer the question.

For example:

```text
Equation (4)

+

paragraph immediately before it
```

may define the symbols.

Therefore represent relationships such as:

```text
equation → nearby definition block

equation → equation caption / number

equation → surrounding section
```

This is an important design principle:

```text
structure should preserve context, not isolate it
```

---

# 14. Parameter-value evidence

Many scientific questions are really about relationships like:

```text
parameter
→ value
→ unit
→ uncertainty
→ experimental/model condition
```

For example:

```text
X = 1.23 ± 0.04 [unit]
```

The answer-critical evidence is not just the number `1.23`.

It is the complete tuple:

```text
(X, 1.23, 0.04, unit, condition)
```

A V6 numeric representation should preserve these relationships where they can be extracted reliably.

---

# 15. Numeric extraction must not become numeric hallucination

A critical rule:

```text
parser output ≠ truth
```

If PDF extraction produces:

```text
1.23 ± 0.04
```

and the parser incorrectly reads:

```text
1.23 ± 0.4
```

the structured index is now wrong.

Therefore every structured extractor needs quality diagnostics.

Track:

```text
successful extraction
partial extraction
malformed extraction
missing value
unit corruption
symbol corruption
```

Do not silently convert uncertain extraction into authoritative evidence.

---

# 16. Temporal evidence representation

Temporal reasoning is different from merely storing publication dates.

A temporal question may ask:

```text
How did the reported estimate change from earlier work to later work?
```

The evidence structure is:

```text
earlier result
↓
later result
↓
change / comparison
```

The system needs to preserve:

```text
source date
scientific quantity
reported value
method/context
```

A document being newer is not enough to make it a temporal evidence source.

---

# 17. Temporal relation schema

Conceptual example:

```json
{
  "type":"temporal_relation",
  "anchor":"X",
  "earlier":{
    "paper_id":"paper-A",
    "date":"2020",
    "value":"..."
  },
  "later":{
    "paper_id":"paper-B",
    "date":"2025",
    "value":"..."
  },
  "relation":"updated_estimate"
}
```

The exact relation taxonomy should be small.

Possible initial relations:

```text
UPDATED_ESTIMATE
REVISED_METHOD
FOLLOW_UP_RESULT
CONFLICT_REPORTED
```

Do not build a large ontology before proving it is useful.

---

# 18. Evidence graph concept

V6 can eventually represent scientific evidence as a graph:

```text
Paper
 |
 ├── Section
 │    ├── Prose
 │    ├── Equation
 │    ├── Table
 │    └── Figure caption
 |
 └── Metadata
```

Cross-document relationships can then be represented as:

```text
Paper A
  |
  └── reports X
          |
          v
Paper B
  |
  └── updates X
```

But the first implementation does not need a graph database.

A lightweight relational or JSON representation is enough for the experiment.

---

# 19. Retrieval architecture options

There are several possible implementations.

### Option A — unified index

All evidence units enter the same retrieval space:

```text
prose
+
tables
+
equations
+
numeric units
```

Pros:

```text
simple serving path
single ranking stage
```

Cons:

```text
representation competition
possible ranking bias toward prose
```

### Option B — type-specific indices

```text
prose index

table index

equation index
```

Results are fused later.

Pros:

```text
explicit control
better ablation visibility
```

Cons:

```text
more infrastructure
fusion complexity
```

For research, Option B may be easier to analyze even if Option A becomes preferable for deployment.

---

# 20. Recommended V6 first architecture

Start with a parallel retrieval design:

```text
                 Question
                    |
          ┌─────────┼─────────┐
          v         v         v
       prose      tables   equations
       search      search      search
          |         |         |
          └─────────┼─────────┘
                    v
                 fusion
                    ↓
                 reranker
                    ↓
              final evidence
```

This makes the contribution explicit.

It also allows component-level failure inspection.

---

# 21. Do not change the reranker first

A common mistake would be:

```text
add structured retrieval
+
replace reranker
+
change embedding model
+
change chunking
```

and then interpret any result as evidence for structural retrieval.

Do not do this.

The initial V6 comparison should keep the reranking model unchanged where technically possible.

Only later should reranker compatibility be studied as a separate ablation.

---

# 22. V6 experimental ladder

Use a staged matrix.

### V6-A — frozen prose baseline

Current baseline, unchanged.

Purpose:

```text
reference retrieval quality
```

### V6-B — prose + table retrieval

Only tables are added.

Purpose:

```text
measure table-specific gain
```

### V6-C — prose + equation retrieval

Only equations are added.

Purpose:

```text
measure equation-specific gain
```

### V6-D — prose + numeric structured evidence

Explicit parameter/value/unit representations.

Purpose:

```text
measure quantitative retrieval gain
```

### V6-E — prose + temporal relations

Only temporal evidence structures are added.

Purpose:

```text
measure temporal retrieval gain
```

### V6-F — combined structure-aware retrieval

```text
prose
+
table
+
equation
+
numeric
+
temporal
```

Purpose:

```text
measure aggregate system benefit
```

Do not skip directly to V6-F.

---

# 23. Benchmark requirements

V6 needs a dedicated structural-evidence benchmark subset.

The existing benchmark can remain frozen.

Create a new V6 benchmark version rather than rewriting historical questions.

Suggested categories:

```text
TABLE_LOOKUP
EQUATION_LOOKUP
PARAMETER_VALUE
UNIT_SENSITIVE
TEMPORAL_COMPARISON
MIXED_STRUCTURE
```

Each question must identify what makes the structural representation necessary or materially useful.

---

# 24. Table benchmark examples — structure only

Good question pattern:

```text
What value of parameter X did the authors report for condition Y?
```

Expected evidence:

```text
table row
+
column heading
+
condition
```

Bad question pattern:

```text
What is the main conclusion of the paper?
```

That is not a table-specific retrieval task merely because the paper contains a table.

---

# 25. Equation benchmark examples — structure only

Good question pattern:

```text
What equation does the paper use to define X?
```

or:

```text
According to Eq. (4), how is X related to Y?
```

Expected evidence:

```text
equation
+
local symbol definition
```

Bad question:

```text
What model does the paper propose?
```

unless the answer genuinely depends on a mathematical formulation not recoverable from the prose alone.

---

# 26. Unit-sensitive benchmark

Units deserve separate attention because scientific answers can be numerically similar but dimensionally different.

Example structure:

```text
10 km
vs
10 km/s
```

A retrieval system that returns only:

```text
10
```

has not preserved sufficient evidence.

A unit-sensitive question should require the full scientific quantity.

---

# 27. Uncertainty-sensitive benchmark

Similarly:

```text
1.23
```

is not equivalent to:

```text
1.23 ± 0.04
```

A quantitative benchmark should test whether retrieval preserves:

```text
estimate
uncertainty
unit
condition
```

where relevant.

This becomes especially important for scientific answer evaluation later.

---

# 28. Mixed-structure questions

The hardest cases may require:

```text
table
+
prose
```

or:

```text
equation
+
parameter definition
```

or:

```text
earlier result
+
later result
+
table values
```

These should be treated separately from single-structure questions.

Otherwise a combined system may appear strong simply because most questions require only one easy evidence type.

---

# 29. Gold evidence design

V6 requires precise evidence labels.

Each question should ideally retain:

```text
gold evidence ID
evidence type
paper ID
section
page if available
required fields
```

For a table question:

```text
table ID
row
column
```

For an equation question:

```text
equation ID
symbol-definition context
```

For temporal questions:

```text
earliest evidence
later evidence
required comparison relation
```

The goal is not merely to know:

```text
which chunk is gold?
```

but:

```text
what structural information must be recovered?
```

---

# 30. Alternative evidence must remain possible

Do not make the benchmark falsely exact.

The same scientific fact may be supported by:

```text
Table 2
```

and:

```text
Results paragraph
```

Both may be valid evidence.

Therefore V6 evaluation should distinguish:

```text
exact structural gold recovery
```

from:

```text
answer-supporting evidence recovery
```

This follows the same lesson from the earlier benchmark work: exact gold-chunk recall can be useful but conservative.

---

# 31. Structural retrieval metrics

Primary retrieval metrics:

```text
Recall@k
MRR
nDCG
structural-evidence recall
```

For quantitative questions add:

```text
field completeness
```

For example:

```text
parameter recovered?       yes
value recovered?           yes
uncertainty recovered?     yes
unit recovered?            no
```

This can expose failures hidden by ordinary chunk recall.

---

# 32. Field-level completeness

Define a question-specific evidence schema.

Example:

```text
Required fields:

parameter
value
uncertainty
unit
condition
```

A retrieved result may have:

```text
parameter = yes
value = yes
uncertainty = yes
unit = no
condition = yes
```

Then structural completeness is:

```text
4 / 5
```

This should not replace standard recall.

It complements it.

---

# 33. Equation completeness

For equation tasks, a similar schema can be used:

```text
equation
symbol definitions
relevant assumptions
parameter context
units if specified
```

An equation without symbol context may be insufficient even when retrieved exactly.

This is an important limitation of naive exact-match evaluation.

---

# 34. Temporal completeness

For temporal questions, define:

```text
earlier result recovered
later result recovered
same quantity confirmed
comparison relation recoverable
```

A system that retrieves only the later paper should not receive full temporal evidence credit.

---

# 35. Answer evaluation

After retrieval-only experiments are stable, run end-to-end answer evaluation.

Use the same answer model and prompt across conditions.

Measure:

```text
answer correctness
relevance
groundedness
citation correctness
citation completeness
unsupported-claim rate
latency
tokens / cost
```

The generation model must not change between:

```text
V6-A
...
V6-F
```

unless the experiment explicitly studies model interaction.

---

# 36. Citation provenance

Structured retrieval should preserve provenance such as:

```text
paper
section
page
structure type
structure ID
```

For example:

```text
paper=abc
page=7
section=Results
type=table
table_id=Table_2
```

This is better than returning only a flattened string.

It also creates a clean interface for V2 evidence verification.

---

# 37. V6 + V2 connection

V6 should be designed so that V2 can later verify structured claims.

Conceptually:

```text
Answer claim
      ↓
Citation
      ↓
Structured evidence
      ↓
verify:
value
unit
uncertainty
comparison
```

This is especially valuable for scientific quantitative claims.

Do not implement automatic repair at the same time as the first V6 retrieval study.

Detection first.

---

# 38. V6 + V3 connection

V3 failure prediction can eventually use structural retrieval-state features.

Potential features:

```text
number of table candidates
number of equation candidates
structural evidence coverage
prose/structure disagreement
field completeness
unit coverage
```

For example:

```text
question asks for parameter + uncertainty

retrieval finds parameter
but no uncertainty

→ likely incomplete retrieval
```

This is a natural extension of retrieval-state-aware failure detection.

But it must be evaluated separately from the basic V6 retrieval result.

---

# 39. Cost control

Structure-aware retrieval may increase:

```text
index size
storage
embedding calls
retrieval calls
reranking calls
latency
```

Measure each separately.

A system that improves recall from:

```text
0.70 → 0.72
```

but doubles latency may not be operationally attractive.

Likewise, a small cost increase for a large reduction in scientific numerical errors could be worthwhile.

The decision should be evidence-driven.

---

# 40. Indexing cost

Track:

```text
number of source documents
number of prose units
number of table units
number of equation units
number of numeric units
index build time
index size
embedding count
```

Do not count generated duplicates as free.

If the same information is embedded multiple times, record it.

---

# 41. Retrieval cost

For each query track:

```text
retrieval calls
candidate count
reranker inputs
LLM calls if any
tokens
latency
```

The first V6 design should preferably add retrieval complexity rather than LLM complexity.

An LLM-generated table description might look convenient, but it makes the experiment harder to reproduce and potentially introduces semantic distortion.

---

# 42. Structural extraction quality gate

Before running the benchmark, establish extraction quality.

Create a small manually inspected sample of:

```text
20 tables
20 equations
20 numeric results
```

or a justified smaller/larger sample depending on corpus size.

Record:

```text
correct
partial
incorrect
missing
```

If extraction is poor, do not interpret retrieval results as meaningful.

---

# 43. PDF extraction failure taxonomy

Useful categories:

```text
TABLE_NOT_DETECTED
TABLE_STRUCTURE_BROKEN
COLUMN_ORDER_WRONG
ROW_LABEL_LOST
UNIT_LOST
EQUATION_NOT_DETECTED
SYMBOL_CORRUPTED
EQUATION_NUMBER_LOST
CAPTION_DETACHED
PAGE_REFERENCE_LOST
```

Keep this taxonomy separate from retrieval failure.

Otherwise:

```text
parser failure
```

may be misreported as:

```text
retriever failure
```

---

# 44. Benchmark contamination

Do not build the V6 question from a table and then accidentally expose the answer in:

```text
question text
metadata
filename
retrieval configuration
```

For example, avoid filenames such as:

```text
paper123_Table2_H0_73.json
```

in a benchmark path that a model or script can inspect.

Use opaque IDs.

---

# 45. Leakage audit

Check that the following never enter inference features:

```text
gold evidence ID
gold table row
gold equation number
gold answer
human label
Oracle route
benchmark category when category is not available in deployment
```

A structural retriever can use:

```text
question
retrieved candidate metadata
```

but not:

```text
knowledge of which candidate is gold
```

---

# 46. Embedding strategy

Possible choices:

```text
reuse current embedding model
```

first.

This isolates the effect of structural representation.

Later experiments can test:

```text
structure-specific embeddings
multivector representations
specialized scientific embeddings
```

But those are separate variables.

Do not combine:

```text
new embedding
+
new structure representation
+
new reranker
```

in the first result.

---

# 47. Fusion strategy

If multiple evidence types are searched independently, start with a simple fusion method.

For example:

```text
RRF across prose/table/equation result lists
```

or a normalized score combination.

The first goal is to answer:

```text
does structure-aware retrieval help?
```

not:

```text
what is the globally optimal fusion function?
```

Fusion optimization can be a later ablation.

---

# 48. Type-aware reranking

A later variant may append evidence-type information:

```text
[TYPE=TABLE]
...
```

or:

```text
[TYPE=EQUATION]
...
```

before reranking.

This is a controlled experiment because type information could help the reranker distinguish:

```text
numeric table
```

from:

```text
similar prose mentioning the same parameter
```

But first measure retrieval without modifying the reranker.

---

# 49. Structural negatives

V6 needs hard negatives.

Examples:

```text
correct paper, wrong table
correct parameter, wrong condition
correct equation family, wrong equation
same value, wrong unit
same observable, earlier unrelated measurement
```

These are much more informative than random unrelated chunks.

---

# 50. Exact quantity integrity

A particularly important scientific failure is:

```text
same symbol
wrong quantity
```

or:

```text
same value
wrong uncertainty
```

or:

```text
same result
wrong condition
```

V6 evaluation should explicitly detect these.

A retrieved chunk can be semantically relevant but scientifically wrong for the specific question.

This is one reason structure-aware retrieval matters.

---

# 51. Unit normalization

If unit normalization is implemented, keep it deterministic.

For example:

```text
m
cm
mm
```

may be convertible, but the original source unit should remain available.

Do not normalize away source information.

Store both:

```text
original_unit
normalized_unit
```

when normalization is used.

The first V6 version can simply preserve original units without conversion.

---

# 52. Numeric parsing safety

Scientific numbers can contain:

```text
1.2e-5

−3.4

0.42 ± 0.07

1.2^{+0.3}_{-0.2}

< 0.05

> 3
```

Do not implement an incomplete parser and then silently call it complete.

Unsupported numeric forms should be recorded as:

```text
unsupported_format
```

rather than incorrectly parsed.

---

# 53. Scientific notation preservation

Keep:

```text
1.2e-5
```

distinct from:

```text
1.2e5
```

and preserve signs.

This may sound obvious, but PDF extraction is a common source of scientific-number corruption.

V6 should include parser regression tests for representative values.

---

# 54. Table row identity

A table answer often depends on the intersection:

```text
row condition
×
column metric
```

A flattened chunk can make the association ambiguous.

The structured representation should therefore permit:

```text
row_id
column_id
cell_value
```

and optionally:

```text
row_label
column_label
```

This allows exact evidence attribution later.

---

# 55. Caption preservation

Captions can contain critical meaning.

For example:

```text
"Results shown for the high-density sample only."
```

If the table is retrieved without its caption, the answer may be interpreted incorrectly.

Therefore table/equation/figure records should retain caption text where available.

---

# 56. Footnote preservation

Table footnotes may define:

```text
special notation
sample exclusions
units
confidence levels
model assumptions
```

Dropping them can change scientific interpretation.

At minimum, track whether a table has footnotes.

If the system cannot reliably associate them, mark the limitation.

---

# 57. Section context

Structural evidence should remain linked to its section.

For example:

```text
Table 3
Results
```

means something different from:

```text
Table 3
Methods
```

Section-aware metadata can help both retrieval and answer grounding.

---

# 58. Figure captions as an optional component

Figures are potentially useful because captions often summarize quantitative findings.

But figure image interpretation is a separate problem from text retrieval.

Therefore the first V6 system should use:

```text
caption text
```

before introducing:

```text
vision-language figure understanding
```

This keeps scope controlled.

---

# 59. Multimodal expansion is not V6-A

Do not immediately build:

```text
PDF images
+
OCR
+
vision model
+
chart interpretation
```

unless V5/V6 evidence demonstrates that this is necessary.

That would turn a focused retrieval experiment into a broad multimodal research project.

V6 should remain primarily about evidence representation.

---

# 60. Temporal graph is separate from publication sorting

Do not implement temporal reasoning as:

```text
sort papers by date
```

That is useful metadata, but it is not temporal evidence reasoning.

A real temporal relation should connect:

```text
same scientific quantity
+
ordered observations
+
meaningful change
```

The benchmark should verify this explicitly.

---

# 61. Evaluation by question family

Overall recall is not enough.

Report:

```text
all questions

TABLE_LOOKUP

EQUATION_LOOKUP

PARAMETER_VALUE

UNIT_SENSITIVE

TEMPORAL_COMPARISON

MIXED_STRUCTURE
```

A system may improve:

```text
TABLE_LOOKUP +20%
```

while having no meaningful effect on:

```text
ordinary prose questions
```

That is a useful and more honest result than a tiny aggregate increase.

---

# 62. Cost-quality frontier

For every V6 condition report:

```text
retrieval recall
answer quality
latency
provider calls
tokens
index size / build cost
```

Construct a quality/cost comparison rather than presenting one metric in isolation.

Possible conclusion patterns:

```text
large quality gain / small cost increase
→ strong candidate

small quality gain / large cost increase
→ weak candidate

large gain only on structural questions
→ targeted use case

no meaningful gain
→ reject or redesign
```

---

# 63. Statistical testing

Use paired comparisons because the same benchmark questions can be run through multiple systems.

Compare:

```text
V6-A vs V6-B
V6-A vs V6-C
V6-A vs V6-D
V6-A vs V6-E
V6-A vs V6-F
```

Use the existing project statistical methodology where possible.

Do not invent a new statistical method solely because it makes the result look more significant.

Report uncertainty intervals.

---

# 64. Error taxonomy

Classify failures as:

```text
STRUCTURE_NOT_EXTRACTED

STRUCTURE_EXTRACTED_BUT_NOT_RETRIEVED

CORRECT_STRUCTURE_WRONG_REGION

CORRECT_REGION_WRONG_FIELD

UNIT_OR_UNCERTAINTY_MISSING

TEMPORAL_LINK_MISSING

ALTERNATIVE_VALID_EVIDENCE

ANSWER_GENERATION_FAILURE

CITATION_FAILURE
```

This separates the real V6 bottleneck from downstream failures.

---

# 65. Structural recall vs answer correctness

A higher structural retrieval score should not automatically be treated as a better final system.

You need to know:

```text
retrieval improvement
↓
answer improvement?
```

Possible outcome:

```text
retrieval recall ↑
answer correctness ↔
```

This can happen when the answer model already has enough evidence or cannot use the structured output effectively.

That is an important result.

---

# 66. Citation correctness may improve before answer accuracy

Structured retrieval could make citations more precise even if final answer accuracy changes little.

For example:

```text
same answer
better citation to Table 2
```

Therefore evaluate:

```text
answer correctness
```

and:

```text
citation correctness
```

separately.

---

# 67. Compatibility with V2 verifier

A V2 verifier can operate over structured evidence more precisely.

For a claim such as:

```text
X = 1.23 ± 0.04
```

it can check fields separately:

```text
value = supported
uncertainty = supported
unit = supported
condition = supported
```

This creates a strong architectural reason to preserve structure even if retrieval gains are modest.

But the architectural value must still be demonstrated rather than assumed.

---

# 68. Compatibility with V3 failure prediction

V3 can later use:

```text
structured evidence coverage
```

as a retrieval-state feature.

Example:

```text
Question requires:
parameter + uncertainty + unit

Initial retrieval state:
parameter = 1
uncertainty = 0
unit = 0

failure probability should rise
```

This is a clear example of how the research versions compose without collapsing into one model.

---

# 69. Possible V6 architecture after validation

If the staged experiments work, the final architecture could become:

```text
Question
   ↓
Adaptive route
   ↓
┌──────────────────────────────┐
│ Scientific Evidence Retrieval│
│                              │
│ prose                        │
│ tables                       │
│ equations                    │
│ numeric units                │
│ temporal relations           │
└──────────────┬───────────────┘
               ↓
             fusion
               ↓
            reranking
               ↓
        evidence state
               ↓
       failure prediction
               ↓
            answer
               ↓
      evidence verification
```

This is a long-term architecture, not the first experiment.

---

# 70. Avoid architecture inflation

A research roadmap can easily become:

```text
router
+
failure detector
+
multimodal retriever
+
graph database
+
LLM verifier
+
agent
```

This makes it difficult to know what improved what.

V6 should remain modular.

Each added component should answer a specific scientific question.

---

# 71. Recommended code organization

Inspect the existing repository before creating directories.

Potential conceptual locations:

```text
src/atlasrag/ingest/
    structure.py
    tables.py
    equations.py

src/atlasrag/retrieval/
    structured.py
    fusion.py

src/atlasrag/bench/
    generate_v6.py
    validate_v6.py

scripts/
    build_structured_index.py
    run_v6.py
    inspect_v6_failures.py
```

These names are suggestions only.

Use the project's actual module organization if equivalent components already exist.

Do not duplicate existing utilities unnecessarily.

---

# 72. Proposed structured schema fields

Every evidence unit should ideally retain:

```text
id
paper_id
section
page
type
raw_text
structured_payload
source_locator
extraction_status
```

Optional fields:

```text
caption
footnotes
units
symbol_definitions
row_id
column_id
temporal metadata
```

The schema should be stable enough to support downstream evaluation.

---

# 73. Raw vs normalized representation

Keep both whenever possible.

For example:

```text
raw_table
```

and:

```text
normalized_table
```

The raw form supports auditing.

The normalized form supports retrieval.

Never discard the original source representation merely because normalization is convenient.

---

# 74. Reproducibility requirement

The structured index must be reproducible from:

```text
corpus version
parser version
extraction configuration
serialization version
embedding model
retrieval configuration
```

Record these in a manifest.

Example:

```json
{
  "corpus_hash":"...",
  "parser_version":"...",
  "serialization_version":"v6.1",
  "embedding_model":"...",
  "retrieval_config":"..."
}
```

Exact keys should match repository conventions.

---

# 75. Do not overwrite baseline indexes

Create separate V6 artifacts.

For example:

```text
data/index_v1/

data/index_v6_structured/
```

or equivalent versioned locations.

Never replace the baseline index with the structured index.

Historical experiments must remain reproducible.

---

# 76. V6 benchmark versioning

Suggested artifacts:

```text
data/bench/questions_v6.jsonl

data/bench/questions_v6_frozen.jsonl

data/bench/v6_review_manifest.json

data/bench/v6_audit.jsonl
```

Exact filenames can differ.

The rule is:

```text
new benchmark → new immutable snapshot
```

Do not silently mutate the earlier benchmark.

---

# 77. Structural benchmark generation

Use generation only to propose candidates.

A candidate pipeline can be:

```text
paper
↓
identify table/equation/numeric structure
↓
construct candidate question
↓
retrieve candidate evidence
↓
structural validation
↓
human review
↓
accept/reject
```

Do not accept candidates because they are structurally formatted.

The question must be answerable and scientifically correct.

---

# 78. Human review checklist for tables

Reviewer should verify:

```text
[ ] question maps to the table
[ ] row identity is correct
[ ] column identity is correct
[ ] units are correct
[ ] uncertainty is correct when relevant
[ ] condition is correct
[ ] answer supported by source
[ ] alternate valid evidence considered
```

---

# 79. Human review checklist for equations

```text
[ ] equation exists in source
[ ] equation number correct if used
[ ] symbols are preserved
[ ] definitions are available
[ ] assumptions are not omitted
[ ] question cannot be answered from unrelated prose alone
[ ] answer supported by equation/context
```

---

# 80. Human review checklist for temporal questions

```text
[ ] evidence has actual ordering
[ ] same quantity/anchor tracked
[ ] earlier evidence verified
[ ] later evidence verified
[ ] requested comparison follows from sources
[ ] no artificial conflict introduced
```

---

# 81. Structural benchmark acceptance rules

Reject when:

```text
answer is directly stated elsewhere and structure is unnecessary

table/equation is unrelated

quantity differs

units do not match

same topic but different scientific entity

temporal relation is merely publication-date difference
```

This preserves the lessons from previous benchmark repair work.

---

# 82. Retrieval ablation matrix

Recommended first matrix:

| ID | Prose | Tables | Equations | Numeric | Temporal |
|---|---|---|---|---|---|
| V6-A | yes | no | no | no | no |
| V6-B | yes | yes | no | no | no |
| V6-C | yes | no | yes | no | no |
| V6-D | yes | no | no | yes | no |
| V6-E | yes | no | no | no | yes |
| V6-F | yes | yes | yes | yes | yes |

This is the core experiment.

Later variants can test fusion and ranking.

---

# 83. Structural ablation by question family

For table questions compare:

```text
V6-A vs V6-B
```

For equation questions:

```text
V6-A vs V6-C
```

For numeric questions:

```text
V6-A vs V6-D
```

For temporal questions:

```text
V6-A vs V6-E
```

This gives direct evidence for whether each representation helps its intended task.

---

# 84. Cross-domain evaluation

V5 asks whether adaptive retrieval transfers across domains.

V6 should ideally evaluate structure-aware retrieval under at least one held-out setting where practical.

Potential matrix:

```text
astro/cosmology → astro/cosmology
astro/cosmology → target domain
```

or, after sufficient data:

```text
domain A → domain B

domain B → domain A

domain C → domain A/B
```

Do not add multiple domains merely for visual complexity.

One rigorous transfer test is preferable to several tiny tests.

---

# 85. Negative transfer is important

Structure-aware retrieval may help one field and hurt another.

For example:

```text
biology + tables → strong gain
cosmology + equations → strong gain
another domain → no gain
```

That is still useful evidence.

Do not average away meaningful domain-specific failures.

---

# 86. Question complexity interaction

Structure-aware retrieval may be especially useful for:

```text
MULTI_HOP
CONFLICTING
TEMPORAL
CHAIN
```

But this is not guaranteed.

Measure interaction between:

```text
question type
×
structure type
```

For example:

```text
TABLE × SIMPLE
TABLE × MULTI_HOP
EQUATION × SIMPLE
EQUATION × CHAIN
```

Only report cells with adequate sample size.

---

# 87. Retrieval-state features for V6

If V3 is active, add structural retrieval-state signals only after the base representation experiment.

Candidate features:

```text
table-candidate count

equation-candidate count

structure-type diversity

best structured score

prose-vs-structure score gap

required-field coverage

structural redundancy
```

These can later feed the failure detector.

Do not use them in the first V6 retrieval comparison if the objective is to isolate structural retrieval itself.

---

# 88. Interaction with routing

Eventually the router could make a decision such as:

```text
ordinary retrieval
```

for simple prose questions, and:

```text
structure-aware retrieval
```

for questions likely requiring scientific tables/equations.

But that is a later adaptive-policy experiment.

First establish:

```text
Does structure-aware retrieval itself help?
```

Then:

```text
Can routing invoke it selectively?
```

This preserves causal order.

---

# 89. Potential structure classifier

A future lightweight classifier may predict:

```text
prose

table

equation

numeric

temporal

mixed
```

from the question alone.

This could become another routing layer.

However, it should not be introduced before the retrieval value of the structural representations is established.

Otherwise the experiment becomes:

```text
classifier accuracy
```

instead of:

```text
retrieval quality
```

---

# 90. Potential query-to-structure matching

A simple heuristic baseline might detect terms such as:

```text
"table"
"Eq."
"equation"
"uncertainty"
"unit"
"reported value"
"upper limit"
```

This can be useful as a cheap routing control.

But keyword presence is not enough to establish scientific structure.

Compare heuristic routing against fixed and learned alternatives when justified.

---

# 91. No hard-coded benchmark answers

Do not add rules like:

```text
if question contains "uncertainty" → retrieve Table 2
```

Such rules would leak benchmark-specific structure.

The system should operate from document/index information, not known test answers.

---

# 92. Long-context alternative baseline

A useful control may be:

```text
retrieve a larger surrounding prose context
```

instead of explicitly building structure-aware units.

This answers an important question:

> **Does structure-aware representation add value beyond simply giving the retriever more text?**

This is a particularly strong ablation.

For example:

```text
Baseline
1800-char prose chunk

Context control
3600-char surrounding window

Structure-aware
explicit table/equation unit
```

If structure-aware retrieval beats both, the evidence is stronger.

---

# 93. Flattened-table control

Another useful control:

```text
flattened table text
```

versus:

```text
structured table
```

This isolates whether the benefit comes from:

```text
including table content
```

or from:

```text
preserving table relationships
```

This is a particularly valuable V6 experiment.

---

# 94. Flattened-equation control

Similarly compare:

```text
broken / plain equation text
```

with:

```text
preserved equation unit
```

The purpose is not to prove mathematical understanding.

It is to test whether preserving the structure improves retrieval.

---

# 95. Strongest baseline

The strongest retrieval control may be:

```text
current strongest validated retrieval
```

rather than merely the cheapest baseline.

If V6 structure-aware retrieval cannot beat the strongest validated baseline, that matters.

The comparison should remain fair:

```text
same corpus
same benchmark
same answer model
same evaluation
```

---

# 96. Oracle recomputation

Whenever retrieval capabilities change materially, recompute the relevant Oracle labels or strongest attainable retrieval reference.

Do not assume V4 Oracle labels remain correct under a fundamentally new evidence representation.

For V6 maintain:

```text
V6 Oracle / strongest-policy reference
```

where justified.

Keep the earlier Oracle snapshots frozen.

---

# 97. Why Oracle semantics can change

Suppose a question was previously marked insufficient because:

```text
gold chunk not retrieved
```

but a V6 table unit contains the exact answer.

Then:

```text
retrieval capability improved
```

and the old insufficiency label no longer describes the new retrieval space.

This is why benchmark sufficiency must be versioned by evaluation environment.

---

# 98. V6 oracle interpretation

A useful separation is:

```text
retrieval architecture capability
```

versus:

```text
adaptive policy choice
```

The V6 strongest retrieval reference should answer:

```text
Can the evidence be recovered at all under this representation?
```

Only then should routing decide whether to invoke that representation.

---

# 99. Provider instrumentation

All experiments involving external models must persist:

```text
logical calls
provider API calls
cache hits
cache misses
retry attempts
rate-limit errors
connection errors
prompt tokens
completion tokens
total tokens
latency
```

Do not rely on console output alone.

This continues the instrumentation lesson from benchmark generation.

---

# 100. Run manifest

Each V6 experiment should persist a machine-readable manifest containing at least:

```json
{
  "experiment_id":"V6-B",
  "benchmark":"questions_v6",
  "corpus_version":"...",
  "index_version":"...",
  "retrieval_config":"...",
  "embedding_model":"...",
  "reranker_model":"...",
  "answer_model":"...",
  "prompt_version":"...",
  "git_commit":"..."
}
```

Add instrumentation fields as available.

---

# 101. Raw per-question outputs

Save every test question result.

Recommended information:

```text
question_id
experiment_id
retrieved_ids
retrieved_types
scores
rankings
gold_evidence
retrieval_metrics
answer
citations
answer_metrics
latency
tokens
errors
```

Without this, failure analysis becomes guesswork.

---

# 102. Reproducibility hash

Where practical, compute hashes for:

```text
benchmark
corpus manifest
structured extraction
index metadata
configuration
result files
```

This prevents accidental mixing of artifacts from different runs.

---

# 103. Test strategy

Add deterministic tests before running the expensive benchmark.

Minimum tests:

```text
table serialization

table row/column preservation

equation serialization

numeric parsing

unit preservation

caption association

section association

temporal relation ordering

structured-result provenance

fusion behavior
```

These should run without external API access where possible.

---

# 104. Regression tests

Run the existing test suite before and after V6 work.

The new V6 code must not silently change:

```text
V1 retrieval behavior

V2 verifier behavior

V3 failure detector behavior

benchmark generation
```

unless the experiment intentionally changes a shared component and records that dependency.

---

# 105. Minimal pilot before full extraction

Do not parse the entire corpus immediately.

Start with:

```text
5–10 representative papers
```

including papers with:

```text
tables

equations

complex numeric notation

captions

units
```

Inspect the structured output manually.

Only then scale extraction.

---

# 106. Representative-paper selection

Choose pilot papers from different characteristics:

```text
prose-heavy

table-heavy

equation-heavy

older PDF formatting

modern PDF formatting
```

The purpose is to expose parser fragility early.

---

# 107. Extraction quality report

Create a compact report such as:

```text
papers inspected: 10

TABLE
found: 42
correct: 37
partial: 4
incorrect: 1

EQUATION
found: 96
correct: 84
partial: 8
incorrect: 4
```

The exact values will come from execution.

Do not invent them in advance.

---

# 108. Decide whether OCR is necessary

OCR may help when PDFs contain scanned or image-based content.

But OCR introduces additional errors and should not be added automatically.

First measure:

```text
how much of the corpus is affected
```

and:

```text
whether those failures materially affect the benchmark
```

Only then decide whether OCR belongs in V6.

---

# 109. Separate parser errors from scientific reasoning

A V6 question can fail because:

```text
parser missed table
```

or because:

```text
retriever ranked wrong table
```

or because:

```text
answer model misread correct table
```

These are three different failures.

Keep them separate in all analysis.

---

# 110. Benchmark difficulty ladder

A useful progression is:

```text
LEVEL 1
single table lookup

LEVEL 2
single equation lookup

LEVEL 3
parameter + uncertainty + unit

LEVEL 4
table + prose

LEVEL 5
equation + definitions

LEVEL 6
temporal structured comparison

LEVEL 7
multi-structure chain
```

Do not build Level 7 until the earlier levels are reliable.

---

# 111. Structure necessity test

For each V6 question, ask:

```text
Could the question be answered correctly from the ordinary prose baseline?
```

If yes, the question may not be a strong structural challenge.

A stronger question is one where:

```text
structure-aware evidence
```

materially improves the chance of recovering the answer-critical information.

---

# 112. Counterfactual structure test

A useful validation is:

```text
remove the table/equation structure
↓
measure baseline

restore structure
↓
measure V6
```

This is stronger than simply showing that the structure exists.

It demonstrates whether the structure changes retrieval behavior.

---

# 113. Retrieval top-k inspection

For a sample of failures, print something like:

```text
rank
paper
section
type
score
snippet / structured payload
```

Then ask:

```text
Was the correct evidence absent?

Was it present but ranked too low?

Was the representation corrupted?

Was another structure more useful?
```

This should become a standard diagnostic view.

---

# 114. Structural score calibration

If separate evidence types produce incomparable scores, calibration may be needed before fusion.

For example:

```text
prose score = 0.82

 table score = 0.58
```

does not automatically imply:

```text
prose > table
```

unless the score scales are comparable.

RRF can avoid some of this issue.

If score normalization is used, document it.

---

# 115. Fusion ablation after the basic result

Once structure-aware retrieval shows value, compare:

```text
RRF

normalized linear fusion

rank-weighted fusion
```

Keep the structure set fixed.

This isolates:

```text
fusion method
```

as the independent variable.

---

# 116. Structure-aware reranker experiment

A later experiment can add explicit type labels to the reranker input.

Compare:

```text
standard reranker
```

vs:

```text
type-aware reranker
```

Do not interpret this as evidence for structural retrieval unless the only changed factor is the reranker.

---

# 117. Potential lightweight metadata reranker

A simple learned reranker could use:

```text
base retrieval score
structure type
question/field match
section type
unit match
```

Start with an interpretable model.

Do not jump to a transformer trained from scratch.

---

# 118. What would count as a strong V6 result?

A strong result could look like:

```text
structure-aware retrieval

↑ answer-critical evidence recall
↑ quantitative field completeness
↑ citation precision

while

latency increase remains bounded
```

Especially strong would be improvement on:

```text
questions where the required information is absent or fragmented in prose chunks
```

The actual thresholds must be defined before seeing test results where practical.

---

# 119. What would count as a weak result?

Examples:

```text
small recall increase
large latency increase
```

or:

```text
retrieval improves
answer quality unchanged
```

or:

```text
benefit exists only on benchmark artifacts
```

or:

```text
parser errors erase the theoretical benefit
```

These are not project failures.

They are evidence about where the approach breaks.

---

# 120. What would justify rejecting V6?

Reject or defer the approach if:

```text
no statistically or practically meaningful improvement

structure extraction is unreliable

benefits disappear under realistic controls

cost is disproportionate

improvement does not survive unseen papers/domains
```

Do not preserve a component simply because it sounds technically impressive.

---

# 121. What would justify keeping only a subset?

A likely outcome may be:

```text
KEEP tables

DEFER equations

REJECT temporal graph
```

That is perfectly acceptable.

AtlasRAG does not need every structural representation.

The research contribution can be narrower and stronger.

---

# 122. Possible V6 decision record

Create:

```text
V6 STATUS: KEEP / KEEP WITH QUALIFIERS / REJECT / DEFER

Primary question:
Can structure-aware evidence representation improve scientific retrieval?

Strongest result:
...

Weakest component:
...

Most useful structure:
...

Main confounder:
...

Main limitation:
...

Recommended next step:
...
```

This prevents roadmap drift.

---

# 123. Publication framing

Do not claim:

```text
"we solved scientific document retrieval"
```

A defensible framing is closer to:

```text
"We evaluate whether explicit representations of scientific evidence structures improve retrieval of answer-critical information in scientific RAG."
```

The exact final claim must follow the results.

If only tables help, say tables.

Do not generalize to all scientific structures.

---

# 124. V6 contribution possibilities

Depending on results, the contribution may be:

```text
an empirical finding
```

rather than:

```text
a new model architecture
```

For example:

```text
explicit table structure substantially improves quantitative evidence retrieval under fixed retrieval/generation conditions
```

This can still be a useful engineering/research contribution if the evaluation is rigorous.

---

# 125. Resume / portfolio framing

Do not add resume claims yet.

After evidence lock, possible phrasing could be:

```text
Built and evaluated structure-aware scientific retrieval for tables, equations, and quantitative evidence under controlled RAG benchmarks.
```

Only use the components actually implemented and measured.

---

# 126. Exact implementation order

The recommended order is:

```text
1. inspect V5 results

2. identify structural failure evidence

3. freeze V5 artifacts

4. inspect current repository architecture

5. design structured evidence schema

6. build small pilot parser

7. manually inspect extraction quality

8. add deterministic serialization

9. add structured index without changing baseline

10. create V6 benchmark candidates

11. human-review candidates

12. freeze V6 benchmark

13. run V6-A baseline

14. run V6-B tables

15. run V6-C equations

16. run V6-D numeric evidence

17. run V6-E temporal evidence if justified

18. run V6-F combined system

19. run control experiments

20. compute paired statistics

21. inspect failures

22. run end-to-end answer evaluation

23. evaluate cost/latency

24. lock results

25. write V6 decision
```

Do not reorder this casually.

---

# 127. Git discipline

Before starting:

```powershell
git status --short
git log --oneline --decorate -10
```

Create logical commits such as:

```text
V6 structured evidence schema
V6 table extraction/indexing
V6 equation extraction/indexing
V6 benchmark infrastructure
V6 retrieval experiments
V6 evaluation and analysis
```

Do not hide experimental history.

---

# 128. Preserve frozen historical artifacts

Never overwrite:

```text
Run1
V1 benchmark
V1 frozen benchmark
V4 benchmark
V5 benchmark
V5 transfer results
V5 manifests
```

Version V6 separately.

The ability to reconstruct the evolution of the project is part of scientific reproducibility.

---

# 129. Suggested V6 deliverables

Target documents:

```text
01_V6_STRUCTURE_SPEC.md
02_V6_EXTRACTION_AUDIT.md
03_V6_BENCHMARK_SPEC.md
04_V6_EXPERIMENT_MATRIX.md
05_V6_RESULTS.md
06_V6_FAILURE_ANALYSIS.md
07_V6_DECISION.md
```

Raw artifacts:

```text
data/v6/
experiments/v6/
```

Exact names should follow the repository's conventions.

---

# 130. Minimal V6 pilot

If the full experiment is too large, the minimum scientifically useful version is:

```text
V5 structural-failure evidence verified

one structure type

small manually audited extraction set

one structural benchmark

frozen prose baseline

one structure-aware retrieval condition

retrieval-only comparison

paired analysis

manual failure inspection
```

A table-only V6 pilot is completely acceptable if tables dominate observed failures.

---

# 131. What not to do

Do not:

```text
replace all parsers simultaneously

change embedding model without documenting it

change reranker and structure representation together

train on target test questions

use gold row/column IDs at inference

assume OCR is accurate

flatten structures and call them structure-aware

use an LLM to silently repair extraction

claim universal scientific transfer
```

Keep the experiment controlled.

---

# 132. Final mental model

Think of V6 as moving from:

```text
Document
↓
Text chunks
↓
Semantic similarity
```

toward:

```text
Scientific document
        ↓
Evidence structures
        ↓
Prose / table / equation / numeric / temporal units
        ↓
Structure-aware retrieval
        ↓
Evidence completeness
        ↓
Answer + citation
```

The key question is:

```text
Does preserving scientific structure actually help the system recover the evidence it needs?
```

Not:

```text
Can we build a complicated parser?
```

---

# 133. Final Week 15 checklist

Before V6:

```text
[ ] V5 results inspected
[ ] structural bottleneck confirmed
[ ] V5 artifacts frozen
[ ] fresh literature review completed where needed
[ ] current repository architecture inspected
[ ] structure taxonomy defined
[ ] extraction schema defined
[ ] pilot papers selected
[ ] extraction quality audited
[ ] parser limitations recorded
[ ] structured serialization tested
[ ] structured index versioned
[ ] V6 benchmark generated
[ ] benchmark human-reviewed
[ ] V6 benchmark frozen
[ ] V6-A baseline measured
[ ] V6-B table experiment measured
[ ] V6-C equation experiment measured
[ ] V6-D numeric experiment measured
[ ] V6-E temporal experiment measured if justified
[ ] V6-F combined experiment measured if justified
[ ] long-context control measured if useful
[ ] flattened-structure control measured if useful
[ ] Oracle/strongest-policy reference updated where necessary
[ ] paired statistical analysis completed
[ ] raw per-question outputs saved
[ ] provider instrumentation saved
[ ] extraction failures separated from retrieval failures
[ ] answer evaluation completed when justified
[ ] citation evaluation completed
[ ] cost/latency evaluated
[ ] V6 decision recorded
[ ] Git commit recorded
```

---

# 134. Final rule for the next AI agent

Start by inspecting the actual repository and the final V5 decision.

Do not assume V6 is justified until the V5 failure taxonomy supports it.

Do not assume tables, equations, or temporal structures are equally important.

Do not build a multimodal system before proving a simpler structural representation is useful.

Do not modify the historical baseline.

Do not silently change the answer model, embedding model, reranker, or benchmark while testing structure-aware retrieval.

Do not treat parser output as ground truth.

Do not expose gold structure metadata at inference time.

Do not reward exact gold retrieval when a valid alternative evidence source exists without recording that limitation.

Do not claim a retrieval improvement without checking whether the final answer and citations improve.

The correct workflow is:

```text
inspect V5
↓
confirm structural bottleneck
↓
freeze historical evidence
↓
define structure
↓
pilot extraction
↓
audit parser quality
↓
build structured index
↓
freeze V6 benchmark
↓
measure baseline
↓
measure one structure at a time
↓
measure controls
↓
measure combined system
↓
analyze retrieval + answer + citation impact
↓
inspect failures
↓
lock evidence
↓
decide what survives
```

That is Week 15.
