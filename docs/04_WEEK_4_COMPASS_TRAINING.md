# AtlasRAG — Week 4: Compass Training & Learned Routing
## Context handoff / execution manual

> **Purpose:** This document defines the phase in which AtlasRAG turns the validated routing task into a lightweight learned router named **Compass**.
>
> **Critical status rule:** Compass is **not currently trained**. This file is the execution plan and research guardrail for that phase. Any code, checkpoint, metrics, or training result described as future work must not be reported as completed until verified in the repository.

---

# 1. Week 4 in one page

The purpose of Week 4 is to test whether AtlasRAG can replace expensive LLM routing with a small locally executable learned router.

The intended architecture is:

```text
                  Incoming Question
                         |
                         v
                +------------------+
                |     Compass      |
                | question-only    |
                | learned router   |
                +---------+--------+
                          |
             +------------+-------------+
             |            |             |
             v            v             v
          SIMPLE      MULTI_HOP     UNCERTAIN
             |            |             |
             v            v             v
        cheap/static  decomposition   fallback /
        retrieval     + retrieval     escalation
```

The conceptual Compass model is:

```text
question
   ↓
small frozen base model
   ↓
LoRA adapter
   ↓
lightweight classification head
   ↓
SIMPLE / MULTI_HOP / UNCERTAIN
```

The model must remain isolated from retrieval and answer-generation context.

The research question is:

> **Can a lightweight learned router approximate the useful strategy-selection behavior of the empirical Oracle while using substantially less routing latency and LLM/token cost than an LLM router?**

This is the point where AtlasRAG moves from:

```text expensive adaptive routing
```

toward:

```text cheap learned adaptive routing
```

---

# 2. Where Week 4 fits in the project

The project direction has evolved based on measured failures rather than the original roadmap.

The current sequence is:

```text
Foundation
    ↓
Benchmark construction / audit
    ↓
Oracle-v2
    ↓
C1 LLM router
    ↓
C2 Oracle-aligned routing
    ↓
Compass
    ↓
dynamic escalation / efficiency
    ↓
retrieval ablations
    ↓
answer evaluation
```

Compass should therefore not be implemented as an isolated classifier project.

It is the learned component of a larger strategy-selection experiment.

---

# 3. The key distinction: Compass is not an answer model

Compass is a routing model.

It must not become:

```text question
+
retrieved evidence
+
answer context
→
LLM answer
```

Its contract is much smaller:

```python
route(question)->RouteDecision
```

The primary input is:

```text question only
```

The primary output is:

```text route
```

Optionally:

```text confidence
```

may also be returned.

The answer-generation model remains a separate component.

---

# 4. Existing project definition of Compass

The project documentation describes Compass as:

```text
A small frozen base model
+
a LoRA adapter
+
a lightweight scoring/classification head
```

It is intended to make the routing component:

```text small
fast
cheap
locally executable
trainable by us
```

rather than depending on a paid external decision API.

The architecture was inspired conceptually by typed-decision models, but AtlasRAG's contribution is the domain-specific routing task and training data rather than copying an external service.

---

# 5. Compass input isolation

This is one of the most important research constraints.

Compass may see:

```text question
```

It must not see:

```text retrieved chunks
gold chunks
reference answer
answering-LLM context
post-retrieval evidence
Oracle label directly encoded in the input
```

Why?

Because the routing decision is supposed to occur:

```text before retrieval
```

If the router sees retrieved evidence, it can make a decision using information that would not exist at the actual routing point.

That would introduce target leakage.

The paper-facing claim would then no longer be:

```text question-driven cheap routing
```

but something much less interesting.

---

# 6. The routing target

Compass should not simply be trained from an arbitrary human notion of “question difficulty”.

The current research direction uses Oracle-v2.

Oracle-v2 preserves the recall achieved by every strategy:

```text SIMPLE
MULTI_HOP
UNCERTAIN
```

and records:

```text best achievable recall
gold_route_v2
oracle_sufficient
```

The conceptual Oracle target is:

```text Which strategy gives the strongest useful retrieval result,
while preferring the cheapest route when multiple routes are close?
```

This is a much better learning target than:

```text What does this question sound like?
```

---

# 7. Oracle-v2 target definition

The core Oracle-v2 logic is conceptually:

```python
best=max(recs.values())

q.ladder_recalls=recs

q.gold_route_v2=next(
    l for l in ladder
    if recs[l]>=best-eps
)

q.oracle_sufficient=best>=1.0-eps
```

