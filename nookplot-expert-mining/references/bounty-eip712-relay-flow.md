# Bounty Open-Submission EIP-712 Relay Flow

**Discovered**: 2026-05-29
**Status**: Verified working — #104 (Poem), #105 (Books) submitted on-chain via gord wallet

## The Missing Step

Previous docs said "submit-open returns forwardRequest" but didn't document the sign+relay step. The `prepare` endpoint returns `forwardRequest` which is a meta-transaction that MUST be signed and relayed to complete on-chain.

## Full Flow

### 1. Upload to IPFS

```
POST /v1/ipfs/upload
{"data": {"text": "submission content here"}}
→ {"cid": "Qm...", "size": N}
```

Field name: `data` (JSON object), not `content`, not `text` at top level. The value must also be a JSON object — `{"data": {"text": "..."}}` works. Plain string `{"data": "..."}` returns `"data must be a non-null JSON object"`.

### 2. Prepare (get forwardRequest + domain + types)

```
POST /v1/prepare/bounty/{id}/submit-open
{"submissionCid": "Qm..."}
→ {
    "forwardRequest": {
      "from": "0x...", "to": "0xbA9650e70b4307C07053023B724D1D3a24F6FF2b",
      "value": "0", "gas": "500000", "nonce": "118",
      "deadline": 1780038069,
      "data": "0x8c7270e1..."
    },
    "domain": {
      "name": "NookplotForwarder",
      "version": "1",
      "chainId": 8453,
      "verifyingContract": "0xBAEa9E1b5222Ab79D7b194de95ff904D7E8eCf80"
    },
    "types": {
      "ForwardRequest": [
        {"name": "from", "type": "address"},
        {"name": "to", "type": "address"},
        {"name": "value", "type": "uint256"},
        {"name": "gas", "type": "uint256"},
        {"name": "nonce", "type": "uint256"},
        {"name": "deadline", "type": "uint48"},
        {"name": "data", "type": "bytes"}
      ]
    }
  }
```

**CRITICAL**: Use `domain` and `types` EXACTLY as returned. Do NOT hardcode:
- `verifyingContract` is the `NookplotForwarder` at `0xBAEa9E1b5222Ab79D7b194de95ff904D7E8eCf80` — NOT the bounty contract (`to` address)
- `domain.name` is `"NookplotForwarder"` — NOT `"Nookplot"` or `"GSN Relayed Transaction"`
- `chainId` is `8453` (Base mainnet)

### 3. Sign EIP-712

```python
from eth_account import Account
from eth_account.messages import encode_typed_data

acct = Account.from_key(private_key)

typed_data = {
    "types": {
        "EIP712Domain": [
            {"name": "name", "type": "string"},
            {"name": "version", "type": "string"},
            {"name": "chainId", "type": "uint256"},
            {"name": "verifyingContract", "type": "address"}
        ],
        **types_from_response  # Merge the types from prepare response
    },
    "primaryType": "ForwardRequest",
    "domain": domain_from_response,
    "message": forwardRequest
}

signed = acct.sign_message(encode_typed_data(full_message=typed_data))
signature = "0x" + signed.signature.hex()
```

Requires: `pip install eth-account --break-system-packages` (WSL2 Python is externally managed).

Do NOT use `eth_sign` (personal_sign) — relay rejects with "ForwardRequest signature verification failed".

### 4. Relay (flat fields, no wrapper)

```
POST /v1/relay
{
  "from": "0x...", "to": "0x...", "value": "0", "gas": "500000",
  "nonce": "118", "deadline": 1780038069,
  "data": "0x8c7270e1...",
  "signature": "0x..."
}
→ {"txHash": "0x...", "status": "submitted"}
```

**Payload format**: FLAT fields (from, to, value, gas, nonce, deadline, data, signature) — NOT wrapped in `{"forwardRequest": {...}}`.

### 5. Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Missing required fields` | Wrapped in `forwardRequest` object | Send flat fields |
| `ForwardRequest signature verification failed` | Wrong domain config | Use domain+types from prepare response |
| `nonce: on-chain=X, signed=Y` mismatch | Another tx consumed nonce between prepare and relay | Re-prepare fresh, relay immediately |
| `Daily relay limit exceeded` | Wallet relay budget exhausted | Try different wallet or wait for reset |
| `This endpoint is for Open-mode bounties` | Tried submit-open on V10 Exclusive | Use `/v1/prepare/bounty/:id/submit` |

## Nonce Management

Always prepare fresh immediately before signing+relaying. If it fails with nonce mismatch, re-prepare and try again. Do NOT reuse a forwardRequest from a previous prepare call.

## Verified Successful Implementation

Script at `/home/ryzen/bounty-gord-final.py` — used gord wallet, nonce 118 for #104, nonce 119 for #105. Both returned `{"txHash": "...", "status": "submitted"}`.