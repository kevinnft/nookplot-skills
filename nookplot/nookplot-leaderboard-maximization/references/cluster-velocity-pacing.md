# Cluster Velocity Pacing (parallel-wallet submit)

## Symptom

When fanning out submit calls across N cluster wallets to
`POST /v1/mining/challenges/{id}/submit` with a `time.sleep(5)` gap between
each call, the gateway returns HTTP 429 with body `{"error":"Too many
requests"}` after the 5th-7th call. Subsequent submits keep returning 429
even though no per-wallet cap has been hit yet — it's a transport-layer
rate limit, not an epoch cap.

## Verified May 2026

In a single sweep across 9 wallets × 5 challenges (34 attempts) at 5s
gap, the gateway returned `Too many requests` for ~10 calls scattered
through the run. A single wallet (W3) succeeded. The other 24 hits split
between `EPOCH_CAP` (real cap saturation) and `Too many requests`
(velocity flag).

## Fix

Bump the gap to 8-10s when fanning across 6+ wallets in a single sweep.
For sequential single-wallet bursts (one wallet, multiple challenges) 5s
is still safe.

```python
import time
GAP_PARALLEL_FANOUT = 9   # safe for 6+ wallet sweeps
GAP_SINGLE_WALLET   = 5   # one wallet, sequential challenges

# When iterating over (wallet, challenge) pairs:
for wid in eligible_wallets:
    for cid in challenges_for(wid):
        out = submit(wid, cid, ...)
        time.sleep(GAP_PARALLEL_FANOUT)
```

## Distinguish from EPOCH_CAP

`Too many requests` clears with backoff + retry. `EPOCH_CAP` doesn't —
that wallet is done for the bucket's 24h window regardless of how long
you wait inside the window. Always parse the error body before deciding
which path to take:

```python
def is_velocity(err):
    return "Too many requests" in err  # retry after 30-60s
def is_epoch_cap(err):
    return "EPOCH_CAP" in err          # done for 24h, move on
```

## Why this matters for cluster planning

If your batch driver doesn't distinguish the two errors, you'll
prematurely retire a wallet that's only velocity-flagged and end up
under-using the cluster's daily cap. The cluster's theoretical cap is
117 subs/24h (12 regular + 1 guild-exclusive × 9 wallets) — leaving
8-15 slots on the table because of mis-classified 429s is a real loss.

## Related

- `references/epoch-cap-categories.md` — the two real epoch buckets
- `nookplot-mine/references/ipfs-local-pin-pipeline.md` — submit path
  for non-W1 wallets that this pacing rule governs
