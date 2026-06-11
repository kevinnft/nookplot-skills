# Nookplot Cluster Guild Map (May 22 2026)

Authoritative snapshot of which guild each W1-W15 wallet belongs to, plus full
guild inventory. Read this BEFORE planning guild migrations — `my_guild_status`
returns stale/wrong data and burned a 5-step plan in this session.

## CRITICAL PITFALL — `my_guild_status` is UNRELIABLE

`nookplot_my_guild_status` returned `inGuild: false` for W3-W11 even though
`check_guild_mining` rosters proved 8 of those 9 wallets ARE mining members of
real guilds. Examples:

- W6 satoshi → my_guild_status said "no guild", actually in Jetpack tier3
- W9 john → my_guild_status said "no guild", actually in Jetpack tier3
- W11 WhiteAgent → my_guild_status said "no guild", actually in nookplot avengers tier3
- W4 aboylabs → my_guild_status said "no guild", actually in Lyceum legacy 100017
- W5 reborn → my_guild_status said "no guild", actually in Quill Edge 100032

The shape of `my_guild_status.result` differs between an established mining
member and what is presumably a stale-cache code path. We do NOT yet know the
trigger. Until that's debugged, do NOT trust `my_guild_status` for migration
planning.

### Authoritative source: `check_guild_mining` roster

Iterate over candidate guild IDs and read `result.members[].agent_address` —
match against `~/.hermes/nookplot_wallets.json` lowercased addrs.

```python
addr_map = {w['addr'].lower(): slot for slot, w in wallets.items()}
for gid in [2,4,5,7,9,10,100000,100002,100017,100032,100045,100046]:
    r = check_guild_mining(gid)
    for m in r['members']:
        if m['agent_address'].lower() in addr_map:
            print(f"{addr_map[m['agent_address'].lower()]} → guild {gid}")
```

## Active mining guild inventory (May 22 2026 snapshot)

```
TIER3 1.9x — 6 guilds, ALL FULL 6/6
   2  Neural Cartography           stake 189M
   4  Adversarial Analysis         stake 158M
   5  The Lyceum Collective        stake  60M
   7  Vector Field                 stake 148M
  10  nookplot avengers            stake  87M  ← W11, W12 here
 100045 Jetpack                    stake  85M  ← W6, W7, W8, W9 here

TIER2 1.6x — 2 guilds, ALL FULL 6/6
   9  Social Contract              stake  50M  ← W2 here
 100000 Knowledge Collective       stake  40M  ← W10 here

TIER1 1.35x — 2 guilds, OPEN slots
 100002 SatsAgent Mining Coll  10M, 4/6 (2 OPEN) ← W3, W13, W15 here
 100046 The Commission        19M, 3/6 (3 OPEN) ← W14 here

TIER0 (none)
 100017 Lyceum [legacy]    ← W1, W4 here
 100032 Quill Edge         ← W5 here
```

## Full W1-W15 guild map

```
SLOT NAME         GID     GUILD                  TIER   BOOST  STATUS
W1   hermes       100017  Lyceum [legacy]        none   1.0    SUB-OPTIMAL
W2   9dragon      9       Social Contract        tier2  1.6    OPTIMAL (full)
W3   kevinft      100002  SatsAgent              tier1  1.35   OK
W4   aboylabs     100017  Lyceum [legacy]        none   1.0    SUB-OPTIMAL
W5   reborn       100032  Quill Edge             none   1.0    SUB-OPTIMAL
W6   satoshi      100045  Jetpack                tier3  1.9    OPTIMAL ⭐
W7   badboys      100045  Jetpack                tier3  1.9    OPTIMAL ⭐
W8   rebirth      100045  Jetpack                tier3  1.9    OPTIMAL ⭐
W9   john         100045  Jetpack                tier3  1.9    OPTIMAL ⭐
W10  joni         100000  Knowledge Collective   tier2  1.6    OPTIMAL (full)
W11  WhiteAgent   10      nookplot avengers      tier3  1.9    OPTIMAL ⭐
W12  PanuMan      10      nookplot avengers      tier3  1.9    OPTIMAL ⭐
W13  hemi         100002  SatsAgent              tier1  1.35   OK
W14  kicau        100046  The Commission         tier1  1.35   OK
W15  lucky        100002  SatsAgent              tier1  1.35   OK
```

Cluster boost composite:
- Current = (6×1.9 + 2×1.6 + 4×1.35 + 3×1.0) / 15 = **1.53x average**
- Max realistic post-upgrade = (6×1.9 + 2×1.6 + 7×1.35) / 15 = **1.60x average**
- Marginal gain of full migration: **+0.07x avg** — small.

12/15 wallets already at realistic ceiling. Tier3 + tier2 are 6/6 full.

## Migration blockers

W1, W4, W5 all blocked by pending-submission gate:

```
W1 hermes   → 100 pending @ Lyceum legacy 100017  BLOCKED
W4 aboylabs →  66 pending @ Lyceum legacy 100017  BLOCKED
W5 reborn   →  62 pending @ Quill Edge 100032     BLOCKED
```

Gateway error:
```
Cannot leave guild while you have pending submissions attributed to it.
```

50-100 pending counts suggest verification-quorum stall. No
`cancel_submission` tool found.

## Tools (verified May 22 2026)

```
Read-only:
  check_guild_mining(guildId)         ← AUTHORITATIVE source
  my_mining_submissions(addr, limit)  ← markdown text, not JSON
  my_guild_status()                   ← UNRELIABLE, do not trust

Mutation:
  join_guild_mining(guildId, declaredDomains[])
    Errors: "Already a mining member of guild N" → must leave first
            "Too many requests" → rate-limited, sleep 60-90s
  leave_guild_mining(guildId)
    Errors: "Cannot leave guild while you have pending submissions"
            "Not a member of this guild's mining"

NOT FOUND:
  cancel_submission / withdraw / abandon / invite_guild_member
```

## Numbering quirk

Guild IDs come from two distinct ranges:
- **Old series 1-10**: created pre-rebase. IDs 1, 3, 6, 8 dissolved.
  Active in old series: 2, 4, 5, 7, 9, 10.
- **Modern series 100000+**: active range 100000-100046.

When scanning, probe BOTH ranges. Initial scan this session missed guild 9
(W2's tier2) and guild 10 (W11+W12's tier3) because we only checked 100000+.
