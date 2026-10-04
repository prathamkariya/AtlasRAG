# AtlasRAG — Week 7: End-to-End Answer Evaluation & Final System Analysis

## 1. Purpose

Week 7 is the phase where AtlasRAG finally evaluates the complete user-facing RAG system.

Earlier phases deliberately separated:

```text
retrieval quality
routing quality
routing cost
```

from:

```text
answer generation
```

That separation was necessary because a final LLM can hide retrieval mistakes, amplify them, or produce fluent answers from incomplete evidence.

Week 7 therefore begins only after:

```text
benchmark is stable enough
+
retrieval stack is understood
+
routing behavior is understood
+
Compass / escalation behavior is understood
```

The complete pipeline becomes:

```text
User Question
      |
      v
Routing policy
      |
      v
Retrieval strategy
      |
      v
Retrieved evidence
      |
      v
Answer-generation LLM
      |
      v
Final answer + citations
```

The main research question becomes:

> **How do retrieval and routing choices propagate into final answer correctness, grounding, citation quality, latency, and total cost?**

---

## 2. Why answer evaluation comes last

The earlier retrieval experiments use:

```text
--retrieval-only
```

so the project can measure evidence coverage without involving final answer wording.

The existing project documentation explicitly separates:

```text
retrieval-only evidence evaluation
```

from the later:

```text
answer-generation benchmark
```

The final benchmark should measure:

```text answer correctness
answer relevance
groundedness / faithfulness
citation correctness
citation completeness
unsupported claims / hallucination
latency
LLM calls
tokens
cost
```

These metrics were part of the original evaluation design, but they should now be implemented only after the retrieval/routing foundations are sufficiently controlled.

---

## 3. What the final system should contain

Depending on the results of earlier weeks, the final candidate systems may include:

```text B
Static retrieval

C1
Original LLM router

C2
Oracle-aligned LLM router

D
Compass

Hybrid
Compass + selective C2 fallback

E2
Oracle-v2 reference
```

The exact final comparison matrix must use only systems that actually exist and have reproducible configurations.

Do not present a planned component as part of the final system before it has been implemented and evaluated.

---

## 4. Retrieval-only vs answer-generation metrics

This distinction must remain explicit.

### Retrieval-only evaluation

Measures:

```text evidence recall
paper recall
retrieval latency
routing cost
```

The system stops after evidence selection.

### End-to-end evaluation

Measures:

```text answer correctness
answer relevance
groundedness
citation precision
citation recall/completeness
unsupported claims
latency
token usage
cost
```

The LLM produces the actual answer.

A strong retrieval score does not guarantee a strong final answer.

A fluent final answer does not prove that retrieval was correct.

---

## 5. The complete evaluation chain

For each query:

```text question
    ↓
router
    ↓
strategy
    ↓
retrieval
    ↓
evidence
    ↓
answer LLM
    ↓
answer
    ↓
citation verification
    ↓
quality metrics
```

Store intermediate artifacts wherever possible.

This allows later analysis of:

```text wrong answer because of retrieval
```

versus:

```text wrong answer despite sufficient retrieval
```

which are different failures.

---

## 6. Answer-generation LLM

The current answering model used in the project is:

```text
openai/gpt-oss-20b
```

served through a Groq-compatible API path.

The exact final model must be recorded again in the final experiment manifest.

Do not silently change the answering model during the final comparison.

If another model is tested, that becomes a separate answer-generation ablation.

---

## 7. Answer-generation prompt

The final prompt should make the model's job explicit:

```text use retrieved evidence
answer the question directly
do not invent unsupported facts
cite evidence
distinguish disagreement when present
avoid claims not supported by retrieved context
```

The exact prompt should be versioned.

For example:

```text answer_prompt_v1
answer_prompt_v2
```

Do not change wording midway through an evaluation without creating a new experiment version.

---

## 8. Context construction

The answer generator receives:

```text question
+
retrieved evidence
```

The context should ideally preserve:

```text paper/source identity
section
chunk text
```

The model should be able to distinguish:

```text evidence A
evidence B
```

especially for:

