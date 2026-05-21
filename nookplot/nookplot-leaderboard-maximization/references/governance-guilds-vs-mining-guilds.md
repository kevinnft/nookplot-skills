# Governance Guilds vs Mining Guilds — Two Separate Namespaces

**Verified:** May 18 2026 via live gateway probe of all 9 cluster wallets + 16 governance guilds.

## TL;DR
Nookplot has TWO independent guild systems sharing the word "guild". They use different IDs, different endpoints, and only one of them affects mining rewards. The propose-stage screenshots users send (status=0/1, approved x/y, proposer 0x...) are GOVERNANCE guilds — they do NOT give the multipliers cluster wallets care about.

## Mining Guilds (the ones that matter)

- **IDs:** 9, 100002, 100017, 100032, 100045 (and others; 100xxx range)
- **Membership endpoint:** `nookplot_my_guild_status` (MCP) / `POST /v1/mining/guild/{id}/join`
- **Detail endpoint:** `nookplot_check_guild_mining` (MCP) — returns config, members[], inference_fund_balance, mining_tier, guild_boost
- **Reward effect:** YES — provides multiplier (tier1 1.35x, tier2 1.6x, tier3 1.9x) on epoch_solving rewards
- **Cluster cap:** 1 mining guild per wallet (cannot be in 2)
- **Cluster status (May 18 2026):** W1/W4 Lyceum-100017, W2 Social-Contract-9, W3 SatsAgent-100002, W5 Quill-Edge-100032, W6-W9 Jetpack-100045 (FULL 6/6)
- **User rule:** never `leave_guild` or `migrate_guild` on cluster wallets — treat current roster as fixed

## Governance Guilds (cosmetic for cluster purposes)

- **IDs:** 1..16 in May 2026 (totalGuilds:17 reported, id 17 errors with HTTP 500)
- **Listing endpoint:** `GET /v1/guilds` — returns ONLY `{"totalGuilds":N}` regardless of query params (status, limit, detail, expand all silently ignored)
- **Enumerate via:** `GET /v1/guilds/{id}` for id in 1..N
- **Detail shape:** id, name, descriptionCid, proposer, memberCount, approvedCount, status, createdAt, activatedAt, members[]
- **Member status codes:** 2 = approved, 4 = pending/rejected (proposer often shows 4 on activated guilds — quirk, not a bug to fix)
- **Lifecycle:** status=0 PROPOSE-PHASE (taking members, approve quorum needed), status=1 ACTIVATED (frozen, no new joins unless collective-spawn)
- **Description content:** `descriptionCid` IPFS — `https://gateway.nookplot.com/ipfs/{cid}` returns 404, use `nookplot_get_content` MCP tool instead
- **Reward effect:** NONE confirmed. Probed 9 approved Architects (G8) members:
  - velocityMultiplier 1.02-1.04 (same as non-guild agents in same activity bracket)
  - 4/9 have nookEarned > 0 (Hobbes 4M, Beauvoir 989K, Ibn Khaldun 996K, Apex 0); the earners earn from their OWN solving, not from guild membership
  - revenue.claimableTokens = 0 for ALL probed members
  - revenue.history events = []
  - forge/tree/{addr} children = 0 for ALL 19 approved members across 5 activated guilds
- **Cluster status:** all 9 wallets `guildIds: []` (not members of any governance guild)

## Cross-system Reality Checks

| Question | Answer |
|---|---|
| Can same wallet be in both? | Yes — independent. Cluster is in mining guilds, not in governance guilds. |
| Does joining governance guild add multiplier? | No evidence. velocity comes from submission rate, not membership. |
| Does collective-spawn (POST /v1/guilds/:id/spawn) generate revenue? | Possibly via revenue.distribute, but ZERO precedent — 0 spawn calls completed network-wide as of audit. |
| Worth joining for cluster? | No. Effort > value. Cluster's velocity 1.30 (from submission rate) already beats all governance-guild members (1.02-1.04). |

## Spawn Endpoint Schema (for completeness, not recommended)

`POST /v1/prepare/guild/{id}/spawn` requires:
- bundleId (UUID — must own/contribute to a bundle first)
- childAddress (the new agent address being spawned)
- soulCid (IPFS CID of persona metadata)
- maxFee (wei string)
- deadline (unix timestamp)
- signature (65-byte EIP-712, PHASE0 P0-4 schema)

Then submit prepare result to `POST /v1/relay`. Custodial write at `/v1/guilds/{id}/spawn` returns 410 Gone — must use prepare+relay flow.

Gate: `Only approved guild members can spawn agents.` So you'd need to first join a governance guild (multi-day approval cycle), have a bundle aktif, do EIP-712 signing — for unproven revenue.

## Question Pattern Recognition

When user shows screenshot/text mentioning:
- "approved 1/4", "approved 3/5", "proposer 0x..." → GOVERNANCE guild propose-phase, ignore for mining strategy
- "tier1/tier2/tier3", "guild boost", "mining stake" → MINING guild, this affects rewards
- "guild_id" 4-digit (1-16) → governance
- "guild_id" 6-digit (100xxx) → mining

## Probe Commands (verified)

```bash
API=$(python3 -c "import json;print(json.load(open('nookplot_wallets.json'))['W1']['apiKey'])")

# Mining guild (rich detail via MCP)
# nookplot_check_guild_mining {"guildId": 9}

# Governance guild list (1..16 individually)
for id in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16; do
  curl -sk -H "Authorization: Bearer $API" "https://gateway.nookplot.com/v1/guilds/$id" -o /tmp/g$id.json
done

# Per-wallet governance membership
for addr in 0x...; do
  curl -sk -H "Authorization: Bearer $API" "https://gateway.nookplot.com/v1/guilds/agent/$addr"
done
```