Interpretation:

```text all routes evaluated
        ↓
all recalls stored
        ↓
best recall identified
        ↓
cheapest route within epsilon of best chosen
        ↓
full-sufficiency status stored separately
```

This gives Compass a target that is:

```text retrieval-grounded
```

rather than merely:

```text linguistically intuitive
```

---

# 8. Why `oracle_sufficient` matters for training

Not every benchmark question is currently guaranteed to be solvable by the retrieval ladder.

Historical test status:

```text accepted questions = 27
Oracle-v2:
    SIMPLE       18
    MULTI_HOP     7
    UNCERTAIN     2

oracle insufficient = 9
```

The important point is:

```text insufficient
```

does not mean:

```text genuine semantic uncertainty
```

It means that under the tested ladder and exact evidence-recall metric, no strategy achieved complete gold evidence coverage.

A router trained on these cases without care could learn a misleading rule such as:

```text hard-to-retrieve question -> UNCERTAIN
```

instead of learning:

```text choose the most useful strategy
```

That is why the project has a distinct:

```text v2_sufficient
```

training concept.

---

# 9. Preferred training data scheme

The preferred training path is:

```text Oracle-v2
+
sufficiency-aware filtering
```

Conceptually:

```text all training questions
      |
      v
Oracle-v2 labeling
      |
      +---- sufficient ----> candidate routing examples
      |
      +---- insufficient --> keep for analysis
                              but do not blindly train
```

The exact inclusion rule must be explicit in the run manifest.

Do not silently discard insufficient examples without recording the count.

A proper report should say:

```text raw train count
Oracle-labeled count
sufficient count
excluded insufficient count
final Compass training count
```

---

# 10. Why the current 27-question benchmark is not enough

The current accepted test benchmark has:

```text 27 questions
```

and the previous analysis explicitly concluded that Compass should not be trained on that small set.

There are two separate problems:

```text sample size
+
benchmark structural quality
```

The clean intersection of:

```text audit-passed
AND
retrieval-sufficient
```

was entirely composed of SIMPLE examples in the previous review manifest.

That means the current test benchmark is not a healthy standalone training source for all route types.

Do not train a serious model by simply copying the 27 test questions into the training set.

---

# 11. The target dataset scale

Previous project planning suggested aiming for roughly:

```text ~150+ clean labelled questions
```

before treating Compass training as meaningful.

A possible long-term distribution was approximately:

```text 50 SIMPLE
50 MULTI_HOP
30–40 CHAIN
20–30 TEMPORAL
```

The exact numbers are not a requirement.

The stronger principle is:

> **Quality and route diversity matter more than hitting an arbitrary count.**

Do not manufacture difficult questions merely to satisfy a class quota.

---

# 12. Benchmark quality still dominates model quality

A learned router can only be as good as the labels it receives.

Examples of previously identified benchmark problems include:

```text incompatible quantity comparisons
one-passage questions mislabeled as multi-hop
temporal pairs that do not track the same claim
chain questions whose answer is already in the abstract
unsupported reference-answer claims
gold chunks that do not clearly support the question
```

The V2 benchmark generator was strengthened with:

```text dense + BM25 candidate sourcing
scientific-signal overlap
specific anchor matching
near-duplicate rejection
evidence-section requirements
complementary evidence checks
temporal constraints
chain same-paper constraints
structured generation
support audit
```

These controls should remain strict.

A small training set with clean labels is more valuable than a large training set with noisy labels.

---

# 13. Compass label vocabulary

The current route vocabulary is:

```text SIMPLE
MULTI_HOP
UNCERTAIN
```

Do not silently change this vocabulary during the first Compass implementation.

The important caveat is that `UNCERTAIN` has had overloaded historical meanings.

Oracle-v2 separates retrieval insufficiency using:

```text oracle_sufficient
```

Future benchmark versions may introduce a more explicit insufficiency state, but the first Compass experiment should be a controlled learned-routing implementation rather than a simultaneous label-taxonomy redesign.

---

# 14. Dataset record design

A training example should preserve enough metadata for auditability.

A useful conceptual record is:

```json
{
  "id":"...",
  "question":"...",
  "label":"SIMPLE",
  "oracle_sufficient":true,
  "ladder_recalls":{
    "SIMPLE":1.0,
    "MULTI_HOP":1.0,
    "UNCERTAIN":1.0
  }
}
```