```text multi-hop
temporal
conflicting
chain
```

questions.

---

## 9. Citation behavior

The final answer should include citations tied to actual retrieved evidence.

The citation representation can follow the existing application format.

The important requirement is:

```text every citation must map to a real retrieved chunk
```

and:

```text cited evidence must actually support the claim attached to it
```

Do not evaluate citation formatting alone.

Citation quality is about:

```text correctness
support
coverage
```

---

## 10. Citation correctness

A useful definition:

> Does the cited chunk actually support the claim associated with the citation?

Example:

```text Claim:
H0 was measured as X.

Citation:
chunk containing H0 = X

→ supported
```

versus:

```text Claim:
H0 was measured as X.

Citation:
chunk only discussing a related cosmological model

→ unsupported citation
```

The second case is a citation error even if the source paper is relevant.

---

## 11. Citation completeness

Citation completeness asks:

```text Are all externally sourced factual claims
that need evidence actually cited?
```

An answer may have:

```text correct citations
```

but still omit citations for additional scientific claims.

Therefore report separately:

```text citation correctness
citation completeness
```

when the evaluator supports both.

---

## 12. Citation precision

A useful citation metric is:

```text supported citations
----------------------
all citations
```

Conceptually:

```text citation precision
```

High precision means the answer is not attaching irrelevant chunks to claims.

Do not equate:

```text citation exists
```

with:

```text citation is correct
```

---

## 13. Citation recall

A complementary concept is:

```text supported factual claims with required citations
-----------------------------------------------
claims requiring citation
```

This is one possible form of citation completeness/recall.

The exact implementation should match the project's chosen evaluation methodology.

Avoid creating overlapping metrics with confusing names.

---

## 14. Groundedness / faithfulness

The central question is:

> Does the generated answer stay supported by the retrieved evidence?

This is more important than linguistic fluency.

An answer can be:

```text grammatically excellent
scientifically plausible
```

and still be:

```text unsupported
```

That should count as a grounding failure.

---

## 15. Unsupported-claim / hallucination metric

Track the number or fraction of answer claims that:

```text are not supported by the retrieved evidence
```

A useful representation is:

```text unsupported claims / total factual claims
```

or a normalized answer-level score.

The exact metric must be clearly defined before final evaluation.

Do not use the word “hallucination” as a vague catch-all without explaining what counts as unsupported.

---

## 16. Answer correctness

Correctness should be evaluated against the benchmark's:

```text reference answer
gold evidence
question intent
```

A correct answer must:

```text answer the actual question
use the right quantity
preserve units/definitions
respect qualifiers
```

This is especially important for scientific questions.

---

## 17. Numeric answer safety

Scientific benchmark answers can involve:

```text H0
Ωm
YHe
ΔNeff
percentage constraints
uncertainties
```

The evaluator must distinguish:

```text correct quantity
correct unit
correct value
correct uncertainty
```

from:

```text numerically similar but scientifically different quantity
```

This issue already caused problems in benchmark generation.

The answer evaluator must not repeat the same mistake.

---

## 18. Multi-hop answer correctness

For a multi-hop question, the final answer should reflect information from:

```text evidence A
+
evidence B
```

when both are genuinely necessary.

A response that uses only one passage may be:

```text incomplete
```

even if that passage contains part of the answer.

The evaluation should therefore combine:

```text answer correctness
+
citation/evidence coverage
```

for multi-hop cases.

---

## 19. Conflicting findings

For conflicting questions, the system must not simply select one paper's value and ignore the other.

A good evaluation asks whether the answer:

```text identifies both findings
describes the relevant difference
avoids inventing a false consensus
uses appropriate citations
```

The exact benchmark determines the expected behavior.

Do not classify every different numerical value as a conflict.

---

## 20. Temporal answers

For temporal questions, evaluate whether the final answer correctly captures:

```text earlier result
later result
same quantity/claim
change/update/refinement
```

Do not reward answers that merely say:

```text Paper B is newer.
```

The answer needs to explain the scientific change when the question asks for it.

The historical temporal benchmark had quality problems, so only validated temporal items should be included in strong final conclusions.

---

