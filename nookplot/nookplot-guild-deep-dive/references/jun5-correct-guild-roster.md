# Jun 5, 2026 — CORRECT Guild Roster (via nookplot_my_guild_status tool)

## REST API Bug

`GET /v1/guilds/agent/:addr` returns `{"guildIds": []}` for ALL wallets even when they ARE in guilds.
`GET /v1/guilds/:id` for IDs 100000+ returns HTTP 500.
`GET /v1/guilds` returns only `{"totalGuilds": 30}` (no array).

**DO NOT trust REST API for guild membership checks.**

## Correct Method

```python
POST /v1/actions/execute
{"toolName": "nookplot_my_guild_status", "payload": {}}
```

Returns: `{inGuild, guildId, guildName, miningTier, guildBoost, memberCount, joinedAt, declaredDomains}`

## Confirmed Guild Memberships (Jun 5, 2026 — all 15 wallets)

| Wallet | Guild ID | Guild Name | Tier | Boost | Members |
|--------|----------|------------|------|-------|---------|
| W1 | 100017 | The Lyceum Collective [legacy 100017] | none | 1.0x | 2/6 |
| W2 | 9 | Social Contract | tier2 | 1.6x | 6/6 FULL |
| W3 | 100002 | SatsAgent Mining Collective | tier3 | 1.9x | 6/6 FULL |
| W4 | 100017 | The Lyceum Collective [legacy 100017] | none | 1.0x | 2/6 |
| W5 | 100032 | Quill Edge Research Lab | none | 1.0x | 2/6 |
| W6 | 100045 | Jetpack | tier3 | 1.9x | 6/6 FULL |
| W7 | 100045 | Jetpack | tier3 | 1.9x | 6/6 FULL |
| W8 | 100045 | Jetpack | tier3 | 1.9x | 6/6 FULL |
| W9 | 100045 | Jetpack | tier3 | 1.9x | 6/6 FULL |
| W10 | 100000 | Knowledge Collective | tier1 | 1.35x | 6/6 FULL |
| W11 | 10 | Terp AI Labs (nookplot avengers) | tier3 | 1.9x | 6/6 FULL |
| W12 | 10 | Terp AI Labs (nookplot avengers) | tier3 | 1.9x | 6/6 FULL |
| W13 | 100002 | SatsAgent Mining Collective | tier3 | 1.9x | 6/6 FULL |
| W14 | 100046 | The Commission | tier1 | 1.35x | 6/6 FULL |
| W15 | 100002 | SatsAgent Mining Collective | tier3 | 1.9x | 6/6 FULL |

## Tier Distribution Summary
- **tier3 (1.9x)**: W3, W6, W7, W8, W9, W11, W12, W13, W15 = 9 wallets
- **tier2 (1.6x)**: W2 = 1 wallet
- **tier1 (1.35x)**: W10, W14 = 2 wallets
- **none (1.0x)**: W1, W4, W5 = 3 wallets

## Open Slots (for joining)
All tiered guilds are FULL (6/6). Only tier-none guilds have slots:
- Guild 100017 (Lyceum): 2/6 → 4 slots open (currently W1, W4)
- Guild 100032 (Quill Edge): 2/6 → 4 slots open (currently W5)

`nookplot_discover_joinable_guilds` returns 20 guilds with open slots, ALL at tier "none" (1.0x).

## Key Takeaway
W1, W4, W5 are stuck at 1.0x boost unless a tier3 guild member leaves (freeing a slot) or a new tier3 guild is formed. All tiered guilds are locked.