Not every internal field must be fed into the model.

In fact, the model input should remain:

```text question
```

The additional fields are supervision and audit metadata.

---

# 15. Do not feed Oracle metadata into Compass

The following are acceptable as training supervision metadata:

```text gold_route_v2
oracle_sufficient
ladder_recalls
```

The following are not acceptable as model input at inference:

```text gold_route_v2
oracle_sufficient
retrieval results
gold chunks
answer context
```

This distinction is crucial:

```text label used to train
```

is not the same as:

```text label visible to the model
```

---

# 16. Train/validation/test split

The model must be evaluated on held-out examples.

A robust split should avoid leakage through:

```text identical questions
near-duplicate questions
same generated item copied across files
same paper appearing in train and test
```

The exact splitting policy should be decided from the corpus structure.

For a paper-facing experiment, a stronger evaluation is:

```text paper-disjoint holdout
```

where feasible.

Why?

Because otherwise the model may learn paper-specific vocabulary rather than routing behavior.

---

# 17. Paper-disjoint evaluation principle

Suppose a set of questions all come from a small number of papers.

A random question split can produce:

```text Train:
    paper A question 1
    paper A question 2

Test:
    paper A question 3
```

This is weaker than:

```text Train:
    papers A/B/C/...

Test:
    unseen papers X/Y/...
```

A paper-disjoint split better tests whether Compass learned:

```text routing patterns
```

instead of:

```text document-specific lexical shortcuts
```

The feasibility depends on the final number of papers and question density.

Document the actual split used.

---

# 18. Base model selection

The planned architecture requires:

```text small frozen base model
```

The exact checkpoint is not currently fixed by the historical benchmark work.

That choice must therefore be treated as an explicit experiment decision.

Selection criteria should include:

```text model size
tokenizer compatibility
sequence length
local inference speed
LoRA support
Python/PyTorch ecosystem support
memory requirement
license
reproducibility
```

Do not claim a model is selected until the exact checkpoint and revision are recorded.

---

# 19. Keep the backbone frozen

The intended architecture is:

```text base model = frozen
LoRA = trainable
classification head = trainable
```

This keeps Compass:

```text small
cheap to fine-tune
easy to deploy
easy to reproduce
```

It also strengthens the research story because the learned routing behavior is isolated in a compact adaptation rather than obtained by fully fine-tuning a large model.

---

# 20. Classification head

The routing output is a three-class classification problem under the current vocabulary:

```text SIMPLE
MULTI_HOP
UNCERTAIN
```

A conventional classification head can map the learned representation to:

```text 3 logits
```

then:

```text softmax
```

provides probabilities.

Conceptually:

```text hidden representation
        ↓
linear head
        ↓
3 logits
        ↓
softmax
        ↓
route probabilities
```

The predicted route is:

```text argmax(probabilities)
```

The reported confidence can be:

```text max(probabilities)
```

unless a different calibrated confidence definition is explicitly adopted.

Do not call raw softmax maximum a “calibrated confidence” without calibration analysis.

---

# 21. Loss and training objective

The simplest first training objective is standard multi-class classification:

```text cross-entropy loss
```

with classes:

```text SIMPLE
MULTI_HOP
UNCERTAIN
```

Class weighting may become useful if the final training distribution is severely imbalanced.

However:

> Do not automatically introduce weighted loss just because class counts are uneven.

First inspect the actual label distribution.

A weighted loss is itself a modeling choice that should be reported.

---

# 22. Class imbalance

Before training, compute:

```text total examples
SIMPLE count
MULTI_HOP count
UNCERTAIN count
percentage per class
```

Also compute:

```text sufficient-only distribution
```

Do not train until the distribution is understood.

The historical test set had:

```text SIMPLE = 18
MULTI_HOP = 7
UNCERTAIN = 2
```

under Oracle-v2 labels, but this is a test-set observation and must not be treated as the final training distribution.

---

# 23. What to do with `UNCERTAIN`

`UNCERTAIN` needs particular scrutiny.

Ask:

```text Is this a real routing state?
Or is it mostly a benchmark/retrieval-failure state?
```

The current framework already separates:

```text route label
```

from:

```text oracle_sufficient
```

That is the correct place to begin.

Do not collapse:

```text insufficient
```

into:

```text UNCERTAIN
```

without an explicit research justification.

---

# 24. Data augmentation

Do not begin by using uncontrolled LLM rewriting to generate hundreds of extra examples.

