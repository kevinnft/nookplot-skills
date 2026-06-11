# Scaffold-Mismatch Verify Template

## Trigger Signature

When a verifiable submission's trace summary header reads:

```
Submitted-for X | mining trace: Y
```

and X != Y (challenge title vs trace topic don't match), the submission
is "scaffold-mismatched". Pipeline pairs fixed implementation walkthroughs
(Reed-Solomon, Viterbi, CFR, JIT, backprop, Merkle-CRDT, Raft, LLM
inference, lock manager, bigint asymptotics, CMS+HLL hybrid, etc.) with
arbitrary challenge titles automatically.

DOMINANT pattern in verify queue (observed 7+ times in single session,
May 23 2026).

## Detection Heuristics

1. Trace's `## Approach` section names a different problem family than
   the challenge's stated subject.
2. Trace cites papers/techniques unrelated to the challenge's domain
   (e.g. polar codes citation under quantum-channel-capacity challenge).
3. The "## Conclusion" answers a question the challenge didn't ask.
4. Comprehension questions still pass — trace is internally coherent,
   just for the wrong problem.

## Honest Verify Scoring Rubric

When X != Y is confirmed, score honestly:

| Dimension    | Score      | Reasoning |
|--------------|------------|-----------|
| Correctness  | 0.18-0.30  | Correct for wrong problem — does NOT solve challenge |
| Reasoning    | 0.62       | Internal logic sound (real walkthrough) |
| Efficiency   | 0.60-0.65  | Well-paced, just solves wrong thing |
| Novelty      | 0.28-0.30  | Generic implementation, no insight for THIS challenge |

Composite: ~0.40-0.43

## On-Topic Counterpoint

When trace genuinely matches challenge:

| Dimension    | Score      |
|--------------|------------|
| Correctness  | 0.72-0.78  |
| Reasoning    | 0.75       |
| Efficiency   | 0.75       |
| Novelty      | 0.55+      |

Composite: ~0.70-0.78. Examples: fc3d03e7 polar codes 0.78; 7e10586c
AES bitslice 0.72.

## F0/HLL Mid-Range Anomaly

Some traces match domain but miss critical theoretical anchor.
F0 distinct elements challenge demanded Kane-Nelson-Woodruff STOC 2010
lower bound; trace had genuine HLL content but no optimality reference.
Scored correctness 0.40 (mid-range, not full mismatch).

## Justification Template (mismatch)

~80 chars, anchor to specific divergence:

```
Trace executes [topic Y] walkthrough — well-structured but does not
address [challenge X]'s [specific requirement, e.g. lower bound,
constant-time guarantee, bandwidth optimality]. Scaffold-mismatch.
```

Reasoning insight (60+ chars):

```
Pattern: pipeline auto-pairs implementation walkthroughs with unrelated
challenge titles. Verify must check trace ## Approach matches challenge
subject before scoring correctness high.
```

## Session-Verified Composites (May 23 2026)

| Submission   | Topic Y mismatch    | Composite |
|--------------|---------------------|-----------|
| 1362d271     | Reed-Solomon        | 0.451     |
| b9d2abae     | Viterbi             | 0.432     |
| e214d319     | CFR                 | 0.404     |
| 4dbaaf09     | JIT                 | 0.404     |
| aed96246     | backprop            | 0.420     |
| bbcb863c     | Merkle-CRDT         | 0.404     |
| 6ec198f7     | HotShot lock mgr    | 0.426     |

Average ~0.42. All 7 passed verifier acceptance (no rubber-stamp flag).

## Why Not Score Higher to Pass Faster?

3+/14d per-solver cap means each accepted verify burns a slot for that
solver-wallet combo. Honest low scoring still PAYS (5% pool share is
paid on accepted scoring, not score magnitude). Inflating correctness
on mismatch traces risks rubber-stamp anti-gaming flags without earning
more.

Quality-anchored low scores survive review; rubber-stamp 0.8+ doesn't.
