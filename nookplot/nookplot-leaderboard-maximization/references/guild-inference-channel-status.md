# Guild Inference Claim Channel — Status Audit (rev May 19 2026)

**Verdict:** ACTIVE (creator-royalty path). Earlier audit (May 18 2026) called it dormant — that was wrong. Re-verified May 19 with three independent signals.

## What flipped the verdict

### Signal 1 — `claimableBalance.guild_inference_claim` is non-zero on at least one cluster wallet
```
SatsAgent  0xd4ca38a8...  guild_inference_claim = 29,629 NOOK   (May 19 2026, live)
```
The May 18 audit said the schema only exposed `epoch_solving` + `epoch_verification`. That sample was wallets without creator status. As soon as a wallet is the creator of a tier1+ mining guild, the third key materialises with a non-zero value.

### Signal 2 — `totalEarned` decomposition for jeff (0x1916C2b8aC...) leaves 77M unaccounted unless creator-royalty is real
```
totalEarned (agent_mining_profile)              85,949,338
totalEarnedNook (check_mining_stake, solver)     8,498,290   ← direct solver income
guild #100000 total_guild_earned                74,495,367   ← guild-side ledger
sum of member earned_for_guild                   8,529,000   ← visible to members
delta (guild ledger – member-visible)           65,966,367   ← UNACCOUNTED ⇒ creator royalty
```
The 65.97M delta cannot come from `epoch_solving` (already counted in stake.totalEarnedNook). It cannot come from `epoch_verification` (jeff has 11 verifications). It cannot come from member boost shares (those are inside `member.earned_for_guild`). The only remaining channel is creator-royalty accruing to the guild creator.

### Signal 3 — SatsAgent confirms the same pattern at smaller scale
```
SatsAgent (creator of guild #100002, tier1 1.35x)
  totalEarned                       32,095,306
  solver direct (2 solves t2 1.4x)            0   ← negligible direct
  claimable.epoch_solving             862,056
  claimable.guild_inference_claim      29,629   ← live, non-zero
  ⇒ ~31M earned via creator-royalty channel
```
Two creators of two different tier-level guilds, both showing creator-royalty income. This is a network feature, not a one-off.

## Mechanism (inferred — verify before staking on it)

Each solve in a tier-N mining guild routes a fee to `MiningGuild` contract. That fee accrues against the guild's creator address, NOT split among members. The creator can claim via `nookplot_claim_mining_reward` with `sourceType="guild_inference_claim"` (key now appears in claimable balance).

Why the May 18 sample missed it:
- Probed only wallets that were members of guilds, not creators (W3 in #100002, W4 in #100017, etc.). Their claimable schema legitimately omits the key.
- `inference_fund_balance` field on `check_guild_mining.config` was misread as the creator-royalty pool. It is something else (still 0 across all guilds — possibly a deposit-driven distinct channel).

## Re-audit recipe (replaces the May 18 version)

Audit creators specifically, not arbitrary members.

```python
# 1. Identify creators in your cluster
nookplot_my_guild_status({"address": ADDR})  # returns guildId
nookplot_check_guild_mining({"guildId": GID}) # config.creator_address

# 2. For each creator address, pull profile
nookplot_agent_mining_profile({"address": creator})
# Look at claimableBalance.guild_inference_claim — present and non-zero ⇒ active

# 3. Cross-check totalEarned decomposition
# delta := totalEarned (agent_mining_profile)
#        − totalEarnedNook (check_mining_stake)
#        − sum of guild boost income visible in member rows
# delta > 0 with no other explanation ⇒ creator-royalty
```

## Cluster implications (no-stake constraint applies)

User has stated repeatedly: NO new staking. So the creator-royalty path is OBSERVATIONALLY confirmed but NOT directly exploitable without:

- Creating a guild (requires guild creation NOOK fee — verify cost before proposing)
- Staking ≥10M NOOK to that guild (tier1 minimum) to enable the royalty channel
- Recruiting members so solves accrue against the creator

What stays useful even without staking:
- Decomposition technique becomes the diagnostic for any "X earned $$$ how?" question — see `references/competitor-economics-decomposition.md`
- When user asks about other top earners, check creator status FIRST. If creator of tier1+ guild, ~80% of their income is this channel and lessons about mining technique do not transfer.
- W3 (kevinft) is already a free member of guild #100002 (SatsAgent's tier1) at 1.35x boost. SatsAgent is the creator earning the royalty; W3 receives the boost. Free position, do not leave.

## Linked memory correction

Mnemosyne entry that called this channel "DORMANT network-wide" is wrong. Updated May 19 to point at this file. Trust this file, not pre-May-19 memory paragraphs about guild_inference_claim.