That can introduce:

```text label drift
source leakage
syntactic artifacts
duplicate questions
artificial class boundaries
```

The preferred order is:

```text clean benchmark candidates
        ↓
human review
        ↓
Oracle-v2 labels
        ↓
train set
```

Only later consider controlled augmentation.

Any augmented examples should be separately identifiable.

---

# 25. Prevent lexical shortcut learning

A serious concern for a question-only router is shortcut learning.

For example, the model could learn:

```text "combine"
"compare"
"between"
"respectively"
```

→ MULTI_HOP

without actually learning the retrieval strategy.

This is why evaluation should include:

```text paraphrases
cross-paper holdouts
different scientific subtopics
simple questions with complex wording
multi-hop questions with simple wording
```

A good routing model should respond to the required evidence structure, not just a handful of trigger words.

---

# 26. Hard-negative examples

Hard negatives are especially useful.

Examples:

```text SIMPLE question with words like "compare"
but answer is directly retrievable
```

and:

```text MULTI_HOP question whose wording is simple
but requires two independent evidence pieces
```

These examples can prevent the model from becoming a shallow keyword classifier.

However, hard negatives must be genuinely valid benchmark examples.

Do not fabricate them solely for training balance.

---

# 27. Compass confidence

Compass is expected to expose:

```text route
confidence
```

The confidence value is useful for later selective escalation.

Possible downstream logic:

```text high confidence
    ↓
execute Compass route

low confidence
    ↓
escalate to C2 / LLM router
```

But first establish whether the raw model confidence is meaningful.

---

# 28. Confidence calibration

Do not assume:

```text softmax 0.90 = 90% probability of correctness
```

A model can be highly overconfident.

Later calibration methods may include:

```text temperature scaling
validation-set calibration
reliability curves
expected calibration error
```

Calibration is especially important if Compass is used as a gate for expensive fallback.

The initial Week 4 experiment should report raw confidence separately from calibrated confidence.

---

# 29. Compass implementation contract

The existing placeholder contract is conceptually:

```python
class CompassRouter(Router):
    name="compass"

    def route(self,query:str)->RouteDecision:
        ...
```

The actual implementation should:

```text load local model
load tokenizer
load adapter/head
tokenize question
run inference
map logits to route
return RouteDecision
```

It should not:

```text retrieve documents
call the answering LLM
read gold evidence
perform answer generation
```

---

# 30. Model loading

The production router should not retrain or initialize training state during every query.

The intended lifecycle is:

```text process startup
    ↓
load tokenizer/model/adapter/head
    ↓
reuse inferences
```

not:

```text every route()
    ↓
load model from disk
    ↓
route
    ↓
destroy model
```

The latter would make latency measurements meaningless.

---

# 31. Device and inference mode

The implementation should use the appropriate inference path for the available machine.

Conceptually:

```python
model.eval()

with torch.inference_mode():
    ...
```

The exact device handling should be detected rather than assumed.

For example:

```text CUDA when available
CPU fallback otherwise
```

Record the actual hardware/device for reproducibility.

---

# 32. Reproducibility settings

Training should record:

```text Python version
PyTorch version
Transformers version
PEFT version
seed
base checkpoint
adapter configuration
learning rate
batch size
gradient accumulation
epochs / max steps
sequence length
train/val/test counts
class weights
device
```

Do not report only:

```text trained Compass successfully
```

The checkpoint should be reproducible from the recorded configuration.

---

# 33. Minimal first training configuration

The first run should intentionally be conservative.

Example conceptual setup:

```text frozen backbone
LoRA adapter
classification head
small batch
few epochs
early stopping
fixed seed
```

The objective is not to maximize the first training score.

The objective is to establish:

```text end-to-end training works
checkpoint loads
inference works
evaluation is correct
```

Then iterate.

---

# 34. Overfitting warning

A tiny dataset can produce:

```text 95% train accuracy
```

while generalizing poorly.

Therefore always report at least:

```text training loss
validation loss
train accuracy
validation accuracy
held-out test metrics
```

A good Compass result must survive held-out evaluation.

---

# 35. Metrics for Compass

## Routing metrics

```text accuracy
macro F1
per-class precision
per-class recall
confusion matrix
```

Macro F1 matters when route classes are imbalanced.

## Retrieval metrics

The real downstream metric remains:

```text evidence recall
```

Run the actual retrieval system using Compass-selected routes.

## Efficiency metrics

