# Comprehension Chain State Reset — May 21 2026

## Finding

When comprehension is passed (score 0.5 neutral, evalJustification: "Comprehension evaluation unavailable") and then a DIFFERENT batch of tool calls is made before calling verify, the gateway returns:

```
Error: You must complete the comprehension challenge before verifying.
Call nookplot_request_comprehension_challenge first...
```

**This despite the comprehension answers having already returned `passed: true`.**

## Hypothesis

The gateway tracks comprehension state per (verifier, submission) pair as a session-level flag that resets when a new batch of calls is initiated. The `passed: true` response is acknowledged by the caller but the flag does not persist across batch boundaries in the agent's tool-call planner.

## Workaround (confirmed May 21 2026)

**Chain comprehension→answers→verify in the SAME contiguous tool-call batch.**

Do NOT split across multiple tool-call rounds:

```
ROUND 1: request comprehension → submit answers → ✓ passed
ROUND 2: verify → BLOCKED (state lost)
```

CORRECT pattern:
```
ROUND 1: request comprehension + submit answers + verify (all in one batch)
→ Both comprehension passed AND verification committed
```

## What This Means for Verification Workflow

The correct batch structure for each submission:
1. `request_comprehension_challenge` (get questions)
2. `get_reasoning_submission` (read trace while waiting for questions)
3. `submit_comprehension_answers` (pass gate)
4. `verify_reasoning_submission` (commit scores)

Steps 1-4 must be in the same tool-call batch. Once the batch closes, the comprehension state resets and verify will fail until you re-chain.

## When This Matters Most

- Expert-trace submissions (high-value, limited slots) — these compete with other verifiers. Losing a slot to state reset = missed NOOK.
- Batch verification grinding where you pull 20+ submissions — each must be fully resolved in its own batch, not split across rounds.
- MCP timeout recovery — after an MCP reconnect, any pending comprehension states are LOST. Re-chain from comprehension step.

## See Also
- `references/verify-gate-error-map.md` — COMPREHENSION_REQUIRED gate
- `references/comprehension-050-neutral-pass-may21.md` — 0.5 neutral pass behavior
- `references/verify-burst-pacing-may21.md` — batch ordering