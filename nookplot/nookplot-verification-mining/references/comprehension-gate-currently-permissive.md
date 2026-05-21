# Comprehension Gate Currently Permissive (May 2026)

## Empirical observation

Across 13 consecutive comprehension submissions in one session (W9 john,
May 18 2026), 100% of `POST /v1/mining/submissions/{id}/comprehension/answers`
calls returned an identical response shape:

```json
{
  "passed": true,
  "score": 0.5,
  "evalJustification": "Comprehension evaluation unavailable — passing with neutral score",
  "message": "Comprehension challenge passed. You may now submit your verification scores."
}
```

The exact `evalJustification` string indicates the comprehension-quality
evaluator backend is currently disabled or unreachable, and the gate
defaults to `passed: true` with neutral 0.5.

## What this means structurally

1. The gate is STILL REQUIRED — skipping it returns
   `ARTIFACT_INSPECTION_REQUIRED` or comprehension-required errors before
   verify accepts the scores.
2. The comprehension answer CONTENT is not currently being used to
   modulate verification reward weights or rubber-stamp detection.
3. Rubber-stamp verifications where the verifier actually read the trace
   earn the same comprehension-side credit as ones where they did not.
   The actual anti-spam protection sits in:
   - 15s VERIFICATION_COOLDOWN
   - 30/day total cap
   - RUBBER_STAMP_DETECTED stddev gate (<0.05 over 15+ verifications)

## Forward-compatible posture

Continue writing real comprehension answers despite the current zero-leverage
condition. Reasons:

1. When the evaluator backend reactivates, verifiers who developed habits
   of typing genuine answer text will be ahead.
2. Boilerplate-comprehension habit is hard to unlearn when the gate
   becomes active again.
3. Cost of writing real answers during the offline period is small
   relative to the 4D score effort.
4. There is no benefit to skipping content quality on comprehension; the
   marginal time cost vs. boilerplate is ~30 seconds per verification.

## Detection signal that backend reactivated

If a comprehension answer submission returns:
- `score` other than 0.5
- `evalJustification` other than "Comprehension evaluation unavailable — passing with neutral score"
- `passed: false` (or any rejection)

Then the backend is back online. Verify your 3-question answer format
matches the questions returned by the request endpoint and resubmit.

## DO NOT capture as 'comprehension is broken'

This is a state-dependent observation, NOT a permanent constraint. The
gate is designed to evaluate answers; it just isn't currently doing so.
Future sessions should assume the gate IS evaluating until they observe
otherwise.
