# Guild Discovery + Tier Saturation Reality Check

When user asks "find higher-tier guild" / "cari guild tier tinggi" for any wallet,
the workflow below is the canonical answer. Discovered May 22, 2026 by exhaustive
probe of guild ID space.

## Discovery Mechanics (Gateway has no list endpoint)

`GET /v1/guilds` returns ONLY `{"totalGuilds": N}` — a count, not a list.
Tried alternates, all dead ends:
- `/v1/guilds/list` → "Invalid guild ID."
- `/v1/guilds/all` → "Invalid guild ID."
- `/v1/guilds?include=members` → still just `{"totalGuilds":17}`
- `/v1/mining/guilds` → 404

The only working enumeration is sequential ID probing via the action endpoint:

```
POST /v1/actions/execute
{"toolName":"check_guild_mining","payload":{"guildId":<ID>}}
```

Guild IDs start at **100000** and are dense (no gaps observed in 100000-100020).
Probe upward until you hit a contiguous run of "NX" responses.

## Probe Script (30s for 50 IDs)

```bash
API=$(python3 -c "import json; print(json.load(open('/home/asus/.hermes/nookplot_wallets.json'))['W1']['apiKey'])")
for gid in $(seq 100000 100050); do
  out=$(curl -s -X POST https://gateway.nookplot.com/v1/actions/execute \
    -H "Authorization: Bearer $API" -H "Content-Type: application/json" \
    -d "{\"toolName\":\"check_guild_mining\",\"payload\":{\"guildId\":$gid}}")
  line=$(echo "$out" | python3 -c "import sys,json
try:
  d=json.load(sys.stdin); r=d.get('result',{})
  if 'error' in d or not r: print('NX')
  else:
    c=r.get('config',{})
    print(f\"{c.get('name','?')[:30]:30} tier={c.get('mining_tier','?'):7} boost={c.get('guild_boost','?'):4} members={len(r.get('members',[]))}/6 stake={int(c.get('mining_stake','0'))//10**18:>10}\")
except: print('ERR')" 2>/dev/null)
  echo "$gid: $line"
  sleep 1
done
```

Sleep 1s between calls to avoid rate-limit (without sleep you hit
`Too many requests` after ~3-5 hits and the 15s back-off rolls into a
session-killing 5min timeout).

## Tier Table (verified May 22, 2026)

| Tier  | Boost | Min Combined Stake | Tier-up Cost from prev |
|-------|-------|--------------------|-----------------------:|
| tier0 | 1.0x  | 0                  | —                      |
| tier1 | 1.35x | 9,000,000          | +9M from 0             |
| tier2 | 1.6x  | 25,000,000         | +16M from 9M           |
| tier3 | 1.9x  | 60,000,000         | +35M from 25M          |

`nookToNextGuildTier` in the response returns the GAP, not the absolute target.
Formula: `nookToNextGuildTier = next_threshold − combined_stake`. So a guild at
10M with `nextGuildTier:tier2, nookToNextGuildTier:15M` confirms tier2=25M.

## Saturation Reality (May 22, 2026 snapshot, 17 guilds)

**High-tier guilds are saturated 6/6:**

| ID     | Name                   | Tier  | Boost | Members |
|--------|------------------------|-------|-------|---------|
| 100045 | Jetpack                | tier3 | 1.9x  | 6/6 ❌  |
| 100000 | Knowledge Collective   | tier2 | 1.6x  | 6/6 ❌  |

**Tier1 guilds with open slots:**

| ID     | Name                          | Tier  | Members | Notes              |
|--------|-------------------------------|-------|---------|--------------------|
| 100002 | SatsAgent Mining Collective   | tier1 | 4/6     | W13,W15 here       |
| 100046 | The Commission                | tier1 | 3/6     | W14 here           |

Other 13 guilds (100001, 100003-100020, 100036-100044): tier0 / 1.0x — pointless.

## Verdict Pattern for "find higher-tier guild" Queries

When the wallet is already in a tier1 guild and the only open higher-tier slots
are at 6/6 capacity:

1. State that tier2 + tier3 guilds are full (numbers).
2. Show that current placement is already the maximum available.
3. Optionally enumerate paths the user CAN take if they relax their no-stake rule:
   - Push current guild to tier2: compute exact NOOK gap.
   - Create new guild: 9M minimum stake for tier1.
4. Do NOT recommend leaving a tier1 with open slots for a tier1 with fewer members
   unless the user explicitly asks about reputation or domain alignment.

User no-stake rule blocks tier-up via direct stake. So the typical answer is
"already maximal under your constraints." Surface that quickly.

## Pitfalls

- Probing 100021-100035 returned NX in this snapshot — guild IDs are NOT strictly
  contiguous past the early block. Don't stop probing at first NX. Probe at least
  +50 IDs past last known guild before declaring complete.
- `totalGuilds` from `GET /v1/guilds` is the source-of-truth count. Confirm your
  enumeration matches this number before answering.
- `inferenceFundBalance` in config is separate from staking — it's the
  guild-creator royalty pool. Non-zero values are NOT staking events.
- `check_guild_mining` does NOT require membership — any wallet can read any
  guild's full member roster + stakes. Read-only intel is free.

## Cross-References

- `guild-deep-dive-strategy.md` — strategic placement criteria once you have
  the saturation map.
- `competitor-economics-decomposition.md` — for `total_guild_earned` forensics.
- `wallets-json-slot-collision-recovery.md` — wallet file structure if you
  need to reference multiple wallets by slot.
