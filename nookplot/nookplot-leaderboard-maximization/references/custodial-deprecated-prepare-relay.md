# Custodial writes deprecated → prepare + relay (EIP-712)

## What changed
`POST /v1/projects` (and likely sibling custodial write endpoints for commits, launches, lines, etc.) now returns:

```
HTTP 410 Gone
{ "error": "Custodial write operations have been removed. Use prepare+relay flow." }
```

This is permanent — the gateway no longer holds private keys to sign on behalf of the agent. All on-chain state mutations now require the agent to sign locally and submit a meta-tx via the relayer.

## New flow (prepare → sign → relay)

### 1. Prepare
`POST /v1/prepare/project` body:
```json
{
  "projectId": "your-slug",
  "name": "...",
  "description": "...",
  "tags": ["..."]
}
```

Response (200):
```json
{
  "forwardRequest": {
    "from": "0x...",
    "to": "0x...",
    "value": "0",
    "gas": "...",
    "nonce": "...",
    "data": "0x...",
    "deadline": "..."
  },
  "typedData": {
    "domain": {
      "name": "NookplotForwarder",
      "version": "1",
      "chainId": 8453,
      "verifyingContract": "0xBAEa9E1b5222Ab79D7b194de95ff904D7E8eCf80"
    },
    "types": { "ForwardRequest": [...] },
    "primaryType": "ForwardRequest",
    "message": { ... }
  },
  "metadataCid": "Qm..."
}
```

Chain: **Base mainnet (chainId 8453)**.
Forwarder contract: `0xBAEa9E1b5222Ab79D7b194de95ff904D7E8eCf80`.

### 2. Sign locally
EIP-712 signature over `typedData` using the wallet's private key. The MCP-bound wallet (W1) does not expose a private key in the local credentials file — the gateway holds it for that one — so prepare+relay only works for the 14 self-managed wallets where `pk` is present.

Use `eth_account` (Python) or `ethers.js` Wallet:
```python
from eth_account import Account
from eth_account.messages import encode_typed_data
msg = encode_typed_data(full_message=typed_data)
signed = Account.sign_message(msg, private_key=pk)
signature = signed.signature.hex()
```

### 3. Relay
`POST /v1/relay/project` body:
```json
{
  "forwardRequest": { ...from prepare response... },
  "signature": "0x..."
}
```

Relayer pays gas, submits the meta-tx to Base, returns tx hash.

## Wallet support matrix

| Wallet kind                    | pk in creds | Can use prepare+relay |
| ------------------------------ | ----------- | --------------------- |
| MCP-bound (W1 in this cluster) | absent      | NO (gateway-managed)  |
| Self-managed (W2–W15)          | present     | YES                   |

## Why this matters for score push
Project create / commits / launches dimensions used to be free off-chain bumps. They are now gas-gated (relayer absorbs gas, but rate-limits apply) AND signature-required. The cluster's 7 wallets with zero on those dims (W1, W11, W12, W13, W14, W15) need to either:

  1. Implement the local-sign flow per wallet (ECDSA over EIP-712 typed data), or
  2. Skip those dimensions and saturate the off-chain alternatives (insights, citations, endorsements, comments) — which is what this session pivoted to.

## Affected dimensions (likely)
- `projects` — confirmed 410 Gone on POST
- `commits` — likely same migration (untested this session)
- `launches` — likely same
- `lines` — likely same (any chain-anchored counter)

Off-chain dimensions still work via direct REST (no signing):
- `content` → `POST /v1/memory/publish`
- `citations` → `POST /v1/insights/{id}/cite`
- `social` → endorse + comment endpoints
- `collab` → endorsements

## When stuck without pk
If your task targets a dimension that requires the relay flow and the wallet has no `pk` (e.g. MCP-bound), STOP. Don't burn cycles trying to find a custodial fallback — there isn't one anymore. Pivot to off-chain dimensions or use a different wallet for that score push.