## 21. Chain answers

For chain questions, evaluate whether the answer connects:

```text earlier/abstract claim
```

to:

```text later evidence-bearing section
```

The final response should not simply repeat the abstract.

It should use the later evidence to explain:

```text how the claim is supported
```

This directly tests the purpose of chain benchmark construction.

---

## 22. Answer relevance

A response can be grounded but still fail because it does not answer the actual question.

For example:

```text question asks for two constraints
answer discusses one constraint extensively
```

This may be grounded but incomplete.

Therefore keep:

```text answer relevance
```

separate from:

```text groundedness
```

---

## 23. Concision is not the primary metric

The final answer should be usable, but the research evaluation should not optimize for:

```text shorter = better
```

unless the experiment explicitly defines a length/utility objective.

The main quality questions remain:

```text correct?
grounded?
complete?
properly cited?
```

---

## 24. Human evaluation vs automatic evaluation

The original project considered established RAG evaluation frameworks such as:

```text Ragas
ARES
```

These can provide automated metrics.

However, automatic evaluation is not equivalent to human judgment.

For a small scientific benchmark, human review can be especially valuable for:

```text numeric correctness
scientific nuance
citation validity
unsupported causal claims
conflicting evidence
```

---

## 25. Recommended evaluation hierarchy

Use:

```text automatic metrics
        ↓
targeted human audit
        ↓
final interpretation
```

rather than:

```text automatic score
        ↓
declare answer quality
```

The final report should identify which metrics are:

```text automated
```

and which are:

```text human-reviewed
```

---

## 26. Answer-evaluation set

Use the declared final benchmark version.

Do not silently add new questions after inspecting answer failures.

If the benchmark is changed:

```text new version
+
new experiment
```

must be recorded.

The final test should remain frozen for the final comparison.

---

## 27. Per-question answer record

A useful JSONL record should preserve:

```json
{
  "id":"...",
  "question":"...",
  "route":"MULTI_HOP",
  "retrieved_chunk_ids":["...","..."],
  "answer":"...",
  "citations":["..."],
  "reference_answer":"...",
  "evidence_recall":1.0,
  "answer_correct":true,
  "grounded":true,
  "citation_correct":true
}
```

Additional fields can include:

```text latency
tokens
provider calls
fallback status
router confidence
```

The exact schema should follow the repository.

---

## 28. Retrieval-to-answer diagnosis

The most valuable analysis is:

```text retrieval succeeded
    ↓
answer succeeded?

retrieval succeeded
    ↓
answer failed?
```

and:

```text retrieval failed
    ↓
answer failed?
```

This lets the project distinguish:

```text retrieval bottleneck
```

from:

```text generation bottleneck
```

---

## 29. Four-way outcome table

For each query, consider:

```text 1. Retrieval sufficient + answer correct
2. Retrieval sufficient + answer incorrect
3. Retrieval insufficient + answer still acceptable
4. Retrieval insufficient + answer incorrect
```

The unusual third case is important.

A final LLM may sometimes answer correctly even when the exact gold chunk was not retrieved.

That does not invalidate evidence-recall evaluation, but it shows:

```text retrieval-only metrics
```

and:

```text final-answer metrics
```

measure different things.

---

## 30. Do not let answer generation hide retrieval failure

Suppose:

```text gold evidence missed
```

but the LLM happens to know the answer from its pretrained knowledge.

The final answer may be:

```text factually correct
```

yet:

```text not grounded in retrieved evidence
```

That is exactly why answer correctness and grounding must remain separate.

---

## 31. Do not penalize correct retrieval for answer-generation errors without diagnosis

The opposite case:

```text gold evidence fully retrieved
```

but the answer model:

```text misreads the value
```

is a generation failure.

Do not call it a retrieval failure.

This separation is a major reason the project built retrieval-only evaluation first.

---

## 32. End-to-end system matrix

A useful final comparison can be:

