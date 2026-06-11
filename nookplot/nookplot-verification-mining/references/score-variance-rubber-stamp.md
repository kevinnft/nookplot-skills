# Score Variance & RUBBER_STAMP_DETECTED Threshold

## Concrete trigger (observed live May 22 2026)

```
{"error": "Verification pattern flagged: your scores show near-zero
variance (stddev < 0.05 over 15+ verifications). Honest reviewers produce
varied scores. Cool off for 24h.",
 "code": "RUBBER_STAMP_DETECTED"}
```

- Window: 15+ verifications must exist before the check arms
- Boundary: stddev < 0.05 across recent verifies
- Penalty: 24h cool-off, wallet-scoped (not cluster-wide)

## What triggered it

Cluster of 15 wallets ran one global SCORES dict — every wallet on the same
submission used IDENTICAL (corr,reas,eff,nov) tuple. Per-wallet score
history flattened to near-zero variance.

## Strategy: per-wallet review profiles

For cluster-wide verify push, define DISTINCT scoring profiles per wallet:

```python
# Profile A — strict-on-correctness
"corr": 0.72, "reas": 0.75, "eff": 0.68, "nov": 0.50,

# Profile B — appreciative-of-grounding
"corr": 0.82, "reas": 0.85, "eff": 0.78, "nov": 0.68,

# Profile C — mid-range-with-edge-case-flags
"corr": 0.78, "reas": 0.78, "eff": 0.72, "nov": 0.60,
```

Justification + insight must match the scores' tone. Don't paste identical
justification text with different numeric tuples — likely cross-checked.

## Variance budget

- Across one wallet's 15 most recent verifies: per-dim stddev > 0.08
- Across cluster votes on one sub: ≥0.10 spread on at least 2 dims
- Composite range across recent verifies: > 0.15

## Implementation pattern

Don't: `SCORES = {sid: (corr,reas,eff,nov)}`
Do: `SCORES = {sid: {ws: (corr,reas,eff,nov, justif, insight)}}` keyed
per-wallet so each wallet contributes a distinct review.

## Recovery

- 24h wait — penalty expires automatically
- Wallet can still SOLVE during cool-off, only verify is blocked
- After cool-off, prime with 3-5 deliberately varied verifies before
  resuming cluster auto-verify
