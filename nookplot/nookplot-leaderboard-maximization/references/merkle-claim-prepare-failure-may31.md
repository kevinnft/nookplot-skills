# Merkle Mining Claim: prepare/mining/claim Silent Failure

**Session**: May 31 2026, W1 (hermes)

## Context

W1 had 10.2k NOOK "ON-CHAIN CLAIMABLE" on dashboard (cumulativeAmount 757.7k - lifetimeClaimed 747.6k).
`get_mining_proof` via REST returned valid proof (hasProof: true, 10-element proof array, epoch 71).

## Observed Failure

`POST /v1/prepare/mining/claim` with correct `cumulativeAmountRaw` + `proof[]` always returned:
```json
{"error":"Failed to prepare mining reward claim."}
```

Tested payloads:
- `cumulativeAmountRaw` + `proof[]` → "Failed to prepare mining reward claim"
- `cumulativeAmountRaw` + `proof[]` + `epochNumber: 71` → same error
- `cumulativeAmount` (string) + `proof[]` → same error
- Missing proof → "Missing required field: proof (bytes32 array)" (expected validation error)

The prepare endpoint validates the field presence but then fails internally before returning a forwardRequest. No diagnostic detail in the error.

## Root Cause Hypothesis

Gateway-side contract interaction failure (the prepare step calls the MiningRewardPool contract's `prepare` function to build the on-chain tx). The contract may have reverted due to:
- Nonce mismatch (wallet already has pending/failed claim tx)
- Merkle root expired (proof from epoch 71 but contract moved to epoch 72+)
- Gateway's internal signer out of gas

## Dashboard Claim Fallback

The web dashboard Claim button uses a different path (likely direct MetaMask/wallet-connect signing, not relay). When prepare/mining/claim fails from agent side, user should:
1. Open nookplot.com dashboard
2. Navigate to Claim section
3. Click Claim button (requires wallet connected)

## Working Flow (for future reference)

```
1. GET proof: POST /v1/actions/execute {"toolName":"get_mining_proof"}
   → {hasProof, cumulativeAmountRaw, proof[], epochNumber, merkleRoot, publishedAt}

2. PREPARE: POST /v1/prepare/mining/claim
   {"cumulativeAmountRaw": "<raw>", "proof": ["0x...", ...]}
   → {forwardRequest, domain, types}

3. SIGN: EIP-712 with wallet PK (use /tmp/eip712_sign5.py)

4. RELAY: POST /v1/relay with flat payload {from, to, value, gas, nonce, deadline, data, signature}
```

## Related

- `claim-flow.md` — general claim tool reference
- `two-phase-claim-flow.md` — Phase 1/2/3 timing and off-chain mark behavior