| System | Evidence Recall | Answer Correctness | Groundedness | Citation Precision | Citation Completeness | p50 Latency | Tokens/Q |
|---|---:|---:|---:|---:|---:|---:|---:|
| B Static | | | | | | | |
| C1 LLM Router | | | | | | | |
| C2 LLM Router | | | | | | | |
| D Compass | | | | | | | |
| Hybrid | | | | | | | |
| E2 Oracle | | | | | | | |

Only include systems with actual completed runs.

---

## 33. Why E2 belongs in the table carefully

The empirical Oracle is not a deployable user-facing system.

It uses benchmark evidence and retrieval outcomes to select strategies.

Therefore:

```text E2 = reference / diagnostic upper-bound
```

not:

```text deployable baseline
```

Keep that distinction explicit.

---

## 34. Answer cost

Measure:

```text answer-model calls
prompt tokens
completion tokens
total tokens
provider calls
```

Then separate:

```text routing tokens
```

from:

```text answer-generation tokens
```

where possible.

The final system cost is:

```text routing cost
+
retrieval compute
+
answer-generation cost
```

The project should not report only answer-token cost while ignoring router cost.

---

## 35. Total latency

Measure:

```text routing
+
retrieval
+
reranking
+
answer generation
```

as:

```text end-to-end latency
```

Keep component timings separately when possible.

This helps determine whether:

```text Compass saves routing time
```

but:

```text reranking dominates the total pipeline
```

or whether:

```text answer generation dominates everything else.
```

---

## 36. Cold and warm latency

As in earlier phases, distinguish:

```text cold start
```

from:

```text warm inference
```

A fair final comparison should primarily use:

```text warm steady-state query latency
```

with initialization cost reported separately.

---

## 37. Provider failures

A provider failure should never be treated as:

```text valid answer
```

Store:

```text timeout
429
connection error
invalid response
```

explicitly.

The final benchmark report should show:

```text evaluated successfully
```

separately from:

```text infrastructure failures
```

---

## 38. Repeated answer evaluation

LLM generation can be stochastic.

The project documentation explicitly warns that benchmark results can vary between runs.

For the final answer benchmark, where practical:

```text run more than once
```

or:

```text use deterministic generation settings
```

and document the choice.

Do not silently compare one system using one stochastic sample against another using many samples.

---

## 39. Reproducibility settings for answering

Record:

```text model
temperature
top_p if used
max_tokens
system prompt
answer prompt version
seed if supported
retrieval context ordering
citation format
```

The model configuration should remain fixed across compared systems.

---

## 40. Answer-generation prompt sensitivity

A prompt change can materially affect:

```text answer quality
citation behavior
verbosity
hallucination rate
```

Therefore prompt changes must be explicit.

Do not:

```text improve the prompt
```

after seeing a poor result and still treat the run as part of the original experiment.

Instead:

```text answer_prompt_v1
```

and:

```text answer_prompt_v2
```

become separate controlled configurations.

---

## 41. Human review rubric

For a high-value subset, review:

```text correctness
completeness
grounding
citation validity
numeric accuracy
scientific nuance
```

Each should have explicit definitions.

Example:

```text Correct:
    answer matches supported evidence.

Grounded:
    factual claims are supported by retrieved evidence.

Citation correct:
    cited source supports the claim attached to it.

Complete:
    required parts of the question are addressed.
```

---

## 42. Numeric/manual review

Pay particular attention to:

```text values
units
uncertainties
signs
parameter definitions
```

For scientific papers, a one-character notation difference may be meaningful.

Automatic semantic graders can miss this.

---

## 43. Unsupported causal claims

A common benchmark-generation failure was overclaiming causality.

The final answer evaluator should catch claims such as:

```text X proves Y
X rules out Y
X causes Y
```

when the evidence only says:

```text X is associated with Y
X constrains Y
X is consistent with Y
```

Scientific wording matters.

---

## 44. Comparative claims

Similarly distinguish:

```text A reports 70
B reports 72
```

from:

```text A is more accurate
B is superior
```

unless the source actually supports that conclusion.

The answer should preserve the paper's evidence rather than introduce new evaluation.

---

## 45. Conflicting evidence and uncertainty

For conflicting papers, the answer should not erase uncertainty.

It should use language appropriate to the source evidence:

