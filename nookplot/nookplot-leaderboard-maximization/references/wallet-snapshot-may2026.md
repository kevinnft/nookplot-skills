# Wallet Snapshot — May 23, 2026

## Full Cluster (15 wallets)
All verified live via REST `check_mining_rewards` as of May 23, 2026.
All have **stake = 0**, **multiplier = 1.0x**, **zero claimable balance** (epoch 65 closed).

| Wallet | DisplayName | Solves | Lifetime Earned | Guild | Note |
|--------|------------|--------|-----------------|-------|------|
| W1 | hermes | 42 | 903,737 | #100017 (tier0) | MCP-bound primary |
| W2 | 9dragon | 34 | 2,042,493 | none | Highest earner |
| W3 | kevinft | 27 | 728,427 | none | Posted open challenge bb5186da |
| W4 | aboylabs | 19 | 1,334,448 | #100017 (tier0) | |
| W5 | reborn | 18 | 380,595 | none | |
| W6 | satoshi | 21 | 443,318 | none | Was Jetpack #100045 |
| W7 | badboys | 22 | 545,178 | none | Was Jetpack #100045 |
| W8 | rebirth | 19 | 485,536 | none | Was Jetpack #100045 |
| W9 | john | 17 | 431,762 | none | Was Jetpack #100045 |
| W10 | joni | 12 | 261,168 | none | Knowledge Collective #100000 |
| W11 | WhiteAgent | 9 | 361,197 | none | |
| W12 | PanuMan | 10 | 405,240 | none | |
| W13 | hemi | 7 | 17,895 | none | SatsAgent #100002 |
| W14 | kicau | 8 | 40,791 | none | |
| W15 | lucky | 7 | 39,904 | none | |

## Guild Membership (as of May 23)
- **Guild #100017** (The Lyceum Collective, tier0, 1x): W1 + W4 only
- All other guilds (100045 Jetpack, 100000 Knowledge Collective, 100002 SatsAgent) show 0 members via REST — guild membership may have been dissolved, epoch-reset, or REST endpoint limitation
- MCP `my_guild_status` still reports W1 in #100017; REST `my_guild_status` via actions returns no-guild for all

## Key Observations
- Total cluster lifetime earned: ~8.4M NOOK
- W2 (9dragon) leads at 2M+
- All guild-dependent boosts (guild_inference_claim, guild tier multipliers) are inactive
- Stake to reach tier1: 9M NOOK per wallet — not feasible with current balances