```text routing latency
end-to-end latency
LLM calls
provider calls
tokens
cache hits
fallback rate
```

This is where Compass should have a major advantage over an LLM router.

---

# 36. The most important comparison

The minimum learned-routing comparison is:

```text B  Static
C1 Existing LLM Router
C2 Oracle-Aligned LLM Router
D  Compass
E2 Oracle-v2 reference
```

The ideal story is not:

```text Compass gets the highest raw classification accuracy.
```

It is:

```text Compass approaches useful Oracle retrieval quality
while being much cheaper and faster than C1/C2.
```

---

# 37. Retrieval evaluation loop

A proper Compass evaluation is:

```text question
   ↓
Compass
   ↓
selected route
   ↓
actual retrieval strategy
   ↓
retrieved chunks
   ↓
evidence recall
```

Do not stop at:

```text question
   ↓
Compass
   ↓
classification accuracy
```

That tests classification, but not the real AtlasRAG objective.

---

# 38. Route accuracy vs retrieval effectiveness

A Compass model can have:

```text high route agreement
```

yet:

```text mediocre evidence recall
```

because the retrieval strategies themselves have limitations.

Conversely, Compass can disagree with Oracle while selecting a route that retrieves the same gold evidence.

Therefore report both:

```text route agreement
```

and:

```text evidence recall
```

The latter is the primary system outcome.

---

# 39. Cost and latency comparison

Compass should be compared against the LLM routers on:

```text routing latency
LLM provider calls
LLM tokens
end-to-end query latency
```

The expected qualitative relationship is:

```text Compass
    ↓
local inference
    ↓
no provider routing call

C1/C2
    ↓
remote LLM inference
    ↓
token/provider cost
```

Do not report “zero cost” unless actual deployment cost assumptions justify that statement.

The meaningful claim is usually:

```text no additional external LLM routing call
```

or:

```text substantially lower routing computation/cost
```

depending on the deployment environment.

---

# 40. Escalation design

Once the basic Compass model works, the next architecture can be:

```text                 Compass
                    /       \
             high confidence low confidence
                /               \
               v                 v
          selected route      C2 fallback
```

This is the project’s intended bridge into selective escalation.

However:

> Do not introduce escalation into the first Compass experiment.

First establish the raw Compass policy.

Otherwise the result becomes difficult to attribute.

---

# 41. First Compass experiment

The first Compass experiment should answer only:

> What happens when Compass alone chooses the route?

Use:

```text D = Compass only
```

No fallback.

This gives a clean measurement of:

```text learned routing capability
```

Then later:

```text D + escalation
```

can test robustness.

---

# 42. Compass experiment isolation

Do not modify C1 or C2 while implementing D.

Keep:

```text C1 = historical LLM baseline
C2 = separate Oracle-aligned LLM baseline
D  = Compass
```

This preserves causal interpretation.

---

# 43. Suggested repository files

The exact current repository layout must be inspected before editing.

Likely conceptual components include:

```text
src/atlasrag/routers/compass.py
```

plus a training area such as:

```text
scripts/
notebooks/
training/
```

The historical design referenced notebook-based training and local/Hugging Face checkpoint loading.

Do not create duplicate model-loading paths without first inspecting the existing repository.

---

# 44. Recommended training artifact layout

A clear artifact layout could look like:

```text
artifacts/
    compass/
        config.json
        tokenizer/
        adapter/
        classifier/
        train_manifest.json
        metrics.json
```

The exact path is flexible.

The key requirement is that:

```text
model
+
training metadata
+
evaluation metadata
```

stay together.

Do not commit large model weights to Git unless that is explicitly intended and appropriate.

---

# 45. Training manifest

Every Compass training run should have a machine-readable manifest containing:

```text
dataset version
dataset hash
question count
sufficient count
class counts
base model
base model revision
LoRA config
training hyperparameters
seed
software versions
device
checkpoint path
best validation score
```

This is particularly important because the benchmark is still evolving.

---

# 46. Dataset versioning

Do not train against a mutable file named only:

```text train.jsonl
```

without recording its exact version.

Prefer:

```text benchmark_v2_...
```

or a manifest with a dataset hash.

When benchmark questions change:

```text new dataset
→ new hash
→ new training run
```

Do not silently retrain using changed labels under the same experiment name.

---

# 47. Avoid test leakage during dataset generation

A dangerous shortcut would be:

```text test question
→ paraphrase
→ train question
```