```text Paper A reports...
Paper B reports...
The values differ because...
```

when the evidence supports that explanation.

Do not force the system to produce a single “winner” when the benchmark asks for comparison.

---

## 46. End-to-end question-type analysis

Report separately for:

```text SIMPLE
MULTI_HOP
TEMPORAL
CHAIN
```

when sample size permits.

For each:

```text answer correctness
groundedness
citation quality
retrieval recall
latency
```

This can expose:

```text retrieval strong
but answer generation weak on chain questions
```

or:

```text multi-hop answers improve mainly because retrieval improved.
```

---

## 47. Routing-to-answer propagation analysis

A useful analysis chain is:

```text route
→ evidence recall
→ answer correctness
```

For example:

```text Compass route correct
→ evidence recall high
→ answer correct
```

versus:

```text Compass route correct
→ evidence recall low
→ answer incorrect
```

This can show whether routing is actually affecting the final user experience.

---

## 48. The final system may have multiple “winners” under different metrics

Do not reduce the final experiment to:

```text one overall winner
```

Different systems can have:

```text different recall
different latency
different cost
different grounding
```

The report should show the tradeoffs rather than force one scalar ranking.

---

## 49. Final tradeoff view

A useful final plot can show:

```text x-axis = total tokens/query
y-axis = answer correctness
```

Another:

```text x-axis = end-to-end latency
y-axis = groundedness
```

Another:

```text x-axis = evidence recall
y-axis = answer correctness
```

These are more informative than a single leaderboard.

---

## 50. Answer quality should be tied to evidence quality

A particularly useful analysis is:

```text evidence recall buckets
    ↓
mean answer correctness
mean groundedness
mean citation quality
```

For example:

```text evidence recall 0.0–0.25
0.25–0.50
0.50–0.75
0.75–1.0
```

The exact bins can be changed.

The objective is to examine whether better evidence retrieval translates into better final answers.

---

## 51. Answer degradation despite sufficient evidence

If many cases show:

```text evidence recall = 1.0
```

but:

```text answer correctness low
```

then retrieval is probably not the dominant end-to-end bottleneck.

Investigate:

```text prompt
answer model
context ordering
citation handling
numeric extraction
```

This is a valuable result.

---

## 52. Answer improvement despite incomplete evidence

If:

```text evidence recall < 1.0
```

but:

```text answer correctness remains high
```

investigate whether:

```text alternate retrieved chunks
LLM prior knowledge
redundant evidence
```

are producing the answer.

Groundedness evaluation becomes especially important here.

---

## 53. Final benchmark honesty

The final report should state:

```text benchmark size
benchmark version
question types
known exclusions
validation procedure
automatic vs human evaluation
```

Do not hide benchmark weaknesses.

Especially disclose:

```text insufficient Oracle cases
temporal limitations
small difficult-class sample sizes
```

when they remain.

---

## 54. Final experiment reproducibility

Record:

```text commit hash
benchmark hash/version
retrieval configuration
router configuration
Compass checkpoint
answer model
prompt version
temperature
token limit
hardware
provider
software versions
```

A reviewer should be able to understand exactly what produced the reported numbers.

---

## 55. Result-file organization

A possible structure:

```text
results/
    run1/
        frozen historical baseline

    run2/
        routing benchmark

    run5/
        dynamic routing

    run6/
        retrieval ablations

    run7/
        end_to_end/
            B_static.jsonl
            C1_llm.jsonl
            C2_llm.jsonl
            D_compass.jsonl
            hybrid.jsonl
            E2_oracle.jsonl
            summary.json
            config.json
```

The exact naming can follow the repository.

The key requirement is:

```text reproducible separation of experiments
```

---

## 56. Final report metrics

The final report should include at least:

```text Evidence Recall
Answer Correctness
Answer Relevance
Groundedness / Faithfulness
Citation Precision
Citation Completeness
Unsupported Claims
p50 Latency
p95 Latency
LLM Calls / Query
Provider Calls / Query
Tokens / Query
Fallback Rate
```

Where a metric is unavailable or unreliable, state that rather than inventing a value.

---

## 57. Statistical analysis

