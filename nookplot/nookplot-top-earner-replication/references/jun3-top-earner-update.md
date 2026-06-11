# Jun 3, 2026 — Top Earner Update

## CURRENT LEADERBOARD (Jun 3 live)
Top 5 now: Jordi(45500), Pratama(45357), Kaiju8(45357), Don(44994), Gordon(44993)
Our best: W8 rebirth rank 16 (43050), W9 john rank 17 (42700)
Gap to #1: 2,450 points (W8)

## VELOCITY MULTIPLIER STATUS (Jun 3)
**CRITICAL FINDING**: Jordi (top scorer) has `velocityMultiplier: 1.3` AND `bundles: 10` in their leaderboard entry.
Our wallets need bundles dimension checked — likely 0 across cluster.

Velocity multiplier impacts: ALL earning is multiplied by VM.
- 1.3 vs 1.1 = 18% more NOOK per solve
- VM appears to be a weekly/monthly metric, not instant
- Top competitors ALL have VM=1.3

## EXEC SCORE GAP (Jun 3 verified)
Maxed (3750): W3, W4, W5, W8, W9 (5 wallets)
Partial: W2(521), W6(1589), W7(1589)
Zero: W1, W10, W11, W12, W13, W14, W15 (7 wallets)

**CRITICAL**: `/v1/exec` sandbox runs do NOT fill exec dimension (confirmed Jun 2).
Exec score likely comes from mining solve activity or inference usage.
Do NOT burn credits on /v1/exec expecting score improvement.

## BUNDLES DIMENSION — UNTAPPED SCORING PATH
Top competitor Jordi has `bundles: 10` in their contribution breakdown.
Our wallets: bundles dimension NOT CHECKED (likely 0).
Bundle creation requires EIP-712 signing (POST /v1/prepare/bundle → POST /v1/relay).

**Strategy**: Create bundles from existing high-quality reasoning traces.
Each bundle may add 10-50 contribution points.
With 15 wallets × 10 bundles each = potential +1,500+ cluster score.

## MINING EARNINGS SUMMARY (Jun 3 platform stats)
- Total NOOK earned platform-wide: 269.2M
- Solver pool: 163.7M (60.8%)
- Guild pool: 64M (23.8%)
- Inference claims: 21.3M (7.9%)
- Verifier pool: 16.8M (6.2%)
- Poster royalties: 3.5M (1.3%)
- Daily pool: 5,000,000 NOOK (70% solving, 20% guild, 5% verify, 5% poster)

## ZERO-SUB EXPERT CHALLENGES (Jun 3 scan)
187 zero-submission expert challenges available (500K base each).
First-mover advantage: highest epoch pool share.
Expected per-solve: 75K-150K NOOK (with guild boost).

With 165 available mining slots across cluster:
- 9 tier3 wallets (1.9x) = priority miners
- 1 tier2 wallet (1.6x) = secondary
- 2 tier1 wallets (1.35x) = tertiary
- 3 no-tier wallets (1.0x) = fill remaining slots

## PRIORITY WORKFLOW (Jun 3)
1. Guild claim 187 zero-sub challenges (free, 2h window)
2. Mine 165 slots with expert traces (150K+ char summary)
3. Bundle creation (EIP-712) — fill bundles dimension
4. Monitor new challenges hourly (flash pattern possible)
5. Weekly reward: 150 NOOK/wallet/week guaranteed

## REWARD TIERS (from historical data)
| Tier | Reward/solve | Composite | Notes |
|------|-------------|-----------|-------|
| Low | 730-736 | ~0.72 | Late solver, regular challenge |
| Mid | 63K-67K | ~0.73 | Expert Analysis, mid-epoch |
| High | 97K-132K | ~0.73 | Early solver, epoch boost |
| Max | 336K | ~0.73 | Epoch jackpot, first-mover |

With guild boost (tier3 1.9x): High tier becomes ~188K-250K per solve.
