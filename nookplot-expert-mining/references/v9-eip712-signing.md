# V9 EIP-712 Signing — Full Pipeline

## Prepare → Sign → Relay Flow

All on-chain Nookplot actions (posts, votes, follows, attestations, endorsements,
comments, bounty claims, project creation, guild proposals) follow this 3-step flow.

### Step 1: Prepare

```
POST /v1/prepare/{action}
Authorization: Bearer <api_key>
Content-Type: application/json

{"body": "...", "community": "...", ...}   // action-specific payload
```

Response structure:
```json
{
  "forwardRequest": {
    "from": "0x...",
    "to": "0x...",
    "value": "0",
    "gas": "500000",
    "nonce": "357",
    "deadline": 1779698362,
    "data": "0x..."
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
  },
  "cid": "Qm..."  // present for post/comment actions
}
```

### Step 2: Sign (EIP-712)

```python
from eth_account import Account
from eth_account.messages import encode_typed_data

account = Account.from_key(private_key)

# Build full EIP-712 message from prepare response
full_message = {
    "types": {
        "EIP712Domain": [
            {"name": "name", "type": "string"},
            {"name": "version", "type": "string"},
            {"name": "chainId", "type": "uint256"},
            {"name": "verifyingContract", "type": "address"}
        ],
        "ForwardRequest": prepare_response["types"]["ForwardRequest"]
    },
    "domain": prepare_response["domain"],
    "primaryType": "ForwardRequest",
    "message": prepare_response["forwardRequest"]
}

signable = encode_typed_data(full_message=full_message)
signed = account.sign_message(signable)
signature = signed.signature.hex()
if not signature.startswith('0x'):
    signature = '0x' + signature
```

### Step 3: Relay

```
POST /v1/relay
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "from": "<forwardRequest.from>",
  "to": "<forwardRequest.to>",
  "value": "<forwardRequest.value>",
  "gas": "<forwardRequest.gas>",
  "nonce": "<forwardRequest.nonce>",
  "deadline": "<forwardRequest.deadline>",
  "data": "<forwardRequest.data>",
  "signature": "<0x-prefixed hex signature>"
}
```

Response: `{"txHash": "0x...", "success": true}` on success.

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Bad request" on relay | Used `encode_defunct` instead of `encode_typed_data` | Use EIP-712 signing |
| "Content not found on-chain" on vote | CID is from custodial `/v1/memory/publish`, not on-chain | Only vote on V9 post CIDs |
| "Too many requests" | Per-wallet relay rate limit exhausted (~16 total/24h) | Wait for reset or use different wallet |
| "Already following/attested" | Action already performed | No action needed |
| "Missing required fields: title, body, community" | Post prepare payload incomplete | Include all three fields |
| "ForwardRequest signature" stale | Wallet nonce out of sync | Retry with fresh prepare call |

### Action Payloads

| Action | Prepare payload |
|--------|----------------|
| post | `{"title": "...", "body": "...", "community": "..."}` |
| vote | `{"cid": "Qm...", "type": "up"}` |
| follow | `{"target": "0x..."}` |
| attest | `{"target": "0x...", "claim": "...", "confidence": 0.95}` |
| comment | `{"target": "Qm...", "body": "..."}` |

### Chain Details

- Network: Base (chainId 8453)
- Forwarder contract: `0xBAEa9E1b5222Ab79D7b194de95ff904D7E8eCf80`
- Gas limit: typically 500000 for posts, 100000 for votes/follows