For the same benchmark questions, use paired comparisons.

Compare:

```text B vs C1
B vs C2
B vs D
C1 vs C2
C2 vs D
D vs Hybrid
```

and relevant reference systems.

For answer correctness, preserve:

```text per-question outcomes
```

so uncertainty can be estimated appropriately.

Do not rely only on aggregate means.

---

## 58. Human-audit sample design

If the full benchmark is small enough, manually inspect all answers.

If not, create a predefined audit sample covering:

```text each question type
high-confidence routes
low-confidence routes
retrieval failures
citation failures
numeric answers
conflicting evidence
temporal examples
```

Do not select only visually impressive answers.

---

## 59. Error taxonomy for final answers

Classify failures into:

```text A. Retrieval failure
B. Routing failure
C. Query decomposition failure
D. Evidence interpretation failure
E. Unsupported generation
F. Citation failure
G. Numeric/unit error
H. Incomplete answer
I. Infrastructure failure
```

This becomes useful in the final project analysis.

---

## 60. Example answer-failure chain

```text Question
   ↓
Compass selects SIMPLE
   ↓
gold evidence missed
   ↓
LLM generates plausible answer
   ↓
answer factually unsupported
```

Classification:

```text primary:
    retrieval/routing

secondary:
    grounding failure
```

This is more informative than simply:

```text answer wrong
```

---

## 61. Example generation failure

```text Question
   ↓
correct route
   ↓
gold evidence retrieved
   ↓
LLM misreads numerical uncertainty
   ↓
wrong answer
```

Classification:

```text retrieval:
    successful

generation:
    failed
```

This distinction is important for final research claims.

---

## 62. Example citation failure

```text answer is correct
evidence is present
citation points to adjacent but non-supporting chunk
```

Result:

```text answer correctness:
    pass

grounding:
    possibly pass

citation correctness:
    fail
```

This shows why one metric is not enough.

---

## 63. End-to-end latency decomposition

A final latency breakdown can be:

```text routing:
    Compass / C2

retrieval:
    dense + BM25

reranking:
    cross-encoder

answer:
    GPT model

citation verification:
    evaluator, if online
```

This allows the final architecture to identify the actual time bottleneck.

---

## 64. Online vs offline evaluation

Some citation or groundedness checks may be:

```text offline
```

and should not be counted in user-facing latency.

Distinguish:

```text production end-to-end latency
```

from:

```text evaluation-only analysis time
```

Otherwise the final performance numbers become misleading.

---

## 65. Answer generation cost accounting

Separate:

```text routing LLM cost
```

from:

```text answer-generation LLM cost
```

and, if relevant:

```text evaluation LLM cost
```

Do not accidentally include the evaluator's LLM calls in the production system's cost/query.

---

## 66. Evaluator leakage

If an LLM judges the answer:

```text evaluator
```

must not influence the answer generation itself.

Keep the stages:

```text generate answer
↓
freeze answer
↓
evaluate answer
```

Never let the evaluator rewrite or repair the answer before scoring it.

---

## 67. Automatic evaluator bias

An LLM judge can prefer:

```text verbose answers
```

or:

```text wording similar to the reference
```

without necessarily improving factual correctness.

Therefore interpret automated answer-quality scores cautiously.

Human review remains valuable for important conclusions.

---

## 68. Reference-answer limitations

The reference answer may itself be imperfect.

This was already observed during benchmark repair.

A generated answer can be:

```text scientifically supported
```

but differ in wording from the reference.

Do not equate:

```text string similarity
```

with:

```text scientific correctness
```

---

## 69. Ground truth should be evidence-first

For difficult scientific questions, the strongest evaluation hierarchy is:

```text source evidence
    ↓
question requirements
    ↓
reference answer
```

The reference answer helps define expected content, but it should not overrule the actual source evidence.

This is especially important for repaired benchmark items.

---

## 70. Final answer prompt should not use hidden gold information

The production answer path must receive only:

```text user question
retrieved context
system instructions
```

It must not receive:

```text gold answer
gold chunks
Oracle route
evaluation labels
```

This should remain true during final evaluation.