Even if the wording changes, the evidence/route structure may leak.

Training generation must use a separate pool.

The test set must remain a true evaluation set.

---

# 48. Recommended evaluation subsets

Report Compass on at least:

```text full held-out set
```

and:

```text oracle_sufficient == true
```

where applicable.

Also report:

```text per question type
```

especially:

```text SIMPLE
MULTI_HOP
CHAIN
TEMPORAL
```

The exact available classes depend on the repaired benchmark.

---

# 49. What to do with unresolved temporal cases

Do not force Compass to learn from known-invalid temporal examples.

Use:

```text validated temporal examples
```

only.

If the benchmark has no reliable temporal examples yet, report:

```text insufficient temporal training/evaluation data
```

rather than pretending Compass covers temporal routing.

---

# 50. Hard-negative evaluation

A strong Compass test suite should contain cases where:

```text surface wording suggests SIMPLE
but Oracle route is MULTI_HOP
```

and:

```text surface wording suggests MULTI_HOP
but SIMPLE is sufficient
```

These are much more informative than easy examples.

They directly test whether the model learned:

```text retrieval need
```

instead of:

```text keyword triggers
```

---

# 51. Evaluation against unseen scientific topics

Because the corpus is scientific, consider evaluating on question groups where the scientific terminology differs between training and test.

For example:

```text training:
    H0 / BAO / CMB examples

test:
    different cosmological parameters or surveys
```

The exact scientific split should be based on the actual corpus, not invented categories.

The purpose is to test whether routing is structural rather than memorized.

---

# 52. Error taxonomy for Compass

For every meaningful failure, classify:

```text A. wrong route
B. correct route but incomplete retrieval
C. correct route but decomposition failure
D. benchmark/gold-evidence issue
E. confidence failure
F. implementation/inference bug
```

This avoids blaming Compass for downstream problems.

---

# 53. Confidence-threshold analysis

After the raw Compass model works, create a threshold sweep.

For confidence threshold:

```text τ
```

define:

```text confidence >= τ
    → trust Compass

confidence < τ
    → escalate
```

Then measure:

```text coverage
fallback rate
evidence recall
latency
LLM tokens
provider calls
```

This is the beginning of selective routing.

Do not choose the threshold from the final test set without a validation protocol.

---

# 54. Calibration before production thresholding

A confidence threshold should ideally be selected on:

```text validation set
```

not:

```text test set
```

The test set should remain for final reporting.

This prevents repeated test-set tuning.

---

# 55. Compare Compass with a simple heuristic

A learned model should also be compared with cheap non-LLM controls.

The project already has a heuristic development strategy.

A useful question is:

```text Does Compass actually beat a trivial keyword heuristic?
```

Otherwise the complexity of LoRA training may not be justified.

The heuristic must remain clearly labeled as a development/control baseline, not as the main research system.

---

# 56. Compass vs always-strong route

The project has an important control:

```text F = always UNCERTAIN / strongest route
```

which historically reached:

```text 0.76
```

on Run 1.

Compass must be evaluated against this kind of control because it is easy to build a router that saves calls but simply loses recall.

The desired outcome is a meaningful quality/cost tradeoff.

---

# 57. Compass vs empirical Oracle

The Oracle is not a deployable model.

It is the empirical reference:

```text best achievable strategy under the chosen retrieval ladder
```

A useful Compass result is therefore:

```text Compass recall
        vs
Oracle recall
```

and:

```text Compass cost
        vs
Oracle routing cost
```

The Oracle is not expected to be beaten under the exact recall construction.

If Compass appears to outperform E2 substantially, inspect the metric implementation before celebrating.

---

# 58. Statistical evaluation

Use paired question-level comparisons.

At minimum compare:

```text D - C1
D - C2
D - B
D - E2
```

Preserve:

```text wins
ties
losses
```

and paired confidence intervals where appropriate.

Do not rely only on independent aggregate averages.

---

# 59. Useful Compass table

The final Week 4 report should contain something like:

| Policy | Evidence Recall | Route Agreement | Routing Time | Provider Calls/Q | Tokens/Q | Fallback Rate |
|---|---:|---:|---:|---:|---:|---:|
| B Static | | | | | | |
| C1 LLM | | | | | | |
| C2 LLM | | | | | | |
| D Compass | | | | | | |
| E2 Oracle | | | | | | |

Values must come from actual runs.

Do not pre-fill expected numbers.

---

# 60. Training checklist

