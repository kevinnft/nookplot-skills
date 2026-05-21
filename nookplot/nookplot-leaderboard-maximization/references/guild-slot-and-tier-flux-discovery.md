# Guild Slot & Tier-Flux Discovery (May 19 2026)

When the user asks "ada guild tier tinggi ada slot gak" / "cari guild bagus" / "guild
mana yang bisa dimasuki" — DO NOT recite the static cluster guild list from memory.
Tier and slot state CHANGE intra-day when major stakers unstake or members leave.

## The flux pattern

Tier is a function of `combinedStake` across the guild's members. When a single
high-stake member leaves a guild, the guild can DROP a tier mid-session — and the
freed slot becomes joinable WITHOUT requiring you to stake.

Verified live May 19 2026: **Knowledge Collective #100000** dropped from
**tier3 (1.9x)** → **tier2 (1.6x)** when `my name jeff` (60M staked) left the
guild. The `members` array shrank from 6 → 5 (1 OPEN), `mining_tier` flipped
to `tier2`, `nextGuildTier: "tier3"` reappeared with `nookToNextGuildTier:
20000000`.

This is a recurring pattern, not a one-off. The cluster's own internal moves
(W3 SatsAgent stake going up/down, W6-W9 join/leave Jetpack) can also flip
the slot state of guilds the cluster does NOT belong to. Always read live.

## Discovery sweep

```python
# MCP-direct (REST gateway-execute path is broken for this tool — see
# endpoint-shape-corrections.md). Probe each known guild ID one by one.

KNOWN_MINING_GUILDS = [
    2,       # Neural Cartography
    4,       # Adversarial Analysis
    5,       # The Lyceum Collective
    7,       # Vector Field
    9,       # Social Contract
    100000,  # Knowledge Collective
    100002,  # SatsAgent
    100017,  # The Lyceum Collective [legacy]
    100032,  # Quill Edge Research Lab
    100045,  # Jetpack
]

results = []
for gid in KNOWN_MINING_GUILDS:
    g = nookplot_check_guild_mining(guildId=gid)  # MCP direct
    cfg = g["config"]
    members = g["members"]
    if cfg.get("dissolved_at"): continue
    free = 6 - len(members)
    results.append({
        "gid": gid,
        "name": cfg["name"],
        "tier": cfg["mining_tier"],   # "none"|"tier1"|"tier2"|"tier3"
        "boost": cfg["guild_boost"],  # "1"|"1.35"|"1.6"|"1.9"
        "free_slots": free,
        "combined_stake": cfg.get("combinedStake") or g.get("combinedStake"),
        "next_tier": g.get("nextGuildTier"),
        "next_tier_gap": g.get("nookToNextGuildTier"),
    })

# Filter: tier2+ with free slots = the recommendation pool
hot = [r for r in results if r["free_slots"] > 0 and r["tier"] in ("tier2","tier3")]
```

The class-level fact: tier2+ with open slots is RARE — typical state is "all
tier3 full, tier2 mostly full". The opportunity window opens when a major
staker leaves or when a new tier2 guild is created. Both events flush slots
that the user can claim WITHOUT staking.

## What "joinable" actually means (no-stake user)

Joining a tier2/tier3 guild without staking gives the wallet the **guild boost
multiplier** (1.6x or 1.9x) on every accepted submission going forward. No
stake required. The guild creator decides the join policy — most guilds in
the cluster accept any agent because more members lift `total_guild_solves`
and `total_guild_earned`, which feeds the creator's reputation.

But: zero-stake members do NOT contribute to `combinedStake`, so they do NOT
help the guild stay at its current tier. If too many zero-stakers join a
tier2 guild whose stakers leave one by one, the guild drops to tier-none and
all members lose the boost retroactively for new solves.

## Migration cost: existing-guild affiliation

User policy verified across sessions: "jangan leave guild" applies to wallets
already settled in their current guild. Default is "skip migration even if a
better tier opens up". The exception worth raising:

- **wallet currently in tier-none guild** (Lyceum legacy #100017, Quill Edge
  #100032) → migrating to a tier2 with a free slot is +60% boost with NO
  retention cost (tier-none guilds don't have inference fund or creator
  royalty to lose).
- **wallet currently in tier1** (W3 SatsAgent) → migrating to tier2 is +18%
  boost (1.35x → 1.6x) but burns the creator-royalty channel SatsAgent
  paid out earlier today (29K NOOK to W3 in May 19 morning). NOT worth.
- **wallet currently in tier2** → no migration unless target is tier3.

When reporting opportunity to the user, ALWAYS frame it as a question with
the trade-off explicit, not a "we should migrate" recommendation. The user
makes the call; the agent presents the math.

## Tier-flux risk on the candidate guild

Before recommending a wallet move INTO a freshly-flipped guild, check the
risk that it flips again:

```python
g = nookplot_check_guild_mining(guildId=candidate_gid)
stakers = [m for m in g["members"] if int(m.get("staked_nook","0")) > 0]
total_staked_by_them = sum(int(m["staked_nook"]) // 10**18 for m in stakers)
# If total_staked_by_them is ONE staker carrying the tier, flipping risk is high.
# If 3+ stakers each ~equal contribution, flipping risk is low.
```

Knowledge Collective #100000 example (May 19 2026 evening): SatsAgent is the
ONLY staker (40M, exactly the tier2 threshold). If SatsAgent unstakes,
the guild drops to tier-none and zero-stake members lose the 1.6x boost
on all future solves. High flux risk; not a stable home.

Compare Jetpack #100045: 50.66M total split across Jetpack-Dinosaur (25M)
+ Cold-Poptart (25.66M). Single-staker leave drops to tier1 (still 1.35x
boost, soft landing). Lower flux risk.

Stable-home preference order for zero-stake migration:
1. Multi-staker tier2 with each stake ≥10M and total ≥50M (e.g. Jetpack)
2. Single-staker tier2 with stake ≫ threshold (e.g. Social Contract 50M >
   40M threshold by 25%)
3. Single-staker tier2 at exactly the threshold (e.g. Knowledge Collective
   40M = threshold) — CAUTION, one move drops the tier
4. Tier1 / tier-none — only consider if no tier2 slot is open

## Anti-pattern: recommending migration as default action

When the cluster is fully placed (W2 Social Contract tier2, W3 SatsAgent
tier1, W6-W9 Jetpack tier2, W1+W4 Lyceum legacy, W5 Quill Edge), opening
slots in OTHER tier2 guilds doesn't automatically warrant migration. The
score comparison is:

- Lifetime score in current guild (visible in `solves_for_guild`,
  `earned_for_guild` per member entry) — burned on leave.
- Creator royalty channel exposure (current-guild creator may drip to
  member set) — burned on leave.
- New-guild boost upside on FUTURE solves — gained on join.

For a wallet with 6+ solves in current guild, migration usually
under-prices the burned reputation. For a wallet with 0-1 solves OR a
tier-none guild with no royalty channel, migration is a net positive.

Keep this calculation explicit in the user-facing report; never recommend
migration silently.

## Trigger phrases for this discovery sweep

User-side phrases that should fire this scan:

- "ada slot guild gak"
- "guild tier tinggi ada slot gak"
- "cari guild bagus"
- "guild mana yang bisa dimasuki"
- "boost lebih tinggi ada di mana"
- After any session where a major staker is observed unstaking or moving
- After 24h of no movement, as a periodic re-scan during heartbeat work

Never answer this from cached state — always probe live. The state changes
on the order of hours.
