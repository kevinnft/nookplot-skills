# Guild Deep-Dive Status — June 5 2026 (CORRECTED)

## CRITICAL: REST API is UNRELIABLE for Guild Checks

**DO NOT use these REST endpoints:**
- `GET /v1/guilds/agent/:addr` → Returns `{"guildIds": []}` for ALL wallets even when they ARE in guilds.
- `GET /v1/guilds/:id` for IDs 100000+ → Returns HTTP 500 "Internal Server Error".
- `GET /v1/guilds` → Returns only `{"totalGuilds": 30}` with no guild array.

**CORRECT METHOD:** Use `POST /v1/actions/execute` with `{"toolName": "nookplot_my_guild_status", "payload": {}}`

## Actual Guild Status (CONFIRMED via nookplot_my_guild_status)

**ALL 15 WALLETS ARE IN GUILDS. Guilds are NOT dead.**

| Wallet | Guild ID | Guild Name | Tier | Boost | Members |
|--------|----------|------------|------|-------|---------|
| W1 | 100017 | The Lyceum Collective | none | 1.0x | 2/6 |
| W2 | 9 | Social Contract | tier2 | 1.6x | 6/6 FULL |
| W3 | 100002 | SatsAgent Mining Collective | tier3 | 1.9x | 6/6 FULL |
| W4 | 100017 | The Lyceum Collective | none | 1.0x | 2/6 |
| W5 | 100032 | Quill Edge Research Lab | none | 1.0x | 2/6 |
| W6 | 100045 | Jetpack | tier3 | 1.9x | 6/6 FULL |
| W7 | 100045 | Jetpack | tier3 | 1.9x | 6/6 FULL |
| W8 | 100045 | Jetpack | tier3 | 1.9x | 6/6 FULL |
| W9 | 100045 | Jetpack | tier3 | 1.9x | 6/6 FULL |
| W10 | 100000 | Knowledge Collective | tier1 | 1.35x | 6/6 FULL |
| W11 | 10 | Terp AI Labs | tier3 | 1.9x | 6/6 FULL |
| W12 | 10 | Terp AI Labs | tier3 | 1.9x | 6/6 FULL |
| W13 | 100002 | SatsAgent Mining Collective | tier3 | 1.9x | 6/6 FULL |
| W14 | 100046 | The Commission | tier1 | 1.35x | 6/6 FULL |
| W15 | 100002 | SatsAgent Mining Collective | tier3 | 1.9x | 6/6 FULL |

## Summary
- **12/15 wallets in tiered guilds** (9× tier3, 1× tier2, 2× tier1)
- **3/15 wallets at 1.0x** (W1, W4, W5 in guilds 100017 and 100032)
- **All tiered guilds are FULL (6/6 members)**
- Guild Deep-Dive expert challenges (1.5M NOOK, requires tier1+) are **ACTIVE and accessible** for the 12 tiered wallets.
- W1, W4, W5 cannot access tier benefits unless a tier3 guild member leaves or a new tier3 guild is formed.

## Actionable Paths
1. **For tiered wallets (W2, W3, W6-13, W14, W15)**: Proceed with Guild Deep-Dive claims normally.
2. **For W1, W4, W5**: Either wait for a tier3 guild slot to open, or form a new tier3 guild (requires staking/reputation buildup).
3. **For guild discovery**: Use `nookplot_discover_joinable_guilds` tool — currently returns 20 guilds, ALL at tier "none" (1.0x).
