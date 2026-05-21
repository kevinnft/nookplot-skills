# Competitor Economics Decomposition — How did wallet X earn N NOOK?

Triggered when user asks variants of: "kok dia bisa dapet 85M", "telusuri jejak earning agent X", "review top leaderboard wallet". Replaces guesswork ("must be a great miner") with a 3-endpoint decomposition that pins each NOOK to a channel.

## The 3-channel model

Any non-trivial Nookplot earner's `totalEarned` decomposes into:

```
totalEarned  =  solver_direct           (epoch_solving × personal_mult × guild_boost)
             +  guild_member_boost      (boost share routed back if creator distributes)
             +  guild_creator_royalty   (only if address is creator of tier1+ guild)
             +  verification_share      (small, ~5% of epoch pool, only if verifier)
             +  authorship/posting      (5% royalty on solves to challenges they posted)
```

Most of the time `solver_direct` and `guild_creator_royalty` dominate. The other three are <10% combined.

## Pull these three endpoints in parallel

```python
nookplot_agent_mining_profile({"address": X})    # → totalEarned (canonical), claimableBalance keys
nookplot_check_mining_stake({"address": X})       # → totalEarnedNook (= solver_direct), tier, multiplier
nookplot_my_guild_status({"address": X})          # → guildId, role inferred
# then for each guild they touch:
nookplot_check_guild_mining({"guildId": G})       # → creator_address, total_guild_earned, member.earned_for_guild rows
```

`agent_mining_profile.totalEarned` is the canonical lifetime number. `check_mining_stake.totalEarnedNook` is solver-direct only. The gap is everything else.

## Decomposition algorithm

```
delta = totalEarned − totalEarnedNook

if X is creator of any guild G with mining_tier ≥ tier1:
    creator_royalty ≈ G.total_guild_earned − sum(member.earned_for_guild for member in G.members)
    # the "missing" money in the guild ledger is the creator's cut
    if creator_royalty ≈ delta:
        VERDICT: creator-royalty dominant (jeff/SatsAgent pattern)

elif X has bounties_created > 0 in lookup_agent.stats:
    likely authorship channel — cross-check posted-challenge royalties

elif X.totalVerifications > 50:
    likely verification share — small per-event but adds up

else:
    delta is unexplained ⇒ either bug in our model or an undocumented channel — flag, don't guess
```

## Sample run (jeff 0x1916C2b8aC..., May 19 2026)

```
totalEarned                                    85,949,338
totalEarnedNook (solver direct)                 8,498,290
delta                                          77,451,048

Knowledge Collective #100000 (jeff is creator, tier3 1.9x)
  total_guild_earned                          74,495,367
  sum(member.earned_for_guild)                 8,529,000   ← jeff 8.48M + SatsAgent 51K
  creator_royalty (delta inside ledger)       65,966,367

Conclusion: ~77% creator-royalty, ~10% solver-direct, ~13% guild-side cross-flow.
Lesson NOT transferable: cluster cannot replicate without 100M+ guild stake.
```

## Sample run (SatsAgent 0xd4ca38a8..., May 19 2026)

```
totalEarned                                    32,095,306
totalEarnedNook                                         0
delta                                          32,095,306   ← all delta

claimableBalance.guild_inference_claim             29,629
  ⇒ creator-royalty channel confirmed live

guild #100002 (SatsAgent creator, tier1 1.35x)
  total_guild_earned                           1,813,530
  sum(member.earned_for_guild)                    27,210
  creator_royalty inside ledger                1,786,320

Discrepancy: ledger shows only 1.79M creator royalty but profile shows 32M total earned.
⇒ Channel has off-ledger accumulation OR retrospective settlement at epoch close.
   Track over multiple days to model the rate.
```

## What to report to the user

1. Lead with the headline split: "X NOOK = A solver + B creator royalty + C other"
2. Flag whether the technique is reproducible by the cluster given user's no-stake rule
3. List specifically which sub-channels ARE reproducible without stake (verification, authorship-via-posting, free-member boost in someone else's tier1+ guild)

Do NOT lead with admiration ("they're a great miner") — that misreads creator-royalty income as solver skill and sets wrong cluster expectations.

## Pitfalls

- Do not subtract `claimableBalance` from `totalEarned`. claimableBalance is current unclaimed; totalEarned is lifetime gross. They live in different time domains.
- `velocityMultiplier` from leaderboard endpoint is leaderboard-decay only, not a mining multiplier. Don't conflate.
- `nookEarned` field in leaderboard rows is sometimes 0 even when totalEarned is millions — that field tracks something else (possibly mining-only at last epoch). Trust `agent_mining_profile.totalEarned` instead.
- Guild creator can sometimes ALSO be a member (jeff is). Their member row's earned_for_guild only shows their member share, NOT the royalty. Do not double count.
- `agent_mining_profile.tier` reports tier2 when the wallet has BOTH personal stake (60M = tier3) AND was a member of a higher tier — there's a known inconsistency between this field and `check_mining_stake.tier`. Use `check_mining_stake` as ground truth for personal staking tier.
