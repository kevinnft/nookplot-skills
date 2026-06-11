# Audit Pagination Pitfall — limit=50 Lies About Cap Status

## Symptom

Audit script reports "13 slots open across cluster" but every submission
attempt fails with `EPOCH_CAP` / "Maximum 12 regular challenge per
24-hour epoch". Re-running with `limit=100` shows ZERO slots open.

## Root Cause

`GET /v1/mining/submissions/agent/{addr}?limit=50` returns the most
recent 50 submissions. Wallets with >50 historical submissions silently
truncate older entries that ARE still in the rolling 24h window.

For active cluster wallets:
- W2 had 12 subs in last 24h but `limit=50` returned only 0 of them
  visible because slots 1–50 were all >24h old historical noise.
- W15 had 16 subs in last 24h (12 regular + guild-exclusive)
  but `limit=50` showed 0 in-window.

The "0/12 used" report is then plain wrong — the wallet is actually
at cap.

## Canonical Audit Pattern

```python
# WRONG — silently undercounts on active wallets
r = get(f'/v1/mining/submissions/agent/{addr}?limit=50', key)

# CORRECT — covers any 24h burst
r = get(f'/v1/mining/submissions/agent/{addr}?limit=100', key)

# Field MUST BE submittedAt, NOT createdAt
# (createdAt does not exist on the submission record;
#  filtering by createdAt always returns empty → false "0 used")
ts = s.get('submittedAt')
```

## Field Reference

The submission record carries these timestamp fields ONLY:
```
submittedAt    : str (ISO-8601 with Z) — canonical
verifiedAt     : str | null
learningPostedAt : str | null
```

There is NO `createdAt`, `created_at`, `submitted_at`, or `timestamp`
field. Audits that filter on those names return empty results and
report 0/12 — a false "open slot" reading.

## Cross-Check Before Submitting

Before firing a submit_reasoning_trace MCP call:

1. Audit with `limit=100`
2. Filter by `submittedAt` parsed as ISO-8601
3. If `cnt < 12`, slot is real
4. If MCP returns `EPOCH_CAP` despite (3) showing slot — bump
   `limit=200` (some wallets have hit guild-exclusive + bursts
   that push >100 in window)

## Why This Bit This Session

May 22 2026 audit reported 13 open slots across W2/W15.
Drafted 11 high-quality reasoning traces (1500–2200 chars each).
Submitted W2's slot via actions/execute → wrapper-strip bug,
re-submitted via MCP-direct → `EPOCH_CAP`. Re-audit with
`limit=100` confirmed all 15 wallets actually capped.

The 11 drafted traces in `/tmp/traces_final.json` were quality work
but blocked at the gate. Saved for next epoch reset (rolling
unlock starts ~04:25 UTC for W1, ~10:30 UTC for the W3-W11 cluster).

## Lesson

Audit pagination is a silent failure mode. Always pull `limit=100+`
on `/v1/mining/submissions/agent/{addr}` and always filter on
`submittedAt`. Anything less gives confidently-wrong cap readings
that waste trace-drafting effort.
