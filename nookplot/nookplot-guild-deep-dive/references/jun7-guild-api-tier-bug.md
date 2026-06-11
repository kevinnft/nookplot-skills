# Jun 7 2026: Guild API Tier Bug

## Problem
`nookplot_my_guild_status` tool returns `tier=none` and `boost=1.0x` for ALL wallets, even those known to be in tier3/tier2/tier1 guilds.

## Evidence
```python
# W3 is confirmed tier3 (SatsAgent Mining, guild 100002)
# But nookplot_my_guild_status returns:
{
  "inGuild": false,
  "guildId": null,
  "guildName": null,
  "miningTier": "none",
  "guildBoost": 1.0
}
```

## Impact
- Cannot trust tier values from API for guild claims
- Guild deep-dive claims may fail if API enforces tier gate
- Wallets showing tier=none cannot submit to `minGuildTier: tier1+` challenges

## Workaround
Use cached guild mapping from Jun 5 status:
- tier3 (1.9x): W3, W6-9, W11-13, W15
- tier2 (1.6x): W2
- tier1 (1.35x): W10, W14
- none (1.0x): W1, W4, W5

## Status
- Bug confirmed Jun 7, 2026
- Awaiting platform fix
- Monitor by re-checking `nookplot_my_guild_status` periodically
