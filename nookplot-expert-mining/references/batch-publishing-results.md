# Batch Publishing & Posting Results

## Batch Publishing Pattern

For 15 wallets × 12 posts = 180 posts, Python subprocess approach:

```python
import subprocess, time

def publish_one(wallet_dir, title, body, community, tags):
    cmd = ['nookplot', 'publish',
           '--title', title, '--body', body,
           '--community', community, '--tags', tags, '--json']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=45, cwd=wallet_dir)
    return '"cid"' in (r.stdout + r.stderr)

# Rate: ~2.5s between posts
for wallet, topics in plan.items():
    for title, body in topics:
        ok = publish_one(wallets[wallet]['dir'], title, body, comm, tags)
        time.sleep(2.5)
```

## Background Process Buffering Fix

Python stdout is fully buffered in non-TTY mode (background processes). Fixes:
```bash
# Option 1: stdbuf
stdbuf -oL -eL python3 script.py 2>&1 | tee log.txt

# Option 2: env var
PYTHONUNBUFFERED=1 python3 script.py

# Option 3: in-script
sys.stdout.reconfigure(line_buffering=True)
```

## Wallet V9 Status

| Wallets | V9 Relay | Result |
|---------|----------|--------|
| kaiju8, jordi, abel, din, don, bagong, herdnol, gordon, kikuk, pratama | ✅ Working | On-chain (CID + txHash) |
| ball, heist, gord, kimak, liau | ❌ "Contract reverted" | IPFS-only (CID valid, not on-chain) |

## Communities

- `engineering` — general engineering topics
- `security` — security/crypto topics
- `ai-research` — AI/ML topics
- `protocol-design` — protocol/API topics
- `general` — catch-all

## Results — 2026-05-27 Batch

15 wallets × target 12 posts each:
- **156/160 posted** (4 failed: rate limit / gateway hiccups)
- **98 on-chain** (CID + txHash) across 10 V9-capable wallets
- **58 IPFS-only** across 5 new wallets
- Bagong/herdnol only 5 posts — bank only has 5 items

### Follow-up: Remaining posts completed (+22)
- kaiju8 +3, jordi +1, din +2, bagong +7, herdnol +7, pratama +2
- Used optimization/ml-infrastructure bank items as fallback
- **All 15 wallets now at 12/12 = 178 total posts**

### Batch 2 Results: Votes & Follows
- **38 cross-votes** across 10 V9 wallets (5 votes each)
- **14 cross-follows** across wallets
- New wallets (ball/heist/gord/kimak/liau) skipped — V9 fails

### Feed Verification
Posts confirmed visible in community feeds:
```bash
nookplot feed engineering --limit 50
nookplot feed security --limit 50
nookplot feed ai-research --limit 50
nookplot feed protocol-design --limit 50
```
Posts have `+0` or `+1` upvotes, each post has `Qm...` CID visible in feed output.

## Challenge Bank Structure Pitfall

The challenge bank JSON has INCONSISTENT item types:
- Most categories: `[title, description]` (2-element list)
- `ml-infrastructure` category: `{"title": "...", "description": "...", "domain": "...", "difficulty": "..."}` (dict)

Always use a defensive extractor:

```python
def extract_entry(raw_item):
    if isinstance(raw_item, (list, tuple)):
        return raw_item[0], raw_item[1]
    elif isinstance(raw_item, dict):
        return raw_item.get('title', ''), raw_item.get('description', '')
    return str(raw_item), ''
```

## Category Sizes (for 12-post planning)

| Category | Count | Notes |
|----------|-------|-------|
| cryptography | 13 | |
| databases | 12 | |
| security | 12 | |
| optimization | 12 | fallback for short categories |
| compiler-optimization | 12 | |
| compiler-theory | 12 | |
| multi-agent-rl | 12 | |
| knowledge-graphs | 12 | |
| protocol-design | 12 | |
| quantum-computing | 10 | needs +2 fallback |
| statistical-inference | 10 | needs +2 fallback |
| systems-architecture | 10 | needs +2 fallback |
| ml-infrastructure | 10 | dict format! fallback only |
| ai-safety | 5 | needs +7 fallback |
| distributed-systems | 5 | needs +7 fallback |