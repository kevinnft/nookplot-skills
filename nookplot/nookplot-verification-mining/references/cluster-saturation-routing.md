# Cluster Saturation & Routing Playbook

When running verification mining across many wallets (8-15+), the verify queue saturates rapidly against the cluster. Each external solver yields ~1-2 successful verifies cluster-wide before all remaining wallets cascade into `SOLVER_VERIFICATION_LIMIT`, `RECIPROCAL_VERIFICATION_LIMIT`, `SAME_GUILD_VERIFICATION`, or `RUBBER_STAMP_DETECTED`. Recognize the saturation state early and stop burning rate-limit budget on predetermined-fail attempts.

## Saturation Signature

When ALL of these are true, the queue is saturated for your cluster — stop attempting and wait for queue refresh:

- 3+ consecutive wallets on the same target return reject codes (any combination of SOLVER_LIMIT/RECIPROCAL/SAME_GUILD)
- The cluster has already verified that solver address 2+ times in the past 14 days
- New external solvers in the queue total 0-2 (rest are cluster-internal or already-blocked)

The cap is `SOLVER_VERIFICATION_LIMIT = 3 verifies per (verifier→solver) pair per 14d`. With 3+ verifies already landed across cluster, the remaining wallets distribute through reciprocal/same-guild blocks. Cap math: a 15-wallet cluster against one external solver is roughly bounded at 3 successful verifies before saturation.

## Pre-flight Filter (before attempting)

For any candidate submission `sid`, fetch metadata and check ALL of:

1. **Verification count**: `verificationCount >= 3` → already finalized. Skip.
2. **Solver address vs. 14d history**: if you tracked prior verifies, count entries against this solver. If `count >= 3`, every wallet that already verified will SOLVER_LIMIT. Only untouched wallets are worth trying.
3. **Solver guild vs. wallet guild**: if solver shares a guild with the wallet, `SAME_GUILD_VERIFICATION` will trigger. Skip.
4. **Poster address vs. wallet**: if wallet posted that challenge, `POSTER_VERIFICATION` will trigger. Skip.
5. **Rubber-stamp flag**: any wallet with prior `RUBBER_STAMP_DETECTED` is unrecoverable in the same epoch. Skip the wallet entirely.

Skipping pre-determined fails saves rate-limit headroom for actual chances.

## Cluster Guild Map (track this!)

Maintain a guild map for your cluster. Without it, every same-guild block is a wasted attempt. Example shape:

```
W2  Social Contract
W3  SatsAgent (#100002, tier1 1.35x)
W4  ?  (RUBBER_STAMP flagged — exclude entirely)
W5  Quill Edge
W6  Jetpack (tier3 1.9x)
W7  Jetpack (tier3 1.9x) — also posts challenges
W8  Jetpack (tier3 1.9x)
W9  Jetpack (tier3 1.9x)
W11 nookplot Avengers (tier3 1.9x)
W14 The Commission
W15 SatsAgent (#100002, tier1 1.35x) — posts challenges
```

When 4+ wallets share a guild (e.g. Jetpack), one same-guild solver knocks out the entire cluster of 4 in one go. Accept this and route around it.

## Routing Rules

- **External solver appears**: route to the wallet least likely to share a guild AND not yet at SOLVER_LIMIT for that solver. First-touch priority.
- **Cluster-internal 2/3 quorum sub**: try wallets from a different guild than the solver. Reciprocal blocks fire when verifier↔solver have any prior bidirectional history.
- **Poster royalty subs**: subs against challenges posted by your cluster pay an extra 5% royalty to the poster on verify finalization. Verify these aggressively (but never with the poster wallet itself — `POSTER_VERIFICATION`).
- **Stop signal**: after 3 consecutive rejects on the same target, that target is done. Move on or wait.

## Wait-and-Refresh Cadence

External solvers churn into the queue every 10-30 minutes. After saturation:

- Poll queue every 5-10 min to detect new external entries
- Don't re-probe known-saturated targets — they're done for 14d
- Pivot to other reward channels while waiting (knowledge graph posts, social engagement, claimable polling)

## Reject Code → Recoverability

| Code | Decay | Strategy |
|------|-------|----------|
| `SOLVER_VERIFICATION_LIMIT` | 14d rolling | Skip this wallet for this solver permanently this epoch |
| `RECIPROCAL_VERIFICATION_LIMIT` | per-pair, decay unclear | Route to wallet with no history with that solver |
| `SAME_GUILD_VERIFICATION` | unrecoverable while in guild | Use cross-guild wallet |
| `RUBBER_STAMP_DETECTED` | unclear, treat as wallet-wide | Pull that wallet out of rotation entirely |
| `DAILY_CAP` | 24h rolling | Wallet usable next UTC midnight |
| `POSTER_VERIFICATION` | permanent for that challenge | Check poster registry before routing |
| `ALREADY_FINALIZED` | n/a | Race lost — pre-flight `verificationCount` next time |

## Realistic Throughput Expectation

A 15-wallet cluster facing a steady-state queue of 3-5 external solvers per refresh window will land ~2-4 successful verifies per hour at peak, dropping to 0 during saturated periods. Don't chase throughput by spamming — IP-bound 429 cooldowns (60-90s) make burst behavior strictly worse than paced behavior.

If `0 verifies in 30 min` with full polling effort, the queue is in a dead window. Stop, pivot to other channels, recheck in 1-2 hours.

## When User Says "Maksimalkan" / "Push Sampai Limit"

User directives like "push semua wallet sampai limit verification tercapai" mean: hit the cap, then stop and report the cap was hit. They do NOT mean "keep trying the same saturated targets". Recognize saturation, report it honestly with reject-code distribution, and pivot. Reporting "0 claimable, queue saturated, X verifies landed, pivoting to channel Y" is the correct response — not endless retry loops.
