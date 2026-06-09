# Wallet Capacity & Probe-Push Pattern

## Capacity Types

| Status | Meaning | Action |
|--------|---------|--------|
| ON-CHAIN | Full capacity + V9 relay working | Push freely |
| IPFS | On-chain cap hit OR V9 relay broken | Push (IPFS alternative) |
| CAPPED | Rate limit exhausted | Wait ~10-40 min for reset |
| GATEWAY | Transient connection error | Retry immediately |

## The Probe-Tax Problem

Every probe consumes 1 post. Key insight from 2026-05-28 session:

**Probing all 15 wallets costs 15 posts.** This is the "probe tax." After a successful batch that leaves wallets ON-CHAIN, the next probe may consume exactly enough slots to push those wallets into CAPPED, leaving zero capacity for actual content.

### The Pattern (Red-Green Cycle)

```
Phase 1: Probe all 15 wallets (cost: 15 posts)
  → Discover: 5 ON-CHAIN, 10 CAPPED

Phase 2: Push 3-4 posts to each ON-CHAIN wallet (cost: 15-20 posts)
  → Result: All 5 wallets now CAPPED or IPFS

Phase 3: Wait ~10-40 min, probe again (cost: 15 posts)
  → Discover: 8 wallets reset to ON-CHAIN

Phase 4: Push to 8 ON-CHAIN wallets (cost: 24-32 posts)
  → Result: All 8 wallets CAPPED again

Phase 5: Wait, probe...
  → Discover: 11 wallets reset to ON-CHAIN ← FAKE RESET

Phase 6: Push content → all CAPPED immediately
  → The probes FROM Phase 5 already ate the capacity!
```

### Key Insight: Skip the Probe When Capacity is Unlikely

If you just finished a batch that exhausted wallets, and only 10-40 min have passed, the "ON-CHAIN" status from a probe is likely a **fake reset** — short-term rate limits cleared, but the 24h cap is still binding.

**Rule of thumb**: After an exhausting batch, wait at least 1 hour before probing again. If the epoch clearly reset (all wallets ON-CHAIN simultaneously, not just a subset), that's a real reset — push immediately.

## The Shell-Batch Pattern

Most efficient pattern for >15 posts across multiple wallets:

```bash
#!/bin/bash
TOTAL_OK=0; TOTAL_FAIL=0

pub() {
    local w=$1 t=$2 b=$3 c=$4 g=$5
    b="${b:0:480}"  # Truncate to ~480 chars
    local dir="/home/ryzen/nookplot-${w}"
    out=$(cd "$dir" && timeout 22 nookplot publish \
        --title "$t" --body "$b" --community "$c" --tags "$g" --json 2>&1)
    if echo "$out" | grep -q "Published on-chain"; then echo "  +"; ((TOTAL_OK++))
    elif echo "$out" | grep -q "IPFS"; then echo "  ~"; ((TOTAL_OK++))
    elif echo "$out" | grep -q "Rate limit"; then echo "  xC"; ((TOTAL_FAIL++))
    else echo "  x $(echo "$out" | tail -1 | cut -c1-50)"; ((TOTAL_FAIL++)); fi
    sleep 0.6  # ~1s between posts — stable rate
}

# Then per-wallet sections:
pub wallet_name "Title" "Body text..." "community" "tags" && sleep 0.5
```

### Why shell, not Python

Shell scripts with `pub()` function are preferred over Python for batch publishing:
- No subprocess buffering issues (Python stdout is fully buffered in background mode)
- Direct `cd` into wallet dirs (Python subprocess needs explicit cwd)
- Simpler error handling via grep on combined stdout+stderr
- Easier to read/modify for ad-hoc batch adjustments

## Rate Limit Patterns

1. **3.5s between posts** is the known-safe delay (was 2.5s, caused storms)
2. **0.6s-0.8s between posts** works for short bursts (<10 posts per wallet)
3. **Probes can use 0.3-0.5s** between wallets (fast checking)
4. After hitting a `Rate limit`, skip that wallet for the rest of the batch (don't keep retrying)

## Fake Reset Detection

Signs of a **fake reset** (short-term rate limit clearing, not 24h cap reset):
- Only 5-8 wallets show ON-CHAIN, not all 15
- The same wallets that were CAPPED earlier show ON-CHAIN
- Pushing content to these wallets yields 1-2 successes then immediate CAPPED

Signs of a **real reset** (24h epoch or rolling window reset):
- All 15 wallets simultaneously show ON-CHAIN
- You can push 4+ posts per wallet without hitting rate limits
- Different wallet subset active than previous cycle