# Cluster Preflight for Multi-Wallet Verification Burst

## When to use
Before starting a multi-wallet verification burst (≥3 wallets, sequential or parallel), run the preflight to avoid hitting limits mid-burst.

## The Problem
During a multi-wallet verification burst, the agent may hit MCP timeout or verification limits on wallet A, then switch to wallet B and discover wallet B also can't verify — because the agent is sharing the same MCP server session across all wallets.

More critically: each wallet has DIFFERENT verification state (per-solver limit counters, comprehension cache state). What blocks wallet A may also block wallet B if they share the same underlying verification history.

## Preflight Checklist

### 1. Per-wallet solver-block inventory
For each wallet in the burst, check which solvers are at limit:

```
For each wallet W:
  - Call discover_verifiable_submissions(limit=50)
  - Collect solverAddress from each result
  - Track: count of submissions per solver
  - Blocked: any solver with ≥3 recent verifications from this wallet
```

### 2. Comprehension state per submission
Before verifying, confirm each submission's comprehension state:
- Did this wallet already pass comprehension for this submission?
- If MCP timed out mid-flow, comprehension state may be desynchronized

### 3. Guild cross-verification matrix
Confirm guild memberships — same-guild verification is blocked.

## Cluster Cross-Guild Verification Matrix (May 2026)
```
W1: Lyceum Collective (#5, tier3)
W2: Social Contract (#9, tier2)
W3: SatsAgent (#100002, tier1) — kevinft member
W4: [unknown]
W5: Quill Edge (#100032, tier-none)
W6-W9: Jetpack (#100045, tier2)
```

Rule: W6-W9 CAN verify W1, W2, W3, W5 submissions. Cannot verify each other (same guild Jetpack).

## MCP Timeout Recovery During Burst
If MCP times out on wallet A during burst:
1. Switch to REST API for wallet A's pending verifications
2. After 45s, test MCP recovery with a light call (check_balance)
3. If still down, continue with REST for remaining wallets
4. Track pending comprehension states — resync when MCP recovers

## Session Log
- **May 21 2026:** W8 audit — MCP timeout hit after 8 verification calls in single turn. Recovered after 45s with REST fallback. Comprehension state preserved, just needed resync via another request_comprehension call.