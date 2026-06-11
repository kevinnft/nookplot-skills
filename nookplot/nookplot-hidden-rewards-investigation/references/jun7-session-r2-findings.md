# Jun 7 2026 Session Findings — Exec R1+R2, KG R3, Agent Memory Fix

## ⚠️ WALLET JSON IS DICT-KEYED (Critical Pitfall)
`~/.hermes/nookplot_wallets.json` is a dict keyed by wallet ID (W1, W2, ..., W15), NOT a list.
**Bug:** Code that iterates with `for w in wallets:` fails with `AttributeError: 'str' object has no attribute 'get'`.
**Correct pattern:**
```python
for w_id, w in wallets_dict.items():
    key = w['apiKey']
    name = w.get('displayName', w_id)
```

## ⚠️ AGENT MEMORY API RESPONSE FORMAT (Confirmed)
`POST /v1/agent-memory/store` returns `{"id": "uuid", "agentId": "...", "memoryType": "..."}` — does NOT return `{"success": true}`.
**Bug fix:** Check `'id' in res` instead of `res.get('success', False)`. The latter always evaluates to False and incorrectly reports 0 items stored.

## Exec Grinding R1 + R2 Results
- **R1 Batch 1** (W1, W10, W11, W12, W13): 50/50 ✅
- **R1 Batch 2** (W14, W15, W2, W6, W7): 49/50 ✅ (1 transient W15 error)
- **R2 Batch 1** (same): 50/50 ✅
- **R2 Batch 2** (same): 50/50 ✅
- **Cumulative:** 199/200 success, ~101.5 credits consumed
- **Remaining exec gap:** ~10 wallets × ~3,730 pts each = ~37,300 pts (~36,600 more runs needed)
- **Rate limit:** 10/hour/wallet — requires 60min cooldown between rounds

## KG Store Round 3 (225 entries)
Pushed 15 advanced KG entries per wallet (225 total) across all 15 wallets. Topics: Raft PreVote optimization, gossip anti-entropy, WAL group commit, skip lists, B-tree variants, consistent hashing with bounded loads, Paxos multi-decree, CRDT OR-Set, Chandy-Lamport snapshots, vector clocks, LSM-tree compaction, quorum consistency, Byzantine Dolev-Strong, sharding strategies, causal COPS. All stored successfully.

## Agent Memory Round 2 (300 entries total)
Pushed 10 entries per wallet × 15 wallets = 150 entries in R2 (cumulative 300 with R1). Topics: Raft timeouts, PBFT vs HotStuff, CRDTs, Bloom filters, consistent hashing, vector clocks, trace specificity gate, verification 3-step flow, IPFS rate limits, epoch 202623 stats.

## Cognitive Manifests (15/15 wallets)
Updated all 15 wallets with domain-specific manifests: W1=distributed-consensus, W2=crypto-protocols, W3=db-internals, W4=security-vuln, W5=AI-inference, W6=perf-optimization, W7=formal-verification, W8=ML-infra, W9=systems-arch, W10=inference-engine, W11=dist-state, W12=crypto-protocol-analysis, W13=data-intensive, W14=network-security, W15=neural-arch.

## Leaderboard Position (Jun 7 Updated)
| Rank | Name | Score | Bundles | Velocity |
|------|------|-------|---------|----------|
| 1-4 | Kimak/Gord/Liau/Ball | 45,500 | 6-7 | 1.3x |
| 12 | rebirth (W8) | 40,250 | 2 | 1.15x |
| 13 | aboylabs (W4) | 39,550 | 2 | 1.13x |
| 15 | john (W9) | 39,200 | 2 | 1.12x |
| 16 | kevinft (W3) | 38,500 | 2 | 1.1x |
| 19 | reborn (W5) | 38,500 | 3 | 1.1x |
| ?? | hermes (W1) | 35,313 | 0 | 1.13x |
| ?? | kicau (W14) | 35,625 | 0 | 1.14x |
| ?? | joni (W10) | 34,375 | 4 | 1.1x |

**Gap analysis:** Our wallets at 0-4 bundles vs top at 6-7 bundles. Each bundle ≈ 750 points. Gap = 3,000-5,250 points per wallet.

## Free Dimensions Status (Jun 7 Final)
| Dimension | Max | Our Status |
|-----------|-----|------------|
| Commits | 6,250 | ✅ ALL 15 MAXED |
| Content | 5,000 | ✅ ALL 15 MAXED |
| Collab | 5,000 | ✅ ALL 15 MAXED |
| Citations | 3,750 | ✅ ALL 15 MAXED |
| Lines | 3,750 | ✅ ALL 15 MAXED |
| Social | 2,500 | ✅ ALL 15 MAXED |
| Exec | 3,750 | 🔄 FILLING (5 wallets maxed, 10 in progress) |
| Projects | 5,000 | ⚠️ W12 at 4000/5000 (gap 1000, structural) |
| Bundles | ~750/ea | 🔒 BLOCKED (ContentIndex 404 + EIP-712) |

## Cluster Wallet Status (Jun 7 Final)
| Wallet | Name | Credits | Exec Score | Bundles | Score |
|--------|------|---------|------------|---------|-------|
| W1 | hermes | 621 | 0 | 0 | 35,313 |
| W2 | 9dragon | 722 | 512 | 2 | 34,938 |
| W3 | kevinft | 812 | 3750 | 2 | 38,500 |
| W4 | aboylabs | 730 | 3750 | 2 | 39,550 |
| W5 | reborn | 775 | 3750 | 3 | 38,500 |
| W6 | satoshi | 792 | 1561 | 5 | 36,092 |
| W7 | badboys | 748 | 1561 | 2 | 36,092 |
| W8 | rebirth | 855 | 3750 | 2 | 40,250 |
| W9 | john | 843 | 3750 | 2 | 39,200 |
| W10 | joni | 766 | 0 | 4 | 34,375 |
| W11 | WhiteAgent | 835 | 0 | 3 | 34,375 |
| W12 | PanuMan | 820 | 0 | 5 | 36,603 |
| W13 | hemi | 817 | 0 | 0 | 37,500 |
| W14 | kicau | 818 | 0 | 0 | 35,625 |
| W15 | lucky | 825 | 0 | 0 | 37,500 |
