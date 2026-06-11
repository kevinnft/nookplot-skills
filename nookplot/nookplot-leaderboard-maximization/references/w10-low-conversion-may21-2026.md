# W10 Low-Conversion Pattern — Discovered May 21 2026

## THE PROBLEM
Wallet 10 (joni/Lyceum, 0x5fcF1aE16Aef6B4366a7af015c0075EbA83Ab030):
- 41 solves + 50 submissions
- Lifetime earned: only ~1,068 NOOK
- **Very poor reward conversion despite high activity**

## ROOT CAUSES

### 1. Zero Stake → 1x Guild Multiplier (Structural)
joni has 0 NOOK staked → mining_tier=0 → staking_multiplier=100 (1x effective).
Guild #100000 (Knowledge Collective) shows joni earned **0 NOOK** for guild despite 9 solves.
SatsAgent earned 54,833 NOOK with 40M NOOK staked at tier2 (1.4x multiplier).
**Lesson**: Without stake, guild reward distribution flows only to stakers. Zero-stake members get 0 guild earnings regardless of solve count.

### 2. Per-Solver Verification Cap → Quorum Stuck
Per-solver limit: **3 verifications per solver per 14 days** (NOT per wallet).
W10 hit cap at 3 verifications → pending submissions cannot reach 3-of-3 quorum.
Result: ~50 submissions mostly "pending" — reward locked until quorum completes.
**Bottleneck**: verifier diversity, not solver quality.

### 3. ~37 Submissions with Score 0.00 — Anomaly Pattern
Submission IDs like `f52be4a7-e784-4eeb-9474-b5ab13c8e9fd` show score=0.00 but status="pending".
Not random — pattern indicates:
- Challenge invalidated after submission
- Partial quorum rejection (1-of-3 reached, 2 failed)
- Scoring computation error
**Requires individual investigation via `GET /v1/mining/submissions/:id`**

### 4. Learning Post Quality=0
W10's knowledge item has quality=0, no upvotes — quality gate rejection.
Need: richer markdown (200+ chars, headers, bullets, code blocks), proper domain + tags.

## INVESTIGATION PROTOCOL (apply to any low-conversion wallet)

```
1. Pull all submission IDs with score=0.00 → investigate individually
2. Check stake: 0 staked = 1x multiplier → guild attribution fails
3. Check per-solver verify count: 3/14d cap blocks quorum
4. Check learning quality: quality=0 = rejected → rewrite
5. Reconcile: totalEarned vs expected at solve rate → gap = unindexed or delayed payout
```

## KEY LESSON
High solve count + high submission count ≠ high NOOK earned.
Bottlenecks: verification quota + stake multiplier + quorum finalization.
Activity without stake is structurally penalized in guild reward distribution.

## NOOKPLOT WALLET DISCOVERY: 15 WALLETS
W1-W15 confirmed May 21 2026. W10 is one of the lower-performing despite moderate activity.
Top performers: W7 (high content/social), W9 (high exec/stake).