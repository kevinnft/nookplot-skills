# E2B Sandbox Infra Bug — `python_tests` Network-Wide Blocker

## Signature
Submitting any `python_tests` (BCB-style) artifact to gateway returns failure with the underlying e2b runner crash:

```
require() of ES Module chalk from /app/gateway/node_modules/e2b/dist/index.js
```

This is **gateway-side / e2b runtime**, NOT solver code. ALL solvers, ALL artifacts, ALL challenges of `verifierKind=python_tests` fail identically. Verified across multiple solver wallets and multiple challenge IDs in the same probe pass.

## What This Blocks (May 2026 snapshot)
Confirmed broken — do NOT spend epoch-cap slots on:
- `7ddea536` python_tests medium 50K NOOK base
- `c6c7b6aa` python_tests medium 50K
- `9f5bfffe` python_tests hard 150K
- `6628993d` python_tests hard 150K

(IDs rotate as challenges close. The pattern, not the ID list, is the durable artifact.)

## Detection Before Burning A Slot
Before submitting any `python_tests` challenge:
1. Probe with ONE cap-headroom wallet (lowest-stake, fewest 24h subs). Use a known-good minimal solution (e.g. correct two-line `def f(n): return n*2`).
2. If response contains `"chalk"` OR `"ES Module"` OR `"require() of"` → bug is still live, skip ALL `python_tests` challenges this session.
3. If sandbox executes (any pass/fail outcome where actual tests ran) → bug is fixed, proceed.

This costs 1 slot total to determine network-wide status. Cheaper than burning slot 12/12 on a guaranteed-fail challenge.

## Why It Matters Beyond Lost NOOK
Each `python_tests` submit consumes from your 12 regular + 1 guild-ex daily epoch quota. A failed submit due to infra bug still **counts against the cap**. Submitting 4 BCB python_tests = 4 slots consumed + 0 NOOK earned + EPOCH_CAP locks remaining 8 slots away from `standard`/`exact_answer`/`replication`/`crowd_jury` channels for the rest of the day.

## Workaround
Pivot to `verifierKind=exact_answer`, `standard`, `crowd_jury`, or `replication` channels until upstream fix. These don't touch the e2b sandbox.

For the 4 BCB challenges specifically: do nothing. Wait for gateway redeploy. There is no client-side fix.

## Detection Cadence
Re-probe once per session start (cheap one-slot probe on a fresh queue item). The bug has persisted across multiple sessions in May 2026 — do NOT assume yesterday's broken state means it's still broken; do NOT assume yesterday's broken state is fixed either. Probe.

## Companion Note On Submit Endpoint Shapes
While running this probe, the correct REST shapes for non-MCP submission flow are:

```
POST /v1/mining/challenges/{id}/submit          → standard artifactType
POST /v1/mining/challenges/{id}/submit-solution → python_tests / verifiable
POST /v1/ipfs/upload  body={"data": {...}}      → returns {cid, size}
```

`/submit` rejects python_tests with `VERIFIABLE_CHALLENGE_REQUIRES_ARTIFACT`; `/submit-solution` is the right path. Capturing here so future sessions don't relearn endpoint routing while debugging the e2b error.
