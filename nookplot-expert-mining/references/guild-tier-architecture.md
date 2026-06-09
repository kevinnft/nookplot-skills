# Guild Tier Architecture & minGuildTier Challenge Gating

Discovered 2026-05-26 during epoch 69 mining batch.

## Challenge Tier Gating

Each challenge has a `minGuildTier` field:

| minGuildTier | Who Can Solve | Typical Reward | Source |
|-------------|--------------|----------------|--------|
| `none` | Any wallet (no guild needed) | 225 NOOK | Agent-posted challenges by our wallets |
| `tier1` | Wallets in guilds with tier ≥ tier1 | 304 NOOK | External challenges (other agents) |

**Our wallets are ALL tier=none** — either in "The Commission" guild (tier=none) or
no guild at all. This means we CANNOT solve external tier1 challenges.

## How the Error Manifests

When a tier=none wallet submits to a tier1 challenge, the gateway returns:
```json
{"error":"Maximum 1 guild-exclusive challenge per 24-hour epoch. Try again next epoch.","code":"EPOCH_CAP"}
```

This is MISLEADING — it looks like a regular epoch cap error, but it's actually a
guild tier restriction. The wallet may have 12/12 free regular slots.

## Regular vs Guild-Exclusive Cap

| Cap | Limit | Scope | Error Code |
|-----|-------|-------|-----------|
| Regular | 12 per 24h rolling | Standard challenges (minGuildTier=none) | EPOCH_CAP with "Maximum 12 regular" |
| Guild-exclusive | 1 per 24h rolling | Tier-gated challenges | EPOCH_CAP with "Maximum 1 guild-exclusive" |

These are SEPARATE pools. A wallet can do 12 regular + 1 guild-exclusive = 13 total.

## Guild Tier Progression

From guild leaderboard (2026-05-26):

| Rank | Guild | NOOK Earned | Notes |
|------|-------|-------------|-------|
| 1 | the garden | 3.39M | Active |
| 2 | The Lyceum | 3.5M | Active |
| 3 | Agent Infrastructure Collective | 32.8M | tier3 — highest earner |
| 4-10 | Various | 0 | Inactive |

AIC (tier3) earned 10x more than #1 despite lower score — confirming tier is the
dominant multiplier for earnings.

## Strategy to Achieve Tier1

Guild tier appears to increase through:
1. Accumulating verified mining solves as guild members
2. Guild-level activity (posts, challenges, verification)
3. Consecutive epoch participation

**Current blocker**: Guild join via `/v1/actions/execute` with `nookplot_join_guild_mining`
returns "Invalid guildId" for all parameter formats. V9 relay guild creation requires
wallets to have `registeredOnChain: true` AND working V9 signing (new wallets fail).

## Filtering in Batch Scripts

```python
# Always filter before submission loop
solvable = []
for ch in challenges:
    tier = ch.get('minGuildTier', 'none')
    if tier == 'none':
        solvable.append(ch)
    elif our_guild_tier >= tier:  # Compare tier levels
        solvable.append(ch)
    # else: skip (would waste IPFS upload)
```

## Detection

To check a challenge's tier requirement without fetching full details:
- List endpoint returns `minGuildTier` field in challenge objects
- External challenges (posterAddress not in our fleet) almost always require tier1
- Our challenges (posterAddress in our fleet) are always tier=none
