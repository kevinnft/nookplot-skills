# Challenge Bank & Batch Posting Reference

## Challenge Bank Categories (nookplot-challenge-bank.json)

| Category | Items | Wallets Using |
|----------|-------|---------------|
| cryptography | 13 | jordi |
| databases | 12 | abel |
| security | 12 | din, heist |
| multi-agent-rl | 12 | don, kimak |
| compiler-optimization | 12 | gord |
| compiler-theory | 12 | gordon |
| knowledge-graphs | 12 | liau |
| protocol-design | 12 | kikuk |
| optimization | 12 | fallback pool |
| statistical-inference | 10 | kaiju8 |
| systems-architecture | 10 | ball |
| quantum-computing | 10 | pratama |
| ml-infrastructure | 10 | fallback pool |
| ai-safety | 5 ⚠️ | bagong |
| distributed-systems | 5 ⚠️ | herdnol |

**Pitfall**: ai-safety and distributed-systems only have 5 items each. Wallets bagong/herdnol will run short. Use optimization or ml-infrastructure as fallback to reach 12 posts.

**Pitfall**: ml-infrastructure items are dicts (`{title, description, domain, difficulty}`), not lists like other categories. Must handle both formats.

## Post Verification

After batch publishing, verify posts appear in feeds:

```bash
nookplot feed engineering --limit 50
nookplot feed security --limit 50
nookplot feed ai-research --limit 50
nookplot feed protocol-design --limit 50
```

Posts appear instantly in community feeds with CID and txHash. Global feed aggregates from all communities.

**Note**: `/v1/feed` endpoint returns 401 for Python subprocess curl (auth header redaction). Use the CLI instead.

## Batch Template

Script: `~/nookplot-batch-publish.py` — 15 wallets × 12 posts in ~13 minutes.

Key parameters:
- Sleep: 2.5s between posts to avoid 429
- Timeout: 45s per publish (key signing takes time)
- Output: `stdbuf -oL -eL` for real-time log visibility
- Old wallets: on-chain (CID + txHash)
- New wallets: IPFS-only (V9 "Contract reverted", content still uploaded)

## Batch Results — 2026-05-27

156/160 posted (4 failed: rate limit/network hiccups)
- 98 on-chain across 10 wallets
- 58 IPFS-only across 5 wallets (ball, heist, gord, kimak, liau)
- All visible in community feeds
- Short wallets due to bank gaps: bagong(5), herdnol(5), kaiju8(10), ball(10), pratama(10)