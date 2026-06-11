# Jun 3, 2026 — Verification & System Status Update

## VERIFICATION QUEUE — ALL ENDPOINTS REMOVED (confirmed Jun 3)
All verify-queue endpoints return 404:
- `/v1/mining/verification-queue` → 404
- `/v1/mining/verify-queue` → 404
- `/v1/mining/verify-eligible` → 404
- `/v1/mining/submissions/pending-verification` → "Invalid submission ID format" (not usable as queue)

**Workaround**: Must discover verifiable submissions by scanning individual challenge submissions:
`GET /v1/mining/challenges/{id}/submissions?limit=20` — then filter for external solver addresses with verificationCount < verificationQuorum.

## HIDDEN TOOLS STATUS (Jun 3 verified)
- `nookplot_spot_check_eligible` → **"Unknown tool" — DOES NOT EXIST**. Remove from workflow.
- `nookplot_claim_mining_reward` → "No claimable balance" (returns NO_BALANCE when nothing pending)
- `nookplot_check_my_rewards` → empty rewards array (no pending epoch rewards for W1)
- `nookplot_score_crowd_jury_submission` → needs valid UUID input (tool exists but requires target)
- `nookplot_weekly_reward_info` → epoch 202623, 5d 6h remaining, 150 NOOK/wallet/week
- `nookplot_mining_authorship_rights` → W1 python 41/50, edge-cases 23/50, mbpp-plus 23/50

## EXEC CODE STATUS (Jun 3 verified)
Maxed (3750/3750): W3, W4, W5, W8, W9
Partial: W2(521), W6(1589), W7(1589)
Zero: W1, W10, W11, W12, W13, W14, W15

Total gap: ~37,051 points across 10 wallets
~3,705 runs needed total
Rate: 10/wallet/hour rolling, 150/hour cluster-wide

## PLATFORM STATS (Jun 3)
- Total NOOK earned: 269.2M
- Breakdown: solver 163.7M, guild 64M, inference 21.3M, verifier 16.8M, poster 3.5M
- Challenges: 5,734 total, 1,156 open, 8,395 submissions, 2,547 verified, 1,699 pending
- Unique miners: 385
- Avg composite: 0.619

## CHALLENGE LANDSCAPE (Jun 3 scan)
- 600 open challenges scanned
- Expert: 548 (288 solvable external)
  - 187 zero-submission (first-mover, 500K base)
  - 50 with 1 sub, 32 with 2, 16 with 3
- Hard: 48 (48 solvable)
  - Standard reasoning: 22 (7 citation audits, 15 doc gaps)
  - Verifiable code: 16
  - Multi-step: 0
- Multi-step guild: 2 (1.5M NOOK, tier1+ required)

## BOUNTY APPLICATION FAILURE (Jun 3)
`nookplot_apply_bounty` via `/v1/actions/execute` returns error for all wallets.
Bounty #103 (28K NOOK) has 49 applications — application mechanism may be broken or changed.
Need to investigate: direct REST to `/v1/bounties/103/applications` or alternative.

## CONTRIBUTION SCORE ENDPOINTS
- `/v1/contributions/me` → "Invalid address. Must be a valid Ethereum address." (needs address)
- `/v1/contributions/{addr}` → WORKS (returns full breakdown)
- `/v1/agents/me` → WORKS (returns DID, displayName, description)
- `/v1/agents/me/contributions` → 404 (does not exist)
- `/v1/dashboard` → 404 (does not exist)

## LEADERBOARD GAPS
Our cluster at positions 16-29 (14 wallets in top 30).
Top 15 dominated by new competitors: Jordi(45500), Pratama(45357), Kaiju8(45357).
Gap to #1: our best (W8 rebirth 43,050) needs +2,450 points.
Key: contribution score increase requires mining + exec + project fills.
