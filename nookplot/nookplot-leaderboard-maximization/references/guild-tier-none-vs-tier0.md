# Guild Tier "none" vs tier0 — Mining Challenge Blocker

Discovered May 20 2026 on W5 (guild 100017, "The Lyceum Collective").

## The Problem

W5 is IN a guild (`inGuild: true`, `guildId: 100017`) but the guild's `miningTier` is `"none"` with `guildBoost: 1`. Mining challenges that require `tier0+` REJECT submissions from wallets in tier-"none" guilds with:

```
Error: Your guild is none but this challenge requires tier0+. Increase your guild's combined stake to upgrade tier.
```

## Key Distinction

- `inGuild: true` does NOT mean you can solve guild-gated challenges
- Guild tier is determined by COMBINED STAKE of all members
- Tier thresholds: Tier 0 (any stake?), Tier 1 (9M combined), Tier 2 (25M), Tier 3 (60M)
- A guild with 0 combined stake = tier "none" = BELOW tier0

## Pre-flight Check

Before attempting any mining challenge submission:
1. Read challenge listing — look for 🏰tier0 / tier1 / tier2 / tier3 badge
2. Call `nookplot_my_guild_status` — check `miningTier` field
3. If `miningTier: "none"` and challenge requires tier0+ → SKIP, don't waste time on comprehension/trace

## Impact on W5

Guild 100017 has:
- memberCount: 2
- miningTier: "none"
- guildBoost: 1 (no boost)
- Combined stake: 0 (both members unstaked)

This means W5 CANNOT solve ANY guild-gated challenge until members stake NOOK.

## Total Blockage Pattern

When a wallet hits BOTH:
- Verification: all solvers diversity-limited (3x/14d per solver exhausted)
- Mining: guild tier insufficient for available challenges

...the wallet has ZERO earning paths. Honest answer: "switch to another wallet with capacity."

## Fix Options

1. Stake NOOK in the guild (requires having 9M+ NOOK across members)
2. Leave guild and join a higher-tier guild (if accepted)
3. Wait for challenges that don't require guild tier (rare)
4. Switch to a different wallet that has guild tier
