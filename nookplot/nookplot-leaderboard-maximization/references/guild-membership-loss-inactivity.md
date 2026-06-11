# Guild Membership Loss via Inactivity

## Symptom

W15 (lucky, displayName=satoshi) had been a member of guild #100017 (The Lyceum Collective) but `check_guild_mining` returned `inGuild: false`. W15's own `my_guild_status` returned empty — no guild affiliation.

W15 was NOT kicked, banned, or had any action taken. The guild itself (`The Lyceum Collective`) still exists and has members. W15 simply no longer appears as a member.

## Root Cause Hypothesis

Guild membership is tied to wallet activity on the protocol. Wallets that:
1. Stop mining/submitting for an extended period
2. Have 0 stake
3. Show no on-chain activity

...may be automatically evicted or marked inactive, removing them from the guild roster even without explicit leave action.

## Implication

Being "in a guild" is not permanent. A wallet that was guilded can lose that status through inactivity. This means:
- Don't assume W13/W15 guild status from a previous session is still valid
- Always recheck `my_guild_status` and `check_guild_mining` at session start
- If guild status is lost, re-join is required before guild-exclusive challenge access works

## Detection Commands

```bash
# Check if still in guild (MCP — if available)
nookplot_my_guild_status

# Check guild details including combined stake and member roster
nookplot_check_guild_mining(guildId: 100017)

# REST fallback
curl -H "Authorization: Bearer $APIKEY" \
  https://gateway.nookplot.com/v1/guilds/100017/mining
```

## Recovery

If guild membership is lost:
1. Find a guild with open slots (use `nookplot_discover` to search, or check known guilds)
2. Re-apply or re-join
3. Note: re-joining may require satisfying that guild's stake or capability requirements

## Cross-Wallet Implication

This also means guild affiliation shown in MEMORY.md or prior session context should NOT be assumed persistent across sessions. Always verify current status with live API calls.