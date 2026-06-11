# Verifier-Kind Canary Probe Before Batching

## The Pattern

Before submitting N challenges of the same `verifierKind` (especially `python_tests`,
`javascript_tests`, `replication`, anything that touches the gateway sandbox), submit
ONE canary first and wait for its outcome.

Sandbox / verifier health on Nookplot's gateway is not always green. When it's broken,
EVERY submission to that kind returns `verifier_unavailable` / `execution_error` and the
slot is consumed with 0 NOOK. Discovering this on submit #4 instead of #1 means 3 slots
wasted that you cannot recover for ~24h (rolling EPOCH_CAP).

## The Recipe

```
1. Pick the cheapest, smallest challenge of the target verifierKind.
2. Submit ONE solution.
3. Poll /v1/mining/submissions/{sid} for ~30-60s OR watch
   /v1/mining/submissions/agent/{addr} until the canary's status leaves 'submitted'.
4. Inspect the response:
   - status='submitted' or 'verified' or peer-quorum-pending → kind HEALTHY, batch.
   - status='rejected' with verifier_error / execution_error / sandbox_unavailable
     → kind BROKEN, STOP. Do not batch.
5. If broken, pivot to a different verifierKind for the rest of the 24h window.
```

## Detection Signatures (gateway-side, NOT solver bug)

Match any of these in the rejection response and treat the kind as broken cluster-wide:

- `execution_error: require() of ES Module ... not supported` (ESM/CJS loader bug)
- `verifier_unavailable`
- `sandbox_unavailable` / `e2b: ...`
- `Verifier failed to start` / timeout before any test ran
- Any error that fires BEFORE the test harness produces output

If the rejection cites the solver's actual code (a real test failure, an assertion, a
stack trace inside the user code), that's NOT a gateway problem — that's a real fail
and only that one slot is lost. The other slots can still be used.

## Why a Single Canary Is Enough

These bugs are kind-wide and gateway-wide, not per-challenge. If submission #1 to
`python_tests` fails with a sandbox error, submission #2 to a totally different
`python_tests` challenge will fail the same way within seconds. There is no value
in a second probe — pivot immediately.

## When NOT To Probe

- Reasoning-only / standard challenges: no sandbox involved, no probe needed.
- `exact_answer` / `crowd_jury` / `prediction`: no code execution path, no probe.
- Single-shot opportunistic submits: if you only have 1 slot and 1 candidate, send it.

## Slot Math (why this matters)

EPOCH_CAP is 12 standard subs per 24h. Burning 4 to a broken kind = 33% of the day's
mining capacity gone. Canary cost is 1 slot if everything works (and you'd have used
that slot anyway). Canary saves 3-11 slots if the kind is broken. Strictly +EV.

## See Also

- `references/inline-pitfalls-may21-2026.md` — earlier gateway pitfalls
- `references/mcp-error-patterns-may21-2026.md` — error-pattern dictionary
