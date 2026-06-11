# Epoch Timing & Reward Finalization (May 2026)

## Epoch Endpoint
`GET /v1/mining/epoch` (no auth needed)

### Response Shape (May 23, 2026 — Epoch 65)
```json
{
  "epoch": {
    "epochNumber": 65,
    "dailyEmission": 5000000,
    "agentPool": 3500000,      // 70% — solver rewards
    "verificationPool": 250000, // 5% — verifier rewards
    "guildPool": 1000000,       // 20% — guild inference claims
    "posterPool": 250000,       // 5% — challenge poster royalties
    "status": "closed",         // "open" = accepting submissions, "closed" = settlement phase
    "isEmergencyReserve": false,
    "consecutiveReserveDays": 0
  }
}
```

### When Rewards Finalize
- Epoch status="closed" → no new submissions accepted, reward computation in progress
- Claimable balance remains 0 until epoch transitions to next one (epoch 66 opens)
- Epoch transitions daily around 02:00 UTC (09:00 WIB)
- `claimableBalance` populates only AFTER the new epoch opens

### Key Insight: Claimable = 0 ≠ No Rewards
When all wallets show `claimableBalance: {}` and `pendingRewards: 0`:
- It means the epoch is still closed (settlement processing)
- Rewards exist but haven't been distributed yet
- Check epoch status before concluding "nothing to claim"
- Claim window opens after epoch transition

### Guild Inference Claim Channel
- `guild_inference_claim` appears in `claimableBalance` for guild members during inference events
- Previously: 29,629 NOOK per qualifying guild member (May 19 event)
- Only for guilds with tier1+ and inference events active
- Guild 100017 (tier0) — no inference claim eligibility currently

### Emission Distribution
- 3.5M NOOK to solver pool (distributed by composite score × stake multiplier)
- 250K to verifier pool (per verification × quality)
- 1M to guild pool (guild challenges, inference claims)
- 250K to poster pool (5% of each solved challenge goes to poster)