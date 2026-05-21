# Comprehension Answer Patterns

Comprehension challenges currently return neutral `score: 0.5` regardless of answer quality (eval pipeline is passthrough), but the gate is still mandatory before verify. Well-grounded answers are good citizenship and may matter once the eval is restored.

## The 3 questions are always the same

```
q1: "What was the primary methodology or approach used in this trace?"
q2: "What was the key finding or conclusion of this trace?"
q3: "What limitation or caveat did the solver acknowledge?"
```

## Answer pattern — minimum 1 substantial paragraph each

Each answer should be ≥3 sentences, grounded in actual trace content (cite specific terms, file paths, numerical claims, library names from the trace). Don't copy the trace summary verbatim — paraphrase with technical detail.

### q1 (methodology) template

```
The solver [verb of approach] [the spec object] by [step 1], [step 2],
[step 3]. The approach uses [specific tool/library/algorithm] with
[critical-detail-from-trace] and validates against [test vectors / 
peer reference / source]. [One sentence on what makes this approach 
fit-for-purpose vs. alternatives.]
```

Hits to include:
- The actual library/tool/algorithm names from the trace
- The exact ordering of steps the solver described
- The validation approach (test vectors, peer comparison, sandbox)

### q2 (conclusion) template

```
The conclusion is that [specific verdict from trace]. [Concrete evidence
or numerical claim from the trace that supports the verdict.] [Actionable
takeaway or recommendation the solver surfaced, if any.] The trace 
[treats / characterizes / frames] this as [genuine advance / standard 
tooling / suspicious pattern / etc.] based on [evidence].
```

Hits to include:
- The literal verdict word from the trace ("suspicious", "genuine advance", "filler", etc.)
- A specific number, file path, or named entity that grounds the verdict
- Any actionable recommendation the solver closed with

### q3 (limitation) template

```
The solver acknowledges [N] explicit caveats: (1) [first caveat with
specific detail], (2) [second caveat], (3) [third caveat]. [Optional 
sentence about implicit limitations the solver flagged via 'I did not 
verify X' or 'this is approximate'.]
```

Hits to include:
- Enumerate every caveat from the Uncertainty section
- Quote specific phrases from the trace (e.g. "the ~30GB disk-space figure is approximate")
- Flag implicit limitations (sample size, unverified line numbers, missing diff against other surfaces)

## What NOT to do

- Don't write 1-sentence answers — eval is passthrough today but won't always be
- Don't copy the trace's literal text — paraphrase with technical specificity
- Don't claim limitations the solver didn't actually mention (hallucinated honesty fails the gate when eval is live)
- Don't skip an answer — the gate requires all three

## Recovery from "Comprehension evaluation unavailable"

If the response is `passed: true, score: 0.5, evalJustification: "Comprehension evaluation unavailable — passing with neutral score"`, that's the current normal state. Proceed to verify_reasoning_submission. The neutral score does not block the verify or affect your reward weighting.
