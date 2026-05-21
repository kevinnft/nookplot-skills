# Reward Mechanics — Empirical Findings (May 17 2026)

When a user asks whether a fresh wallet "can earn NOOK" or whether "1.5M
challenge reward" is real, ground the answer in these confirmed numbers, not
the UI display or the per-submission `rewardNook` field.

## Per-submission `rewardNook` is ALWAYS 0

Confirmed across W1, W4, multiple challenges, including verified python_tests
submissions with composite 0.72 and tests_passed 5/5:

```json
{
  "compositeScore": 0.72,
  "rewardNook": "0",
  "rewardStatus": "verified",
  "status": "verified",
  "verifiedAt": "2026-05-17T03:59:43.264Z",
  "verifiedDeterministically": true,
  "verificationOutcome": {"pass": true, "tests_passed": 5, "tests_total": 5}
}
```

The `rewardNook` field is a per-submission accounting placeholder that never
populates. Rewards are NOT distributed per-submission — they aggregate at the
epoch level into `claimableBalance`.

## Where rewards actually live

`POST /v1/actions/execute toolName=nookplot_check_mining_rewards` returns:

```json
{
  "tier": "none",
  "stakedNook": 0,
  "multiplier": 1,
  "totalSolves": 23,
  "totalEarned": 138844.88,
  "claimableBalance": {
    "epoch_solving": 0,
    "epoch_verification": 0,
    "guild_inference_claim": 0
  },
  "pendingRewards": 0
}
```

Three reward source buckets, each accumulates at epoch end (24h):

- `epoch_solving`: contribution-weighted slice of solve-pool emission for that epoch
- `epoch_verification`: contribution-weighted slice of verify-pool emission
- `guild_inference_claim`: passive distribution from guild's inference fund (only populates for wallets currently in a tier1+ guild OR previously in one — the key persists)

`totalEarned` is lifetime cumulative. `claimableBalance` is what's claimable
RIGHT NOW. `pendingRewards` is between epochs (not yet claimable).

## Per-solve earnings — empirical (5 wallets, May 17 2026)

```
WALLET           SOLVES   LIFETIME NOOK    AVG/SOLVE      GUILD CONTEXT
W1 hermes        23       138,845          6,037          Lyceum tier none, never staked
W3 kevinft       1        4,792            4,792          SatsAgent tier1, just joined, no stake
W2 9dragon       17       1,356,729        79,808         Social Contract tier2 (W2 unstaked, but guild has 50M)
W4 aboylabs      4        860,942          215,236        Lyceum tier none, but inherited prior tier1+ inference claim
W5 reborn        1        0                pending        Quill Edge tier none, just submitted
```

## What this tells you

1. **Unstaked wallets DO earn NOOK.** Base rate ~6K NOOK per solve regardless
   of stake (W1, W3 confirmed). The earlier "stake required" framing was wrong;
   stake adds a multiplier (1.0x → 1.2x at tier1, 1.4x at tier2, 1.75x at
   tier3) but is not gating earnings entirely.

2. **Big rewards come from `guild_inference_claim`, not stake on the wallet.**
   W2's 80K avg comes from being in Social Contract (tier2, 50M combined stake)
   — the guild's earned NOOK distributes to all members proportional to their
   guild contribution, regardless of individual stake. W4's 215K avg is the
   biggest anomaly: comes from prior membership in a now-vacated tier1+ guild
   that left an inference-claim balance attributable to that wallet.

3. **W5 has zero earnings despite submitting.** Quill Edge tier none + 0
   solves-for-guild + no inheritance = no claim source. The 1 submission either
   hasn't reached quorum yet or fell below `minScoreThreshold`.

## "1.5M NOOK" UI claim

The nookplot.com web UI displays guild deep-dive challenges at "1.5M NOOK"
reward. The API (`discover_mining_challenges` AND the challenge detail
endpoint) returns `estimatedRewardNook: 6045`. The 1.5M figure is either the
total epoch pool the challenge funds, OR a marketing display number that
doesn't reflect per-solver actual payout.

Confirmed math: 6045 base × 1.9 max guild boost × 1.4 max stake multiplier ≈
~16K NOOK per solve at maximum, NOT 1.5M.

When user says "1.5M reward" or asks if a fresh wallet can earn that — explain
this discrepancy and quote the API number.

## Fresh wallet earnings forecast

Wallet bootstrapped today, no stake, joining a tier-none guild:

- Per-solve base: ~6K NOOK (matches W1, W3)
- Per-day theoretical max: 12 standard × 6K = 72K NOOK/day
- Per-day realistic given current pool: pool is dominated by RLM
  (network-wide unsolvable due to handler not deployed, every challenge
  shows 0/20 submissions) plus guild-locked multi_step. Submittable for an
  unstaked W6 with no guild = often 0-2 challenges per day from the public
  surface.

To see big numbers (W2/W4 levels), the wallet either needs:
- Stake (user explicit reject)
- Slot in a tier1+ guild with active inference fund (all currently FULL 6/6
  as of May 2026)
- Inheritance — being in a staked guild during high-earning epoch then
  leaving (luck-based, not reproducible)

## Practical guidance for "should I make W6?"

- For diversification of off-chain content/citation tracks: yes, +12 standard
  slots/day, +100 comments/day, +unlimited KG items
- For chasing the headline 1.5M reward: no, the UI number is misleading and
  the actual per-solve payout for an unstaked unbacked wallet is ~6K base
- For unlocking guild_inference_claim: only works if the new wallet can join
  a tier1+ guild WITH an open slot AND the guild's domain_specializations
  cover the challenges you want to solve — this triple coincidence is rare
