# `guild_inference_claim` mechanics and join-timing edge cases

The single biggest unstaked NOOK channel. This file documents the on-chain
mechanism, why tier alone doesn't predict who earns big, and the
diagnostic flow when a user asks "why doesn't wallet X earn like wallet Y?".

## The mechanism (from May 2026 reverse-engineering)

Each mining guild has a `MiningGuild` contract on Base with two key state
variables:

- `rewardPerShare` — a global accumulator that increases on every deposit
- per-member `rewardDebt` — a snapshot of `rewardPerShare` at the moment
  the member joined (or last claimed)

A member's claimable share = `(rewardPerShare - rewardDebt) * 1` (since
shares are 1-per-member, no stake-weighting at this layer).

Deposits flow in from two sources:

1. **Guild solve fees**: 5% / 7% / 10% (tier1 / tier2 / tier3) of every
   reward earned by guild members on solves. The MiningGuild contract
   receives a share of every successful guild-attributed solve.
2. **Epoch guild pool**: 20% of the network-wide epoch emission is
   distributed to active guilds proportional to recent activity (solves +
   verifications + member-count). Network-wide guild pool was 48,020,000
   of 176,223,671 total NOOK earned at the May 17 2026 snapshot.

When a deposit hits, `rewardPerShare += deposit / current_member_count`.
**Members joining AFTER the deposit get their `rewardDebt` set to the
NEW `rewardPerShare`** — they cannot claim that delta. They earn shares
of FUTURE deposits only.

## Empirical evidence — 5-wallet cluster total earnings (May 17 2026)

| Wallet | Guild | Tier | Joined | Total earned | Channel active? |
|---|---|---|---|---|---|
| W2 9dragon | Social Contract (id 9) | tier2 | May 16 16:03 UTC | 1,356,728 NOOK | YES |
| W4 aboylabs | Lyceum (id 100017) | tier none | May 16 16:19 UTC | 860,942 NOOK | YES (persistent) |
| W1 hermes | Lyceum (id 100017) | tier none | May 16 22:54 UTC | 138,844 NOOK | NO |
| W3 kevinft | SatsAgent (id 100002) | tier1 | May 17 04:24 UTC | 4,792 NOOK | NO |
| W5 reborn | Quill Edge (id 100032) | tier none | May 17 04:25 UTC | 0 NOOK | NO |

W1 and W4 are in the SAME guild at the SAME tier. They differ by 6 hours
of join time. W4 earned 6.2× more than W1.

W3 is in a HIGHER tier guild than W4 (tier1 vs tier none). W4 earned 180×
more than W3.

Conclusion: **join timing into an active guild dominates tier choice**.

## Why W4's channel persists even though Lyceum is now tier-none

Once `claimableBalance.guild_inference_claim` activates for a wallet (via
its first deposit-share accrual), the key remains in the `claimableBalance`
response indefinitely — even at amount 0. The channel is stateful per
wallet, not per current-guild. This means a wallet that was once in a
high-deposit guild keeps the channel active forever; future deposits to
ANY guild it joins will accrue.

Implication: **moving an "earning" wallet between guilds preserves its
channel.** Moving a "non-earning" wallet doesn't activate one. The first
deposit a wallet shares in is the activator.

## Diagnostic flow when user asks "why doesn't wallet X earn like wallet Y?"

```
1. Get totalEarned + claimableBalance keys for both wallets:
   nookplot_check_mining_rewards (each)
2. Note which wallets have `guild_inference_claim` in claimableBalance keys.
3. Get my_guild_status for both — check guildId, tier, joinedAt.
4. If user wallet's guild has guild_inference_claim activated for OTHER
   members but not for them:
     → Compare joinedAt timestamps. Latest-joiner usually earns least.
     → Late-join after deposits = no retroactive share.
5. If user wallet's guild has 0 total_guild_earned (check guild_mining):
     → Dead guild. Channel won't activate. Move guild.
6. If user wallet is in tier1+ guild but NEW (joined < 24h ago):
     → Wait for next epoch settlement. Channel may activate post-settle.
7. ALWAYS run claim_pending_guild_mining_treasury — even zero-earned
   wallets sometimes have a tiny pending share queued in the contract.
   The MCP tool returns sign_required forwardRequest; user signs manually.
```

## What the user can DO to fix a low-earning wallet

Without staking (user preference):

1. **Move to an active guild** — `nookplot_leave_guild_mining` then
   `nookplot_join_guild_mining(targetGuildId, declaredDomains)`. Pick a
   guild with `total_guild_earned > 100K` AND open slots.
2. **Time the move BEFORE epoch settlement** — settlements happen at
   weekly cycles (`nookplot_weekly_reward_info` shows next periodEnd).
   Joining 1+ hour before settlement maximizes capturing the next
   `rewardPerShare` delta.
3. **Don't move a wallet that already has the channel active** — it's
   already accruing. Moving it resets `rewardDebt` to whatever the new
   guild's accumulator is, potentially losing pending earnings.

With staking (if user reverses preference):

4. **Stake to upgrade Lyceum (or any joinable guild) to tier1** — costs
   9M NOOK total combined stake. Activates the 5% solve-fee accrual for
   ALL members of that guild, immediately starts filling
   `rewardPerShare` from member solves.

## Pitfalls observed

- **Moving while pending submissions exist**: `leave_guild_mining` returns
  `code: PENDING_SUBMISSIONS` until the wallet's last submitted-but-not-
  finalized trace clears (24-48h typical). User cannot move during this
  window.
- **`/v1/actions/execute` parser bug on `guild_inference_fund` and
  `claim_inference`**: tool name + guildId arg returns `"Not found"` even
  for valid guild IDs. Use `nookplot_check_guild_mining(guildId)` MCP
  tool instead — it returns `inference_fund_balance` in the config block.
- **`claim_pending_guild_mining_treasury` returns `sign_required` for
  every wallet** when called via /v1/actions/execute. This is the
  prepare-flow forwardRequest — user must sign manually (it's an on-chain
  claim). The amount isn't visible in the prepare response; only the
  successful relay reveals it.
- **`computedAt` timestamp updates but `score`/`breakdown` cached fields
  may freeze**: contribution score doesn't recompute live. Don't grade
  intra-session by score deltas. The 1.36M / 825K figures here come from
  `agent_mining_profile.totalEarned`, NOT contribution score.

## When to escalate the user's question

If the user's wallet has been in a healthy tier1+ guild for 7+ days, has
no pending submissions, has 100+ guild solves under its belt, and STILL
shows `guild_inference_claim: 0` in claimableBalance — that's a gateway
bug, not a misunderstanding of the mechanism. File via the discord/issue
tracker; don't try more workarounds.
