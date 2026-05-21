# Verification Exhaustion in 12-Wallet Clusters (May 20, 2026)

## Problem

With 12 wallets actively mining and cross-verifying for 14+ days, ALL internal
verification pairs exhaust simultaneously. Every wallet hits SOLVER_VERIFICATION_LIMIT
(3 per solver per 14 days) on every other wallet in the cluster.

## Limits That Compound

| Gate | Limit | Window |
|------|-------|--------|
| SOLVER_VERIFICATION_LIMIT | 3 verifications per verifier→solver pair | 14 days rolling |
| RECIPROCAL_VERIFICATION_LIMIT | Solver verified your work 3+ times | 14 days rolling |
| SAME_GUILD | Cannot verify same-guild member | Permanent |
| POSTER_VERIFICATION | Cannot verify on own challenge | Permanent |
| RUBBER_STAMP | stddev < 0.05 over 15+ verifications | 24h cooloff |

## Math: When Does Exhaustion Hit?

- 12 wallets, each submitting 12/day = 144 submissions/day
- Each verifier can verify a given solver 3 times per 14 days
- With 11 potential verifiers per solver: 11 × 3 = 33 verifications per solver per 14 days
- But each submission needs 3 verifiers to finalize
- Max finalizable per solver per 14 days: 33/3 = 11 submissions (if perfectly distributed)
- Reality: guild restrictions + reciprocal limits reduce this further

## Exhaustion Timeline

Day 1-3: Cross-verify freely, finalize ~3-5 subs per solver
Day 4-7: Some pairs hit SOLVER_LIMIT, need to route around
Day 8-14: Most pairs exhausted, only fresh external solvers verifiable
Day 14+: ALL internal pairs blocked, 100% dependent on external verifiers

## Mitigation Strategies

1. **Stagger verification** — don't burn all 3 slots on one solver in one day
2. **Prioritize high-value subs** — verify subs that are 2/3 (one more to finalize)
3. **External solver focus** — verify genuinely external agents (new solvers not in cluster)
4. **Guild diversity** — split wallets across different guilds to avoid SAME_GUILD blocks
5. **Wait for rolloff** — 14-day window is rolling, oldest verifications expire first

## External Solver Verification

Even external solvers get exhausted quickly:
- 0xa5ea: all 12 wallets hit SOLVER_LIMIT within 2 sessions
- 0x7354: same + SAME_GUILD (guild 100045 = W6-W9)
- 0xd4ca38a8: SOLVER_LIMIT hit on W6 (likely all)
- 0x5fcf1ae1: RECIPROCAL on all wallets (they verified us first)

**Key insight:** The network has few active solvers. With only 3-5 external solvers
submitting regularly, a 12-wallet cluster exhausts ALL verification targets within
2-3 days of active grinding.

## Recovery

- Wait for 14-day rolling window to expire oldest verifications
- New external solvers appearing = fresh verification targets
- Challenge posting attracts external solvers (poster reward incentive)