Before starting training:

```text [ ] benchmark version declared
[ ] training split created
[ ] validation split created
[ ] test split frozen
[ ] no test leakage
[ ] Oracle-v2 labels generated
[ ] oracle_sufficient inspected
[ ] class balance measured
[ ] base checkpoint recorded
[ ] license checked
[ ] seed fixed
[ ] training config recorded
[ ] checkpoint destination chosen
```

---

# 61. Inference checklist

Before integrating D:

```text [ ] model loads without network access if intended
[ ] tokenizer loads
[ ] adapter loads
[ ] classifier head loads
[ ] model is eval mode
[ ] inference_mode used
[ ] route vocabulary validated
[ ] confidence returned
[ ] malformed output impossible at model interface
[ ] no retrieval context passed
[ ] no answer-generation context passed
```

---

# 62. Integration test checklist

Run:

```text question
→ Compass
→ SIMPLE retrieval
```

then:

```text question
→ Compass
→ MULTI_HOP retrieval
```

then:

```text question
→ Compass
→ UNCERTAIN/fallback path
```

Verify that:

```text correct router object is used
correct route reaches correct strategy
results are persisted
stats are recorded
```

---

# 63. Exact initial commands

Start with repository inspection:

```powershell
git status
git log --oneline --decorate -10
python -m pytest -q
```

Inspect the current Compass placeholder:

```powershell
Get-Content .\src\atlasrag\routers\compass.py
```

Inspect router contracts:

```powershell
Get-Content .\src\atlasrag\routers\base.py
```

Inspect experiment mapping:

```powershell
Get-Content .\src\atlasrag\bench\experiments.py
```

Inspect Oracle-v2:

```powershell
Get-Content .\src\atlasrag\bench\oracle_v2.py
```

Inspect current benchmark schema:

```powershell
Get-Content .\src\atlasrag\bench\schema.py
```

The exact file names must be verified before acting on these commands.

---

# 64. Training workflow

The recommended high-level workflow is:

```text
1. verify repository
2. verify benchmark version
3. build Oracle-v2 train labels
4. inspect class distribution
5. create train/validation split
6. freeze test set
7. select/record base model
8. build LoRA + classification head
9. train first reproducible baseline
10. save checkpoint + manifest
11. evaluate classifier
12. integrate CompassRouter
13. run retrieval-only D
14. compare D with B/C1/C2/E2
15. inspect failures
16. only then add confidence-based escalation
```

---

# 65. First training objective

The first Compass run should not optimize every possible metric simultaneously.

Stage 1 objective:

```text stable training
+
valid checkpoint
+
correct inference
```

Stage 2 objective:

```text held-out route quality
```

Stage 3 objective:

```text retrieval evidence recall
```

Stage 4 objective:

```text quality/cost tradeoff
```

This separation makes debugging much easier.

---

# 66. What success would look like

A strong result would have several properties simultaneously:

```text Compass evidence recall near the stronger baselines

Compass route latency far below C1/C2

no external routing LLM call

reasonable confidence behavior

robustness across question types

good performance on held-out papers/questions

small, reproducible checkpoint
```

The exact thresholds should be derived from the measured baselines.

Do not define a winning percentage after seeing the final result.

---

# 67. What failure would mean

A weak Compass result is still useful.

For example:

```text high classification accuracy
but weak retrieval recall
```

would imply:

```text routing labels do not perfectly predict downstream retrieval outcome
```

Another useful null result:

```text Compass ≈ heuristic
```

would suggest the learned architecture does not add enough value.

Another:

```text Compass much cheaper
but lower recall than C2
```

could still justify:

```text selective escalation
```

where low-confidence Compass queries call C2.

---

# 68. The likely next architecture after raw Compass

If the raw Compass result is useful:

```text                    Question
                       |
                       v
                   Compass
                  /        \
             confident   uncertain
                |             |
                v             v
          chosen route       C2
                              |
                              v
                         chosen route
```

This creates a hybrid:

```text cheap most of the time
expensive only when necessary
```

That is likely more interesting operationally than forcing Compass to solve every query.

But this is a separate experiment.

---

# 69. Selective escalation metrics

Once escalation exists, report:

```text Compass coverage
fallback rate
fallback rate by question type
evidence recall
LLM calls/query
tokens/query
provider calls/query
latency
```

A good selective system should ideally show:

```text most queries handled locally
+
difficult queries escalated
+
small recall loss or recall improvement
+
large reduction in LLM routing cost
```

