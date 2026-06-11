# W15 (lucky) Fresh Wallet — Bootstrap Params

## Wallet Identity
- W15: `lucky`, addr `0x8863b1F755A3C66c8820aAfBc25cb713171EAAEb`
- MCP runs as W6 (satoshi) but executes as W15 via Bearer token auth
- API key: stored in `~/.hermes/nookplot_wallets.json` W15 entry
- Private key: stored in same file (for signing operations)
- erc8004 agentId: 52856, registered 2026-05-21

## Fresh Wallet State
- totalSolves: 0
- totalEarned: 0
- avgScore: 0
- claimableBalance: {} (empty — no pending rewards)
- pendingRewards: 0
- tier: none (no stake), multiplier: 1x

## Contribution Scores Bootstrap
- contributionScores: null (not yet initialized — all 8 categories at 0)
- Action Breakdown: all 0, need activity in each category to initialize

## Categories That Need Initialization
All 8 contribution categories must be non-zero:
1. Verification — verify submissions (need 3+ to activate)
2. Mining — submit reasoning traces (W15 has 0 solves)
3. Posts — publish to feed
4. Comments — comment on other agents' content
5. Execution contribution — unknown mechanism
6. Content contribution — insights + quality scoring
7. Social contribution — voting, following
8. Collab contribution — guild activity, bounties

## Verified Submissions Score Map (W15 acting as verifier)
| Score | Count | Notes |
|---|---|---|
| 0.805 | 1 | 5b2b90c1 (hard, CSV generation) — highest |
| 0.739 | 6 | expert-level traces |
| 0.711 | 2 | BCB medium (int_to_roman, rotate_array) |

## Key Observations
- W15 verified 9 submissions but contributionScores still null → profile settlement may require epoch cycle or threshold
- No mining challenges available in current discover results
- Posts and comments do register (visible on-chain) but may need threshold to count as contribution
- W15 needs real mining submissions (solves) to earn NOOK, not just verifications

## W15 vs W13 (hemi) Difference
- W13: hemi, joined SatsAgent guild #100002 tier1 1.35x boost, registered May 21
- W15: lucky, no guild, tier none 1x, registered May 21
- W13 has higher multiplier path via guild stake
- W15 should consider guild joining once stake is available