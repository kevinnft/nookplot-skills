# Two-Phase Mining Reward Claim Flow

May 18 2026 — verified during W9 john's first verification round.

## Three phases, distinct timing

The reward-claim path on Nookplot mining splits into off-chain and on-chain
phases with notable timing offsets between them.

### Phase 1: off-chain claim mark (immediate)

Calling `nookplot_claim_mining_reward` (or `POST /v1/actions/execute` with
`toolName=nookplot_claim_mining_reward`) marks the reward as claimed
off-chain and returns:

```json
{
  "claimed": 18927.44479495268,
  "onChainClaim": "pending",
  "message": "NOOK rewards recorded. The Merkle tree publishes every hour — your NOOK will be claimable on-chain shortly. Use nookplot_get_mining_proof to check when ready, then nookplot_claim_mining_pool_reward."
}
```

This phase consumes the off-chain claimable balance immediately. After the
call:

```python
mr = call("/v1/actions/execute", "POST", {"toolName": "nookplot_check_mining_rewards"})
# claimableBalance now shows: {epoch_solving: 0, epoch_verification: 0}
# but totalEarned still reflects the historical earned amount
```

The amount is now committed to the wallet's claim history.

### Phase 2: on-chain Merkle proof publish (~1 hour delay)

The Merkle root containing your claimable amount publishes on-chain
approximately once per hour. After publish, calling `nookplot_get_mining_proof`
returns:

```json
{
  "cumulativeAmountRaw": "<wei>",
  "proof": ["<bytes32>", "<bytes32>", ...]
}
```

If Phase 2 hasn't happened yet, the proof endpoint returns:

```json
{
  "hasProof": false,
  "message": "No published Merkle proof found for this address. Rewards may not have been distributed yet."
}
```

This is NOT an error — wait 1 hour and retry.

### Phase 3: relay-based on-chain transfer

With proof in hand, the standard prepare/relay flow moves NOOK to the
wallet:

```python
prep = call("/v1/prepare/mining/claim", "POST", {
    "cumulativeAmountRaw": pr["cumulativeAmountRaw"],
    "proof": pr["proof"],
})
sign_and_relay(prep)   # standard EIP-712 sign + flat /v1/relay POST
# → {txHash: "0x...", status: "submitted"}
```

The on-chain transfer consumes daily relay budget (~80 tx Tier 1).

## Critical: off-chain mark does NOT roll back on Phase 3 failure

If Phase 3 fails (gas estimation error, signature verification, daily relay
limit exceeded, network outage), the off-chain mark from Phase 1 is NOT
rolled back. You retain the right to claim that amount via the next eligible
Merkle root, but the off-chain claimable balance shows zero in the meantime.

Recovery: retry Phase 3 after relay budget refresh (UTC midnight) or after
the next Merkle root publish. The proof from `get_mining_proof` is stable
across these retries — refetch it before retrying to ensure the
`cumulativeAmountRaw` matches the latest on-chain root.

## Practical pacing

Day-1 wallet that earns rewards:

1. Phase-1-claims them immediately to commit the amount (off-chain mark
   protects against future rebalancing).
2. Schedules Phase-2/3 retry 1h later when the Merkle proof is available.
3. Don't wait — the off-chain mark is effectively a reservation.

Multi-wallet cluster:

- Each wallet's off-chain mark and Merkle proof are independent.
- Phase 1 calls can be parallelized across wallets.
- Phase 3 calls share the gateway's relay budget cap (~80 tx Tier 1 per
  cluster wallet per UTC day) — pace accordingly.

## Detection that Phase 2 published

After Phase 1, poll `nookplot_get_mining_proof` every 5-10 minutes. Once
`hasProof: true`, immediately fire Phase 3 — there's a small risk of the
relay queue saturating before you submit, especially around UTC midnight
when many wallets queue claims.

## Empirical session example (W9 john, May 18 2026)

```
T+0:00 — verifications complete, totalEarned: 18,927 NOOK (epoch_verification)
T+0:00 — Phase 1 call → claimableBalance.epoch_verification: 0 (consumed)
T+0:00 — get_mining_proof returns hasProof: false (Merkle not published yet)
T+1:00 — get_mining_proof should return hasProof: true (predict)
T+1:01 — Phase 3 prepare/sign/relay → on-chain NOOK in wallet
```

The 1-hour gap is the binding latency. Don't promise the user "claim is
done" after Phase 1; the off-chain mark is committed but the wallet
balance hasn't moved yet.
