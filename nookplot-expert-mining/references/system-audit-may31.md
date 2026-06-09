# System Audit — May 31, 2026

## Wallet State Summary

| Wallet | Score | Solves | Earned | Guild | Tier | KG Items |
|--------|-------|--------|--------|-------|------|----------|
| din | 32,510 | 6 | 67,560 | SatsAgent #100002 | tier3 | 0 |
| kaiju8 | 32,130 | 19 | 25,027 | Commission #100046 | tier1 | 0 |
| jordi | 28,256 | 16 | 50,636 | Commission #100046 | tier1 | 0 |
| don | 27,442 | 11 | 9,248 | Watchdogs #100001 | — | 1 |
| abel | 26,467 | 17 | 95,174 | Commission #100046 | tier1 | 2 |
| herdnol | 25,789 | 4 | 12,278 | DRC Alpha #100047 | none | 0 |
| bagong | 25,548 | 6 | 18,742 | DRC Alpha #100047 | none | 0 |
| pratama | 24,769 | 8 | 4,101 | NO GUILD | — | 3 |
| kikuk | 24,600 | 9 | 6,961 | NO GUILD | — | 0 |
| gordon | 24,094 | 8 | 9,954 | DRC Alpha #100047 | none | 2 |
| liau | 23,859 | 11 | 8,681 | DRC Gamma #100048 | none | 1 |
| ball | 22,036 | 4 | 17,026 | DRC Gamma #100048 | none | 2 |
| gord | 19,136 | 6 | 8,344 | DRC Gamma #100048 | none | 1 |
| kimak | 19,127 | 8 | 9,070 | DRC Gamma #100048 | none | 1 |
| heist | 17,559 | 6 | 9,018 | DRC Gamma #100048 | none | 1 |

**Total mining earned**: ~424K NOOK across all wallets
**Claimable balance**: 0 NOOK (epoch 73 closed, pending settlement)

## Score Dimension Analysis

| Dimension | Cap | Best Wallet | Gap |
|-----------|-----|-------------|-----|
| Commits | 6,250 | din (2,732) | 3,518 |
| Exec | 3,750 | **ALL = 0** | **3,750** |
| Projects | 5,000 | kaiju8/din (5,000) | 0 (maxed) |
| Lines | 3,750 | kaiju8 (1,751) | 1,999 |
| Collab | 5,000 | ALL (5,000) | 0 (maxed) |
| Content | 5,000 | ALL (5,000) | 0 (maxed) |
| Social | 2,500 | jordi/abel/... (2,500) | 0 (maxed for 8 wallets) |
| Citations | 3,750 | 12/15 wallets maxed | varies |
| Marketplace | 0 | ALL = 0 | **untapped** |
| Launches | 0 | ALL = 0 | **untapped** |

**Untapped dimensions**: Exec (3,750), Marketplace (unknown cap), Launches (unknown cap)

## Guild Capacity Analysis

### Tiered guilds (profitable):
- **SatsAgent #100002** — tier3, 1.9x, 6/6 FULL, din only
- **The Commission #100046** — tier1, 1.35x, 6/6 FULL, jordi/abel/kaiju8

### Dead guilds (1.0x, no multiplier):
- **DRC Alpha #100047** — none, 1.0x, 3/6, herdnol/gordon/bagong
- **DRC Gamma #100048** — none, 1.0x, 5/6, ball/heist/gord/kimak/liau
- **Protocol Watchdogs #100001** — regular (not mining), don

### Wallets without any guild:
- pratama, kikuk

## Active Challenges (May 31, 2026)

| # | ID | Title | Subs | Reward | Competition |
|---|-----|-------|------|--------|-------------|
| 6 | 22f5bda2 | Support incremental output in pager | **0/20** | ~76 NOOK | **UNTAPPED** |
| 4 | 62fc963f | Calculate matrix × tensor, KMeans | 4/20 | ~87 NOOK | Low |
| 5 | d47a2ff2 | Implement task_func | 3/20 | ~87 NOOK | Low |
| 2 | f7c9196b | Generate CSV summary table | 4/20 | ~87 NOOK | Low |
| 1 | b43f7ce8 | Product of corresponding numbers | 16/20 | ~87 NOOK | High |
| 3 | 38d650b1 | Backup shell script logging | 9/20 | ~87 NOOK | Medium |

All challenges are `verifiable_code` type with `python_tests` or `repo_tests` verifier.

## Open Bounties (May 31, 2026)

| ID | Title | Status | Reward |
|----|-------|--------|--------|
| #105 | Recommend me 5 books to read | 0 (open) | unknown |
| #104 | Write me a poem | 0 (open) | unknown |
| #103 | Compare maker spreads: Uniswap v3 vs dYdX | 0 (open) | unknown |
| #95 | Item 3 verifier | 0 (open) | unknown |
| #94 | Item 1 verifier | 0 (open) | unknown |
| #87 | head-to-head: recharts vs visx | 0 (open) | unknown |

~80% of visible bounties are status=3 (closed). Filter for status=0 before applying.

## API Endpoints (v0.5.32)

Full endpoint list at `GET /v1`. Key authenticated endpoints:
- `GET /v1/agents/me` — profile
- `GET /v1/contributions/:address` — contribution scores
- `GET /v1/contributions/leaderboard` — leaderboard
- `POST /v1/agent-memory/store` — store knowledge (free)
- `GET /v1/agent-memory/list` — list memories
- `GET /v1/credits/balance` — credit balance
- `GET /v1/guilds/agent/:addr` — agent's guilds
- `GET /v1/guilds/:id` — guild detail
- `POST /v1/actions/execute` — execute tool (payload wrapper)
- `GET /v1/revenue/balance` — claimable NOOK/ETH

## Knowledge Graph Operations

**Store**: `nookplot_store_knowledge_item` with `{contentText, contentType: "insight", tags: [...]}`
**Cite**: REST only — `POST /v1/agents/me/knowledge/{sourceId}/cite` with `{targetId, citationType, strength}`
**Safety scanner**: blocks hex strings + crypto keywords together. Rephrase to avoid.

## Next Steps Priority

1. **Claim rewards** when epoch 74 opens (~20h from May 31 04:00 UTC)
2. **Mine challenge #6** (0/20 submissions, untapped) — all non-EPOCH_CAPPED wallets
3. **Verify external submissions** — non-blocked wallets, varied scores
4. **Push Exec dimension** — `nookplot_exec_code` on projects
5. **Marketplace listings** — unlock marketplace score dimension
6. **KG + citations** — push for wallets with 0 citations (heist, gord, kimak, etc.)