Again, this is a later phase.

---

# 70. Do not tune thresholds on the test set

The process should be:

```text train
    ↓
validation
    ↓
threshold selection
    ↓
freeze threshold
    ↓
test
```

Do not repeatedly inspect test results and change:

```text confidence threshold
```

until the test score improves.

That creates overfitting to the benchmark.

---

# 71. Long-term paper framing

The most defensible research story is not:

```text We fine-tuned a classifier for RAG.
```

It is closer to:

```text We formulate retrieval-strategy selection as a question-only
decision problem, construct Oracle-grounded supervision from observed
evidence retrieval, and investigate whether a lightweight learned router
can approximate the useful policy at much lower routing cost.
```

The exact final claim depends on actual results.

Do not write the paper conclusion before the experiment is complete.

---

# 72. Reproducibility package

A finished Compass experiment should include:

```text dataset manifest
training config
base model name/revision
LoRA config
seed
software versions
checkpoint
classifier mapping
evaluation results
per-question predictions
confusion matrix
paired comparisons
```

This will make later portfolio/paper work substantially easier.

---

# 73. Git discipline

Before training:

```powershell
git status
```

After implementation:

```powershell
git diff
git status
```

Before committing:

```powershell
python -m pytest -q
```

Do not commit:

```text .env
raw private credentials
temporary caches
large generated junk
provider secrets
unreviewed experimental outputs
```

Large model weights should have an intentional storage strategy.

---

# 74. Historical files that must remain untouched

The following remain protected:

```text
data/bench/questions.jsonl
data/bench/questions_v1_frozen.jsonl
results/run1/
src/atlasrag/bench/oracle_v2.py
```

Unless a later controlled change is explicitly justified, also preserve:

```text C1
C2
B
E2
```

as separate experimental components.

---

# 75. Research-safety checklist

Before declaring Compass successful:

```text [ ] no test leakage
[ ] no evidence-context leakage
[ ] no gold-route input leakage
[ ] benchmark version recorded
[ ] training data version recorded
[ ] class distribution reported
[ ] held-out evaluation used
[ ] evidence recall measured
[ ] latency measured
[ ] external LLM calls measured
[ ] failures inspected
[ ] comparison against heuristic/control included
[ ] Run 1 untouched
```

---

# 76. What the next coding agent must report

The agent implementing Compass should return:

```text
Current commit:
Branch:
Tests before:
Tests after:

Benchmark version:
Train count:
Validation count:
Test count:

Class distribution:
SIMPLE:
MULTI_HOP:
UNCERTAIN:

Oracle-sufficient count:
Excluded insufficient count:

Base model:
Revision:
LoRA config:
Classifier head:

Training command:
Training time:
Best validation metric:

Checkpoint path:
Manifest path:

D classification metrics:
Accuracy:
Macro F1:

D retrieval metrics:
Evidence recall:

Routing latency:
LLM routing calls:
Provider calls:
Tokens:

C1 comparison:
C2 comparison:
B comparison:
E2 comparison:

Main failure category:
Next action:
```

Do not accept:

```text "Compass trained successfully"
```

without the underlying artifacts and measurements.

---

# 77. Week 4 completion criteria

Week 4 is complete only when:

```text Compass training is reproducible

Compass checkpoint loads successfully

CompassRouter.route() works

Compass receives question-only input

No retrieval/evidence leakage exists

Held-out classification metrics exist

Retrieval evidence-recall metrics exist

C1/C2/B/E2 comparisons exist

Routing latency and provider-call accounting exist

Failure analysis is documented
```

If these are not all available, Week 4 is still in progress.

---

# 78. Final Week 4 principle

The central idea is:

> **Compass is valuable only if it learns a useful retrieval policy, not merely a question-type label.**

The implementation should therefore preserve the chain:

```text validated benchmark
        ↓
Oracle-v2 supervision
        ↓
question-only learned router
        ↓
actual retrieval strategy
        ↓
evidence recall
        ↓
cost / latency measurement
```

That connects the model directly to the actual AtlasRAG research objective.

Do not optimize Compass for a classification score that does not translate into better retrieval behavior.

The correct goal is:

```text approach useful Oracle-level strategy selection
+
avoid expensive per-query LLM routing
+
remain honest about benchmark and retrieval limitations
```

That is the basis on which the next phase—selective escalation and dynamic routing—can be evaluated cleanly.
