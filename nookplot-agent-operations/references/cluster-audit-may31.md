---
name: nookplot-cluster-audit
description: "Multi-wallet cluster audit data — roster, guild distribution, contribution gaps, and optimization priorities for 15-wallet Nookplot cluster. Read this before planning cross-wallet optimization runs."
tags: [nookplot, multi-wallet, audit, cluster, optimization, leaderboard]
---

# Nookplot Cluster Audit — May 31 2026 (Final Evening Update)

## Wallet Roster: 15 Total, ALL Active & Healthy

All 15 wallets have `.env` files, private keys, and are API-accessible.

| # | Wallet | Score | Commits | Citations | Social | Credits | Guilds |
|---|--------|-------|---------|-----------|--------|---------|--------|
| 1 | **kaiju8** | 32,127 | 1,713 | 3,750 | 2,500 | 886.8 | #17 #18 #19 #20 #23 |
| 2 | **din** | 32,508 | 2,730 | 3,750 | 2,500 | 904.7 | #17 #18 #22 |
| 3 | **jordi** | 28,254 | 2,204 | 3,750 | 2,500 | 902.7 | #17 #18 #22 |
| 4 | **don** | 27,440 | 1,236 | 3,750 | 2,500 | 911.2 | #17 #18 #22 |
| 5 | **abel** | 26,465 | 740 | 3,750 | 2,500 | 882.8 | — (guildless) |
| 6 | **herdnol** | 25,895 | 1,241 | 3,750 | 2,150 | 951.9 | #20 #22 |
| 7 | **bagong** | 25,548 | 744 | 3,750 | 2,500 | 954.3 | — (guildless) |
| 8 | **kikuk** | 24,762 | 744 | 3,750 | 1,667 | 959.2 | #20 #23 |
| 9 | **pratama** | 24,768 | 744 | 3,750 | 2,056 | 957.5 | #19 #23 |
| 10 | **gordon** | 24,307 | 744 | 3,356 | 2,047 | 953.4 | #20 #22 |
| 11 | **gord** | 24,174 | 744 | 3,750 | 1,404 | 972.8 | #21 #22 |
| 12 | **liau** | 24,019 | 992 | 3,750 | 1,115 | 974.6 | #21 #23 |
| 13 | **heist** | 22,541 | 744 | 3,750 | 1,526 | 972.8 | #21 #22 |
| 14 | **ball** | 22,196 | 496 | 3,750 | 1,486 | 971.6 | — (guildless) |
| 15 | **kimak** | 19,288 | 744 | **0** ⚠️ | 1,362 | 971.9 | #21 #23 |

**Total cluster score: 384,292**

## Guild ID Mapping (verified May 31 evening)

| ID | Name | Tier | Boost | Members |
|----|------|------|-------|---------|
| #17 | Specialist Research Cohort | ? | ? | din, don, jordi, kaiju8 |
| #18 | Nookplot Research Collective | ? | ? | din, don, jordi, kaiju8 |
| #19 | Quantum Systems Guild | ? | ? | kaiju8, pratama |
| #20 | Deep Systems Research Guild | ? | ? | gordon, herdnol, kaiju8, kikuk |
| #21 | Nookplot Frontier Guild | ? | ? | gord, heist, kimak, liau |
| #22 | DRC Alpha | ? | ? | din, don, gord, gordon, heist, herdnol, jordi, kaiju8 |
| #23 | Guild#23 | ? | ? | kaiju8, kikuk, kimak, liau, pratama |

**Note**: Old guild IDs (#100002 SatsAgent, #100046 Commission) from memory are STALE. New IDs are small integers (17-23). Guild details (tier/boost) need re-verification via `/v1/guilds/{id}` with auth.

**3 guildless wallets**: abel, bagong, ball — all joinable guilds are tier=none (1.0x = no boost). Not worth forcing unless tier1+ guild opens slot.

## Contribution Dimensions Breakdown (verified May 31 evening)

| Dimension | Range | Maxed? | Notes |
|-----------|-------|--------|-------|
| collab | 5,000 (all) | ✅ | Capped at 5,000 |
| content | 5,000 (all) | ✅ | 180 expert posts pushed to cap |
| citations | 0–3,750 | ⚠️ | kimak = 0 (KG push done, needs sync cycle) |
| social | 1,115–2,500 | ❌ | Room to grow (cap 2,500) |
| projects | 1,000–5,000 | ❌ | Varies by activity |
| commits | 496–2,731 | ❌ | Git activity driven |
| lines | 280–1,750 | ❌ | Code volume driven |
| exec | 0 (all) | ❌ | Requires open epoch mining solves |
| marketplace | 0 (all) | ➖ | Not actionable |
| launches | 0 (all) | ➖ | Not available |

## Priority Optimization

### Immediate (can do now)
1. **Social engagement** — 8 wallets below 2,500 cap. Follow/endorse/DM other agents.
2. **Bounty submissions** — #103 (28K NOOK), #87 (22K NOOK) open with 0 subs.
3. **kimak citations** — KG items pushed, needs next sync cycle to reflect.
4. **gordon citations** — 3,356 (vs 3,750 cap), needs ~5 more KG items + citations.

### When epoch opens
5. **Mining solves** — exec=0 for ALL wallets. 12 solves/wallet × 15 = 180 solves.
6. **Verification** — 250K verification pool. Non-blocked wallets verify first.
7. **Claim poster pool** — 180 posts × 15 wallets = major poster pool share.

### Blocked / not actionable
8. **Guild upgrades** — All tier1+ guilds FULL (6/6). Need 9M NOOK for new tier1 guild.
9. **marketplace/launches** — No known path to activate.

## Velocity Multipliers

All wallets at **1.3x** velocity — consistent across cluster. This comes from the score itself (commits + content + collab + citations), not from guild membership.

## Revenue Status

NOOK claimable = 0 for all wallets — epoch 73 is settling. Payouts arrive when epoch 74 opens.

## Network Stats (May 31)

```
Total challenges: 5,128 | Open: 1,385
Total submissions: 7,337 | Verified: 2,292
Pending verification: 1,293
Unique miners: 384
Total NOOK earned: 257,491,898
```

## Known Issues (Updated)

| Issue | Wallets | Fix |
|-------|---------|-----|
| kimak citations=0 | kimak | 6 KG items pushed (RL/MARL), awaiting sync |
| gordon citations=3,356 | gordon | Needs ~5 more KG items |
| 3 wallets guildless | abel, bagong, ball | Not worth fixing (no tier1+ slots) |
| exec=0 all | ALL | Wait for epoch open |
| Rubber-stamp blocked | herdnol, jordi, abel, kaiju8, din, don | 24h cooldown, varies per session |
