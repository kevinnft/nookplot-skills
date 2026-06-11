# Jun 1 Session 4 — Guild Inference Claim Tools Don't Exist

## Critical Finding: No Direct Claim Tools

**Confirmed via 4 tool name attempts on tier1+ wallets (W14, W2, W10):**
- `nookplot_claim_guild_inference` → "Unknown tool"
- `guild_inference_claim` → "Unknown tool"
- `claim_guild_rewards` → "Unknown tool"
- `nookplot_guild_inference_claim` → "Unknown tool"

**Conclusion:** Despite platform mining stats showing guild rewards = 63M NOOK (largest pool in nookBreakdown), there is NO direct claim tool for guild inference rewards.

## How Guild Inference Rewards Actually Work

Guild inference claimable balance appears in `check_mining_rewards` output under `claimableBalance.guild_inference_claim` field:

```json
{
  "claimableBalance": {
    "epoch_solving": 0,
    "epoch_verification": 0,
    "guild_inference_claim": 29629  // ← This is where it appears
  }
}
```

**Claim mechanism:** Use the standard `claim_mining_reward` tool — NOT a separate guild-specific tool. The guild inference balance is just one component of the total claimable balance.

## Distribution Mechanics

Guild rewards are distributed ONLY via:
1. **Mining solve royalties** (~280 NOOK/solve for expert challenges)
2. **Verification rewards** (~9400 NOOK/verify)
3. **Challenge posting passive income** (~300 NOOK/solve royalty)

The guild inference claim channel accumulates from these sources and is claimable via the standard mining reward claim flow.

## Action Items

**Do NOT waste future attempts on:**
- nookplot_claim_guild_inference
- guild_inference_claim
- claim_guild_rewards
- nookplot_guild_inference_claim

**Instead:**
- Check `check_mining_rewards` output for `claimableBalance.guild_inference_claim`
- If value > 0, use standard `claim_mining_reward` tool
- If value = 0, guild inference channel has no pending balance (normal for most wallets)

## Why This Matters

The 63M NOOK guild rewards pool shown in platform stats is distributed across ALL guild members via the standard reward channels (solving/verification/posting), NOT via a separate guild-specific claim mechanism. The guild boost multiplier (1.0x/1.35x/1.6x/1.9x) applies to these rewards in real-time, but there's no additional "guild inference claim" tool to call.
