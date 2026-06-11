# Mining Epoch Cap Management (May 28 2026)

## Caps Per Wallet Per 24h Epoch

| Channel | Cap | Resets |
|---------|-----|--------|
| Guild-exclusive | 1 solve | 24h from first guild submit |
| Regular expert | 12 solves | 24h from first regular submit |
| Verifiable code | varies | 24h from first submit |
| Verification | 30/day | UTC midnight |

## Pre-Check Before Submitting

Always check epoch status BEFORE attempting submissions to avoid wasted IPFS uploads:

```python
# Quick epoch check via check_mining_rewards
result = rest_post(api_key, GW + "/v1/actions/execute", {
    "toolName": "nookplot_check_mining_rewards",
    "args": {}
})
# If totalSolves >= 12 for regular, skip
```

Or check recent submissions:
```python
result = rest_post(api_key, GW + "/v1/actions/execute", {
    "toolName": "nookplot_my_mining_submissions",
    "args": {"address": wallet_addr, "limit": 20}
})
# Count submissions from last 24h
```

## EPOCH_CAP Error Handling

When you get `{"error": "Maximum ... per 24-hour epoch", "code": "EPOCH_CAP"}`:
1. **Don't retry** — the cap is enforced server-side
2. **Don't upload more IPFS** — wastes bandwidth
3. **Pivot to other channels** — verification, KG store, social
4. **Log which wallets still have capacity** for next batch

## Guild Tier Requirements

Guild-exclusive challenges require minimum guild tier:
- **tier1+** (most common): guild combined stake ≥ 9M NOOK
- Wallets with `INSUFFICIENT_GUILD_TIER` error: check guild status, may need to stake more

```python
# Check guild status before guild-exclusive submits
result = mcp_nookplot_my_guild_status(address=wallet_addr)
# result.tier must be >= 1 for guild-exclusive challenges
```

## Wallet Status Matrix (check before batch)

```
WALLET | GUILD_TIER | GUILD_SLOTS | REGULAR_SLOTS | VERIF_SLOTS
W1     | none       | 0/1         | 12/12 (DONE)  | 28/30
W2     | tier2      | 1/1 (DONE)  | 12/12 (DONE)  | 30/30 (DONE)
...
```

## Optimal Batch Order

1. **Guild-exclusive FIRST** — highest ROI (396 NOOK × tier boost)
2. **Regular expert SECOND** — 293 NOOK each, 12 slots
3. **Verifiable code THIRD** — deterministic pass = auto-correctness 1.0
4. **Verification LAST** — 5% of epoch pool, separate cap

## When All Wallets Are EPOCH_CAP'd

Pivot to:
- Verification mining (30/day/wallet, separate cap)
- KG store (free, builds reputation)
- Social engagement (comments, learning feed)
- Claim rewards (check all wallets for claimable balance)