---

## 71. Comparison between full systems

A useful final pipeline comparison is:

```text B:
question
→ static retrieval
→ answer

C1:
question
→ LLM route
→ retrieval
→ answer

C2:
question
→ Oracle-aligned LLM route
→ retrieval
→ answer

D:
question
→ Compass
→ retrieval
→ answer

Hybrid:
question
→ Compass
→ possible C2 fallback
→ retrieval
→ answer
```

This gives a coherent system-level story.

---

## 72. Oracle final-system caveat

E2 may use information unavailable to deployable systems.

It therefore provides:

```text empirical strategy reference
```

rather than:

```text production answer baseline
```

The final report must say this explicitly.

---

## 73. What a strong final conclusion can establish

The project may eventually be able to answer:

```text Does adaptive routing improve final answer quality?

Does it improve evidence grounding?

Does Compass reproduce the useful retrieval behavior cheaply?

Does selective escalation preserve answer quality?

Which retrieval stack provides the best quality/cost tradeoff?

How much of the final improvement comes from routing versus retrieval?
```

These are the meaningful end-to-end questions.

---

## 74. What a negative result would mean

Examples:

```text Compass improves routing cost
but final answer quality does not improve.
```

Possible interpretation:

```text retrieval quality was already sufficient
or
answer generation is now the bottleneck.
```

Another:

```text stronger retrieval improves evidence recall
but final groundedness barely changes.
```

Possible interpretation:

```text answering model already handles some retrieval gaps
or
evaluation is insensitive to the retrieval improvement.
```

These are useful findings too.

---

## 75. Final system selection must be evidence-driven

The final deployed/configured system should be selected from:

```text measured evidence quality
+
answer quality
+
cost
+
latency
+
robustness
```

Do not choose the configuration simply because it has the highest one-dimensional score.

The final report should preserve the tradeoff information.

---

## 76. Suggested final answer-evaluation workflow

```text 1. freeze benchmark
2. freeze retrieval configuration
3. freeze router/configuration
4. freeze answer prompt
5. run all systems
6. save raw answers/citations
7. run automatic evaluators
8. perform predefined human audit
9. compute paired comparisons
10. inspect failures
11. separate retrieval vs generation errors
12. write final system analysis
```

---

## 77. Commands to begin Week 7

Set project path/imports:

```powershell
$env:PYTHONPATH="src"
```

Verify:

```powershell
git status
git log --oneline --decorate -10
python -m pytest -q
```

Inspect answer-generation pipeline:

```powershell
Get-Content .\src\atlasrag\pipeline.py
```

Inspect configuration:

```powershell
Get-Content .\configs\default.yaml
```

Locate generation/evaluation code:

```powershell
Get-ChildItem .\src\atlasrag\ -Recurse -File | Select-String "answer|citation|faithful|ground|generate"
```

Exact file names and commands must be checked against the current checkout before editing.

---

## 78. Tests required before end-to-end evaluation

At minimum:

```text router tests
retrieval tests
answer-generation tests
citation mapping tests
JSON/result-schema tests
failure-handling tests
benchmark tests
```

Then:

```powershell
python -m pytest -q
```

Do not begin a long answer benchmark from a failing code state.

---

## 79. End-to-end smoke test

Run one query manually and verify:

```text question accepted
route selected
retrieval completed
evidence attached
answer generated
citations emitted
citations map to real chunks
result persisted
latency recorded
LLM usage recorded
```

This is only a pipeline smoke test.

It is not an answer-quality benchmark result.

---

## 80. Final benchmark run

Use a new result group.

For example:

```text results/run7/
```

Do not overwrite earlier retrieval/routing experiments.

Persist:

```text raw answer
retrieved evidence
citations
metrics
config
model information
```

---

## 81. Final report layout

A good report can use this structure:

```text 1. Experimental setup
2. Benchmark
3. Retrieval configurations
4. Routing configurations
5. Answer-generation configuration
6. Automatic metrics
7. Human audit
8. End-to-end results
9. Retrieval → answer analysis
10. Cost/latency analysis
11. Failure taxonomy
12. Limitations
13. Final architecture
14. Reproducibility information
```

