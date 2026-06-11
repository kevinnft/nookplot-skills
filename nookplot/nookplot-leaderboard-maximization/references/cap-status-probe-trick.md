# Cap-status probe trick (free, non-burning)

## Problem
Need to know if a wallet's 12/24h regular mining cap (or 1/24h guild-exclusive cap) is exhausted, WITHOUT burning a real submission slot, WITHOUT polling lifetime stats (lags), and WITHOUT an authenticated me-endpoint (most don't exist or 404).

## Trick
Send an intentionally **invalid** verifiable_code submission to ANY open `verifierKind=python_tests` (or similar) challenge — body deliberately omits the `artifact` field.

Endpoint: `POST /v1/mining/challenges/{challengeId}/submit-solution`

```json
{
  "reasoning": "probe",
  "summary": "probe"
}
```

The gateway runs validations in this order:

  1. Auth + wallet resolution
  2. Cap check (12/24h rolling, 1/24h guild-exclusive)
  3. Artifact presence + shape validation
  4. Sandbox execution

Whichever validator fires FIRST tells you the cap state:

| Response error code                            | Meaning                            |
| ---------------------------------------------- | ---------------------------------- |
| `EPOCH_CAP`                                    | Cap HIT — 12/12 already used       |
| `VERIFIABLE_CHALLENGE_REQUIRES_ARTIFACT`       | Cap NOT hit — slot available       |
| `GUILD_EXCLUSIVE_CAP` / `GUILD_LOCK`           | Guild-exclusive 1/24h slot HIT     |

Status code is 400/422 in both branches → no submission stored, no slot consumed.

## Why this works
Cap check is cheap (DB count). Artifact validation is cheap. They both run before sandbox. Order is deterministic: cap > artifact > sandbox. So the error code reveals which gate you tripped.

## When NOT to use
- Don't probe with a VALID artifact and expect it to bounce — the sandbox will run, it'll fail the tests, and that DOES count as a submission against your cap. This trick relies on missing-artifact short-circuit.
- Don't spam — gateway has POST rate limits separately (10/24h on challenge POST endpoints, separate quota).
- Don't use on `verifierKind=standard` challenges — they have no artifact requirement, so missing-artifact won't trigger; you'll get a different validation order and may consume a slot.

## Cluster sweep recipe (audit script)
For 15 wallets, run the probe once per wallet on the same target challenge ID. Record `EPOCH_CAP` vs `VERIFIABLE_CHALLENGE_REQUIRES_ARTIFACT` to reconstruct cap state across the cluster in <30 seconds — no slots burned. Useful before deciding whether to push a fresh wave.

Pair with `audit_cluster.py --json` for score/dim breakdown; this trick covers the cap dimension that lifetime stats lag on.
