# Verify-Queue Full Saturation Pattern

When a single wallet has been heavy-verifying for several sessions, you can
hit a state where the visible verify queue contains N solvers but **zero**
of them are eligible because every one is already on this wallet's
exhausted list (3+/14d same-direction or reciprocal). This is structurally
distinct from a transient rate-limit and has a different ETA shape.

## Diagnostic — how to recognize it

Symptoms in one session:

- `discover_verifiable_submissions(limit=50)` returns 15–20 rows.
- After filtering against the wallet's cumulative exhausted-solver set,
  the resulting "eligible" subset is **0**.
- `request_comprehension_challenge` on any of the visible rows returns
  3+/14d or reciprocal block.

Confirmation probe:

```python
solvers_in_queue = {addr for _,addr,_ in rows}
new = solvers_in_queue - exhausted_cumulative
print(f"queue: {len(solvers_in_queue)}, new: {len(new)}")
# new == 0  ==> saturation ceiling reached
```

## Why it happens — math

Verify cap is 3 per solver-address per rolling 14-day window. The active
solver pool is roughly 20–30 unique addresses submitting regularly. After
~3 heavy verify sessions on a single wallet, you accumulate ~20+ exhausted
addresses. Once the exhausted set ⊇ active queue rotation, the eligible
subset clamps at 0 until the oldest 14d entries roll off.

Empirical W11 cluster (May 2026) — 5 sessions of heavy verifying produced
~25 unique exhausted addresses, which is wider than the typical visible
queue rotation, hence the queue can look "full" while being entirely
ineligible.

## ETA — when does it unblock

Two regenerators:

1. **Oldest 3+/14d roll-off**: 14 days from the first verify against that
   solver. If you started verifying solver X on day 0, slot 1 frees on
   day 14. This is the slow regenerator.

2. **Fresh solver entry**: a new wallet starts submitting and shows up in
   the queue. They're not on the exhausted list yet, so the next 1–3
   verifies against them are free. This regenerates faster but is
   bursty and unpredictable.

Typical recovery cadence:

- Same-day re-poll: ~0% chance of new eligibles unless a fresh solver
  just submitted.
- 6–12h re-poll: ~30% chance — usually 1–2 fresh solvers.
- 24h re-poll: ~70% chance — solver pool rotated enough.
- 14d full reset: 100% — earliest verifies roll off.

## Right thing to do when saturated

This is a **wait-state**, not a fix-something state. Three correct moves:

1. **Pivot to non-verify channels** that are still open: KG store
   (subject to its own 5min cooldown), citations, comments, insights.
   See `non-mining-reward-channels.md`.
2. **Schedule a low-frequency poll** — every 4–6h is enough; faster
   wastes API calls and hits rate limits without finding new targets.
3. **Do NOT** keep retrying comprehension on already-exhausted solvers.
   That just burns rate-limit budget on guaranteed-block calls.

## What NOT to do

- Don't reset the exhausted-solver list and try the queue fresh — the
  3+/14d cap is server-side, you'll just collect the same 9 failures.
- Don't switch the wallet's API key to retry same solvers — the cap is
  per-wallet-address, not per-key.
- Don't downgrade scoring quality to "force through" — the gate is
  comprehension-stage, before scoring even fires.

## Cumulative exhausted-solver tracking — practical

Keep this list in session memory **across** sessions for a wallet, not
just within one session. The 14d window means a Tuesday block is still
in force the following Monday. A small JSON sidecar per wallet works
fine:

```json
{
  "wallet": "W11",
  "address": "0xcdDb0f53E5E1203621676539334735a670390BDe",
  "exhausted": {
    "0x5fcf…b030": "2026-05-15T...",
    "0xa5ea…bb6d": "2026-05-18T...",
    "...": "..."
  }
}
```

When building the filter set in code, parse the timestamps and drop
entries older than 14 days — they've rolled off and are eligible again.

## Companion to "sudah maksimal" reporting

When this saturation hits and the user asks "verify queue masih ada?" or
"kenapa tidak verify?", the right reply shape is:

- queue rows: 17, eligible after filter: 0
- saturation cause: cumulative 3+/14d cap across active solver pool
- ETA: oldest entries roll off DD-MM-YYYY (14d from first verify)
- pivot: KG/citations/comments still open

That answers the question with fresh numbers + concrete ETA, matching
the user's standing reporting preference.
