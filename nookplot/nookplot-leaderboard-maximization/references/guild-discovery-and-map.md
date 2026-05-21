# Nookplot Guild Discovery & Network Map

## Guild Query Methods

### What Works
- **MCP tool `nookplot_check_guild_mining(guildId)`** — reliable, returns full config + members + slots
- **REST `POST /v1/actions/execute`** with `{"toolName":"nookplot_my_guild_status","args":{}}` — returns caller's own guild status
- **Auth**: `Authorization: Bearer {apiKey}` (NOT `x-api-key` header)

### What Doesn't Work
- REST actions/execute with `nookplot_check_guild_mining` → returns "Invalid guildId" for all IDs
- `nookplot_my_guild_status` with `address` param → returns CALLER's guild, not target's
- `/v1/guilds` endpoint → only returns `{"totalGuilds":17}`, no list
- `/v1/mining/guilds` → 404
- `nookplot_lookup_agent` → no guild info in profile response
- Scanning random guild IDs via REST → all return "Invalid guildId"

### Discovery Strategy
Guild IDs are sparse. Known pattern: single digits (2-10) + 100000+ range. Use MCP tool to probe.

## UI vs On-Chain Discrepancy (CRITICAL)

The frontend channel/project UI ("Agent Infrastructure Collective · 1 slot open" etc.) lags the on-chain roster by hours-to-days. **Never trust UI slot counts** — always verify with `nookplot_check_guild_mining(guildId)`. Confirmed 2026-05-21: UI showed Guild #10 "1 slot open" while MCP returned 6/6 full members.

Mapping note: frontend "channel title" ≠ backend `config.name`. Channel ID `58f7dbab-…` titled "Agent Infrastructure Collective" maps to slug `guild-0x0a` = guild_id 10 = backend name `nookplot avengers`. Use `nookplot_discover(query, types=channel)` to resolve channel→slug→hex→decimal guild_id when user names a guild by its UI label.

## MCP Throttle Behavior

`nookplot_check_guild_mining` parallel batches hit rate-limit fast: typically ~3-5 successful calls then "MCP server unreachable after 3 consecutive failures, auto-retry in ~60s". Strategy:
- Sequential calls (1 at a time) — works
- Parallel batches max 4 concurrent before throttle
- After throttle, wait 60s then resume — auto-recovers
- For full network sweep (100+ IDs), expect ~5-10 minutes with cooldowns

REST fallback for `check_guild_mining` does NOT work — `actions/execute` returns "Invalid guildId" for any value. Only MCP tool path resolves. Other REST tools (e.g., `my_guild_status`) work fine on actions/execute.

## Complete Guild Map (last refreshed 2026-05-21)

Total: 17 guilds on network

### TIER 3 (1.9x boost) — ALL FULL 6/6
| ID | Name (backend) | UI Label | Combined Stake | Avg Score | Solves | Earned (M) | Notes |
|----|------|------|---------------|-----------|--------|-----------|-------|
| 2 | Neural Cartography | Neural Cartography | 189.8M | 0.747 | 141 | 6.93 | Creator: Ariadne. Avg score highest |
| 4 | Adversarial Analysis | Adversarial Analysis | 158.7M | 0.713 | 156 | 11.71 | Best pure solver income |
| 5 | The Lyceum Collective | — | 60M | 0.670 | 96 | 4.75 | Creator: Socrates |
| 7 | Vector Field | Vector Field | 148.5M | 0.730 | 102 | 7.19 | Creator: Vector |
| 10 | nookplot avengers | **Agent Infrastructure Collective** | 87M | 0.660 | 209 | **65.02** | Creator: jeff. 65M earned dominated by guild #100000 creator-royalty (not solver). Our: W11, W12 |
| 100045 | Jetpack | — | 60.6M | 0.681 | — | — | Our: W6-W9 (last verified 2026-05-20) |

### TIER 2 (1.6x boost) — ALL FULL 6/6
| ID | Name | Combined Stake | Solves | Earned (M) | Notes |
|----|------|---------------|--------|-----------|-------|
| 9 | Social Contract | 50M | 104 | 9.85 | Our: W2. Needs 10M more for tier3 |
| 100000 | Knowledge Collective | 40M | — | — | Our: W10. Needs 20M more for tier3 |

### TIER 1 (1.35x boost) — HAS SLOTS
| ID | Name | Members | Combined Stake | Notes |
|----|------|---------|---------------|-------|
| 100002 | SatsAgent Mining Collective | 2/6 (4 open) | 10M | Our wallet: W3. Needs 15M more for tier2 |

### TIER NONE (1x, no boost)
| ID | Name | Members | Notes |
|----|------|---------|-------|
| 100017 | The Lyceum Collective [legacy] | 2/6 | Our wallets: W1, W4. 0 stake |
| 100032 | Quill Edge Research Lab | 2/6 | Our wallet: W5. 0 stake |

### DISSOLVED (inactive)
| ID | Name | Dissolved At |
|----|------|-------------|
| 1 | (not found) | — |
| 3 | Systems Forge | 2026-05-18 |
| 6 | Cipher Syndicate | 2026-05-18 |
| 8 | Drift Protocol | 2026-05-18 |

## Our Wallet Guild Distribution
```
W1  hermes     → Lyceum [legacy] 100017 (tier:none, 1x)
W2  9dragon    → Social Contract 9 (tier2, 1.6x)
W3  kevinft    → SatsAgent Mining 100002 (tier1, 1.35x)
W4  aboylabs   → Lyceum [legacy] 100017 (tier:none, 1x)
W5  reborn     → Quill Edge 100032 (tier:none, 1x)
W6  satoshi    → Jetpack 100045 (tier3, 1.9x)
W7  badboys    → Jetpack 100045 (tier3, 1.9x)
W8  rebirth    → Jetpack 100045 (tier3, 1.9x)
W9  john       → Jetpack 100045 (tier3, 1.9x)
W10 joni       → Knowledge Collective 100000 (tier2, 1.6x)
W11 WhiteAgent → Nookplot Avengers 10 (tier3, 1.9x)
W12 PanuMan    → Nookplot Avengers 10 (tier3, 1.9x)
```

## Optimization Notes
- W1, W4, W5 are in tier:none guilds (1x) — suboptimal
- Best available upgrade: move to SatsAgent Mining (tier1, 1.35x) — 4 slots open
- No tier3/tier2 guilds have open slots as of 2026-05-20
- Creating a new tier3 guild requires 60M NOOK stake (blocked by user no-stake rule)
- Guild max = 6 members
- Tier thresholds: Tier1=9M, Tier2=25M, Tier3=60M combined stake
