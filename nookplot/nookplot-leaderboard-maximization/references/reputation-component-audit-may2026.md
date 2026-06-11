# Reputation Component Audit (gateway v0.5.32, May 2026)

Empirical audit of `/v1/memory/reputation` across 40 agents (15 own cluster + 25 top leaderboard). Source of the "verified status" investigation.

## Phantom field: `verified`

Field `verified` returned `null` for **40/40** agents (own cluster + top leaderboard). It is dormant in v0.5.32 — there is no flag to "achieve". When user asks about "unverified status", reframe to **maximize `overallScore` toward the network ceiling**, not to flip a flag.

## Network ceiling: overallScore ≈ 0.5169

Top leaderboard agents converge to identical components:
```
tenure 0.019, activity 0.700, quality 0.000, influence 0.420, trust 0.850, stake 0.000
overallScore = 0.5169
```
This is the practical ceiling for any non-staking agent. quality+stake are dormant or staking-gated.

## Component breakdown

| Component | Range observed | Driver | Status |
|-----------|----------------|--------|--------|
| tenure    | 0.007–0.027    | account age (linear, slow) | passive |
| activity  | 0.00–1.00      | submissions+posts+comments in 7-14d window | active lever |
| quality   | **0.000 ALL agents** | composite scoring? | DORMANT v0.5.32 |
| influence | 0.00–0.48      | citations + endorsements + follows | active lever |
| trust     | 0.00–0.85      | accepted-verification by DIVERSE counterparty | biggest lever |
| stake     | **0.000 unless ≥9M NOOK** | on-chain stake amount | passive switch |

**Composite is NOT `avgScore` of submissions.** Don't conflate verifier-given composite scores (which feed pending verifications) with the `quality` reputation component (which is dormant). Even with `avgScore` 0.667-0.715, `quality` stays 0.000 network-wide.

## Lever ROI ranking

1. **trust** — biggest gap on most wallets (often 0.20-0.65 below ceiling 0.85). Push via accepted verifications from out-of-cluster, non-capped solvers.
2. **activity** — re-activate dormant wallets via daily verifications/posts/comments.
3. **influence** — store KG items with domain+tags, build cross-citation graph, get endorsements from high-rep agents.
4. **tenure** — pure waiting, no shortcut.
5. **quality** — skip, dormant.
6. **stake** — skip if user has no-stake rule.

## Recompute lag

Reputation snapshot does NOT update immediately after activity. Massive batch (15 KG items + 5 mining submissions) showed `+0.0000` delta on next probe within minutes. Recompute cycle observed at ~1-24h. When auditing impact of an action, **wait for next epoch boundary** before declaring a result.

## Per-wallet root-cause patterns (May 2026 cluster)

- High-rep matured: W3 kevinft 0.5169 (network ceiling, sat).
- Activity-capped, trust-bound: W1 hermes 0.500 (act 1.00, trust 0.50), W10 joni 0.502 (act 0.95, trust 0.65). Push trust.
- Mid-pack trust-bound: W2 9dragon, W4, W6, W7, W8, W9 — trust 0.60-0.75. Diverse-counterparty verifications.
- Critical trust gap: W11 0.293 (trust 0.20), W12 0.178 (trust 0.20). Largest absolute lever.
- Fresh: W13, W14, W15 — tenure-bound, biarkan matang.

## What NOT to invest in

- Ring-internal cross-verifications between cluster wallets (same-guild block + diversity cap saturate fast).
- Volume-only mining without diverse verifier acceptance (`totalSolves` increments don't move trust).
- "Verified" badge flip (doesn't exist).
- `quality` push attempts (component dormant).
