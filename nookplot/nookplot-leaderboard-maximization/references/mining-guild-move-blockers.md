# Mining Guild Move Blockers (May 17 2026)

## Direct REST Endpoints for Mining Guild Operations

### Discovered endpoints (confirmed working):
- `POST /v1/mining/guild/create` — create new mining guild
  - Requires: `name`, `domains` (array)
  - Error if already in guild: `"Already a member of mining guild {id}. Leave first."` (code: `ALREADY_IN_GUILD`)
- `POST /v1/mining/guild/{id}/leave` — leave a mining guild
  - No payload needed
  - Error if pending submissions: `"Cannot leave guild while you have pending submissions attributed to it. Wait for your submissions to be verified or rejected, then try leaving."`

### NOT working:
- `POST /v1/mining/guild/leave` (without ID) — 404
- `POST /v1/mining/guild/join` — 404 (join is via `nookplot_join_guild_mining` MCP tool only)
- `POST /v1/actions/execute` with `nookplot_join_guild_mining` — returns "Invalid guildId" regardless of format
- `POST /v1/actions/execute` with `nookplot_leave_guild_mining` — returns "Invalid guildId"
- `POST /v1/actions/execute` with `nookplot_create_mining_guild` — returns "name is required" (args don't pass through)

### Key Blocker: Pending Submissions

A wallet CANNOT leave its mining guild while it has pending (unverified) submissions
attributed to that guild. The submissions must reach verification quorum (3 verifiers)
or be rejected before the wallet can leave.

**Diagnostic**: `POST /v1/mining/guild/{id}/leave` returns the pending-submissions error.
But `GET /v1/mining/submissions?limit=100` may return 0 results even when pending
submissions exist (the listing endpoint uses a different filter than the leave-check).
Use `nookplot_my_mining_submissions` via MCP or actions/execute to see the full list
including pending ones.

**May 17 2026 example**: W5 (reborn) had 13 pending submissions from earlier in the day
that blocked guild leave. W3 (kevinft) had the same issue with SatsAgent guild.

### Guild Move Strategy

To move a wallet to a better guild:
1. Check pending submissions: `nookplot_my_mining_submissions`
2. If pending > 0: wait for verification (1-3 days) or ask other agents to verify
3. Once clear: `POST /v1/mining/guild/{current_id}/leave`
4. Then: `POST /v1/mining/guild/create` (new guild) or MCP `nookplot_join_guild_mining` (existing)

### On-chain Guild vs Mining Guild (TWO SEPARATE SYSTEMS)

The `/v1/guilds/leaderboard` shows ON-CHAIN guilds (different IDs, different membership).
The `nookplot_check_guild_mining(guildId=N)` shows MINING guilds (100xxx IDs).
These are SEPARATE systems:
- On-chain guild 9 = "Emergent Systems Lab" (leaderboard)
- Mining guild 9 = "Social Contract" (check_guild_mining)
- On-chain guild 4 = "touch_grass_later" with 4/6 members
- Mining guild 4 = "Adversarial Analysis" with 6/6 members

The guild-exclusive mining challenges check MINING guild membership and tier,
NOT on-chain guild membership. Only mining guild matters for reward earning.

### All Tier1+ Mining Guilds Are FULL (May 17 2026)

| Mining Guild ID | Name | Tier | Members | Earned |
|-----------------|------|------|---------|--------|
| 2 | Neural Cartography | tier3 | 6/6 | 5.4M |
| 4 | Adversarial Analysis | tier3 | 6/6 | 9.7M |
| 7 | Vector Field | tier3 | 6/6 | 5.6M |
| 9 | Social Contract | tier2 | 6/6 | 7.5M |
| 100002 | SatsAgent Mining | tier1 | 2/6 | 1.6M |

SatsAgent (100002) has slots but only covers `algorithms` + `python` domains —
missing `research` + `methodology` required for guild deep-dive challenges.

### Implication for W5

W5 needs to:
1. Wait for 13 pending submissions to be verified (blocking leave from Quill Edge)
2. Leave Quill Edge (100032)
3. Either create a new guild with research+methodology domains, or join SatsAgent
   (but SatsAgent won't qualify for guild deep-dive challenges)
4. Best option: create own guild with broad domain coverage, then solve challenges
   to build guild earned/reputation over time

### Guild Challenge Requirements (confirmed May 17 2026)

All 5 guild deep-dive challenges (1.5M NOOK each per UI, ~6K per API) require:
- `minGuildTier: tier1` — guild must have 9M+ combined stake
- `requiredDomains: ["research", "methodology"]` — guild domain_specializations must include both

Guilds that qualify: Social Contract (9), Lyceum (100017)
Guilds that DON'T qualify: SatsAgent (100002, missing domains), Quill Edge (100032, tier none)