---

## 82. Final project narrative

The overall AtlasRAG story should now be explainable as:

```text scientific corpus
      ↓
retrieval baseline
      ↓
stronger retrieval
      ↓
adaptive strategy selection
      ↓
Oracle-grounded routing target
      ↓
lightweight learned router
      ↓
selective fallback
      ↓
retrieval ablations
      ↓
end-to-end answer evaluation
```

Each phase should answer a distinct question.

---

## 83. What should remain separate in the final paper/report

Keep separate:

```text benchmark construction
retrieval ablations
routing experiments
Compass training
selective escalation
answer-generation evaluation
```

Do not collapse every result into one “AtlasRAG score”.

A reader should be able to see:

```text what changed
why it changed
what improved
what cost increased
what remained a bottleneck
```

---

## 84. Limitations to disclose

Potential final limitations include:

```text small scientific corpus
small benchmark
limited difficult-question counts
benchmark-generation dependence on LLM-assisted proposals
gold-chunk metric limitations
possible alternate evidence paths
provider rate limits
evaluation-model bias
paper-distribution limits
```

The exact list should match the final project state.

---

## 85. Gold-chunk metric limitation

The existing project already recognized:

```text gold evidence = chunks used to write the question
```

Other chunks may also answer the question.

Therefore:

```text exact gold-chunk recall
```

can be conservative.

A system might retrieve:

```text valid alternative evidence
```

without retrieving the exact gold chunk.

This should be considered when interpreting retrieval and end-to-end results.

---

## 86. Oracle limitation

The Oracle is:

```text empirical
```

and:

```text benchmark-specific
```

It is an upper reference over the tested strategies and metric.

It is not a universal optimal retrieval policy.

The final paper should avoid describing it as omniscient or universally optimal.

---

## 87. Compass limitation

Compass learns from:

```text question text
+
Oracle-derived labels
```

It does not directly observe:

```text actual retrieval state
```

unless a later extension changes the architecture.

Therefore some routing failures may remain fundamentally difficult to predict before retrieval.

That can be treated as a research limitation rather than hidden.

---

## 88. Selective-escalation limitation

Hybrid routing introduces:

```text threshold sensitivity
```

and:

```text fallback dependence
```

The final report should state:

```text threshold-selection protocol
```

and:

```text fallback model
```

clearly.

---

## 89. Answer-model limitation

Even with excellent retrieval:

```text the final answer model can hallucinate
misread evidence
omit required pieces
produce incorrect citations
```

Therefore AtlasRAG should not claim that retrieval improvements automatically solve all answer-quality problems.

---

## 90. Final end-to-end checklist

```text [ ] benchmark frozen
[ ] benchmark version recorded
[ ] retrieval configuration frozen
[ ] router configuration frozen
[ ] Compass checkpoint recorded
[ ] answer model recorded
[ ] answer prompt version recorded
[ ] generation parameters recorded
[ ] automatic metrics implemented
[ ] citation verification implemented
[ ] groundedness metric implemented
[ ] unsupported-claim metric implemented
[ ] human audit protocol defined
[ ] raw answers saved
[ ] per-question metrics saved
[ ] latency measured
[ ] tokens measured
[ ] provider calls measured
[ ] retrieval-vs-generation failures separated
[ ] B/C1/C2/D/Hybrid/E2 comparison completed where available
[ ] Run 1 untouched
[ ] test set not tuned against final results
```

---

## 91. Final Week 7 principle

> **A better RAG system is not merely one that retrieves more or answers more fluently; it is one whose final answers are demonstrably supported, correct, appropriately cited, and produced at a measured cost.**

The final analysis should preserve the full causal chain:

```text route
  ↓
retrieval
  ↓
evidence
  ↓
answer
  ↓
citation
  ↓
grounding
  ↓
user-facing quality
```

That makes the final AtlasRAG evaluation much stronger than a generic RAG benchmark.

The project should finish this phase knowing not just:

```text which system scored higher
```

but:

```text why
where
at what cost
under which benchmark conditions
and with which remaining failure modes.
```
