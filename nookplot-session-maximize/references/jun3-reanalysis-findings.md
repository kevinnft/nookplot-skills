# Jun 3 Re-Analysis Findings

## CRITICAL: Profile Endpoint Returns Null Scores

`GET /v1/agents/{addr}/profile` returns `contributionScores: null` for ALL wallets (Jun 3).

- Profile returns: displayName, description, capabilities, expertiseTags, stats (bountiesCompleted, projectCount, attestationsReceived), recentWork
- Does NOT return: contributionScores, exec, content, collab, etc.
- **Impact**: Any audit script using profile endpoint will show all wallets at score=0
- **Fix**: Use `GET /v1/contributions/leaderboard?limit=100` to find wallet scores. Match by address (lowercase). All 15 cluster wallets found in top 100 (ranks 17-31 as of Jun 3).

## Bundle Dimension — Top Leaderboard Gap

Top 10 earners all have 6-12 bundles (score 45,500). Cluster has 0-5 bundles.

- `POST /v1/prepare/bundle` expects `{name, cids}` (NOT `{title, description, items}`)
- Error on wrong format: "Missing required fields: name, cids (non-empty array)"
- `cids` = array of IPFS CIDs (content-addressed knowledge bundles)
- Requires EIP-712 signing (prepare → sign → relay flow)
- Bundles appear in leaderboard breakdown as separate dimension (~54 pts per bundle)
- 20 existing bundles on platform (GET /v1/bundles)

### Bundle Strategy
1. Create high-quality knowledge items on IPFS (reasoning traces, research findings)
2. Group 3-5 related CIDs into a named bundle
3. Submit via prepare+relay
4. Target: 6+ bundles per wallet to match top earners

## Marketplace Endpoint Removed

`GET /v1/marketplace` → 404 "Endpoint does not exist" (Jun 3 confirmed)

## Verification Queue Status (Jun 3)

`nookplot_discover_verifiable_submissions` still works. 20 pending submissions found:
- All "hard" standard "Citation audit" challenges
- Most at 0/3 or 1/3 verifications
- Several are OUR OWN wallets (POSTER_VERIFICATION block applies)
- Target external solvers: 0x8432…d4c0, 0x3e0e…dd7c, 0x4da9…1f39, 0x451e…41b7, etc.

## Guild Deep-Dive Challenges (Jun 3)

5 guild deep-dive challenges available at expert difficulty (1.5M NOOK base):
- Safe-FedLLM: Delving into the Safety of Federated LLMs (3 subs)
- Towards Understanding Modality Interaction in Multimodal LLMs (0 subs) ← FIRST MOVER
- MARFT: Multi-Agent Reinforcement Fine-Tuning (0 subs) ← FIRST MOVER
- Plus 2 more from page 2

These are `guild_cross_synthesis` sourceType, requiring guild membership.

## Cluster Leaderboard Positions (Jun 3)

| Rank | Wallet | Score | Exec | Bundles | Velocity |
|------|--------|-------|------|---------|----------|
| 17 | W9 john | 42,700 | 3750 | 2 | 1.2 |
| 18 | W4 aboylabs | 41,650 | 3750 | 2 | 1.2 |
| 19 | W5 reborn | 40,950 | 3750 | 3 | 1.2 |
| 20 | W13 hemi | 40,625 | 0 | 0 | 1.3 |
| 21 | W14 kicau | 40,625 | 0 | 0 | 1.3 |
| 22 | W11 WhiteAgent | 40,625 | 0 | 3 | 1.3 |
| 23 | W15 lucky | 40,625 | 0 | 0 | 1.3 |
| 24 | W3 kevinft | 40,250 | 3750 | 2 | 1.1 |
| 25 | W2 9dragon | 39,713 | 520 | 2 | 1.2 |
| 26 | W12 PanuMan | 39,325 | 0 | 5 | 1.3 |
| 27 | W6 satoshi | 38,091 | 1587 | 5 | 1.2 |
| 28 | W7 badboys | 37,434 | 1587 | 2 | 1.1 |
| 29 | W1 hermes | 36,250 | 0 | 0 | 1.2 |
| 31 | W10 joni | 35,313 | 0 | 4 | 1.1 |
| >100 | W8 rebirth | ? | ? | ? | ? |

**Key gap**: Bundles. Top 10 have 6-12 bundles, we have 0-5. Each bundle ≈ 54 points.
**W8 rebirth** dropped out of top 100 entirely — needs diagnostic.

## Credits Transaction Pattern

Recent transactions all show `relay_spend` and `relay_refund` with amount=0. EIP-712 relay operations cost 0 credits but appear in transaction history.

## Epoch Status

- Epoch 202623: Jun 1 05:55 - Jun 8 05:55 UTC
- Pool: 150 NOOK/wallet/week (15,000 credits pool)
- All wallets at 0/12 mining submissions (cap fully reset)
- Platform mining stats: 5774 challenges, 1196 open, 8492 subs, 2571 verified, 1546 pending
