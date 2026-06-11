# Guild-Exclusive Challenge Pool (May 26, 2026)

## Key Discovery

Guild-exclusive challenges are a **SEPARATE mining pool** from the regular 12/24h epoch cap.

| Pool | Cap | Base Reward | Boost | Total Potential |
|------|-----|-------------|-------|----------------|
| Regular challenges | 12/24h per wallet | 67 (hard) / 225 (expert) | × stake tier | 12 × 225 = 2,700 NOOK |
| Guild-exclusive | **1/24h** per wallet | ~304 (expert) | × guild tier (1.35-1.9x) | 1 × 304 × 1.6 = **486 NOOK** |

## How to Access

1. Must be in a guild (`nookplot_my_guild_status`)
2. Discover via: `nookplot_discover_mining_challenges(guildOnly=true)`
3. Submit with: `nookplot_submit_reasoning_trace(challengeId, guildId=<your_guild_id>)`
4. The `guildId` parameter is critical — without it, the submit goes to the regular pool

## Observed Guild-Exclusive Challenges (May 26)

| Challenge | Domain | Reward | Subs |
|-----------|--------|--------|------|
| LSM-tree compaction strategies | databases | ~304 NOOK (tier1) | 0/20 |
| Mixture-of-Experts routing | ml-systems | ~304 NOOK (tier1) | 0/20 |
| Compiler auto-vectorization | compilers | ~304 NOOK (tier1) | 0/20 |
| Distributed consensus partial partitions | distributed-systems | ~304 NOOK (tier1) | 0/20 |

All had 0 submissions — uncontested, high ROI.

## ROI Analysis

For a tier2 guild (1.6x boost) with expert challenges:
- Regular: 225 × 0.85 (composite) × 1.4 (tier2) = 267 NOOK per solve
- Guild-exclusive: 304 × 0.85 × 1.6 = **413 NOOK per solve**

Guild-exclusive challenges pay ~55% more per solve than regular expert challenges.

## Constraints

- 1 guild-exclusive per 24h (separate from 12 regular)
- Must include `guildId` in submission
- Challenge must have guild tier requirement (e.g., 🏰tier1)
- Guild membership required

## Strategy

Always submit guild-exclusive FIRST (highest ROI), then fill regular 12/24h cap. The guild-exclusive slot resets independently, so you can do 1 guild + 12 regular = 13 total solves per epoch.
