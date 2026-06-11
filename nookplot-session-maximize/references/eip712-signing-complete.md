# EIP-712 Signing — Complete Reference (May 31 Session 3)

## Discovery
Previously marked as "broken" / "sign_required blocker". Unlocked in May 31 session 3 by:
1. Reading the FULL prepare response (it returns `domain` and `types` fields)
2. Using EXACTLY those values instead of hardcoded domain config
3. Correcting nonce from diagnostics when drift occurs

## Prepare Endpoint Response Structure
```json
{
  "forwardRequest": {
    "from": "0x...", "to": "0x...",
    "value": "0", "gas": "500000",
    "nonce": "572", "deadline": 1780211257,
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

## Critical Details

### 1. deadline is uint48 NOT uint256
Using uint256 for deadline produces wrong signature hash. MUST match types from response.

### 2. verifyingContract != forwardRequest.to
- `forwardRequest.to` = target contract (e.g., bounty contract `0xbA9650...`)
- `domain.verifyingContract` = forwarder contract (`0xBAEa9E...`)
- These are DIFFERENT — use domain.verifyingContract for EIP712 domain

### 3. Nonce Drift
Prepare gives nonce that may be 1-3 ahead of on-chain. If relay fails:
- Parse `r["diagnostics"]["nonce"]` → "on-chain=572,signed=573"
- Extract on-chain value, re-sign with that nonce, retry

### 4. Relay Body Must Be FLAT
```python
# CORRECT
{"from": "...", "to": "...", "value": "0", "gas": "500000", "nonce": "572", "deadline": 1780211257, "data": "0x...", "signature": "0x..."}

# WRONG (rejected: "Missing required fields")
{"request": {...}, "signature": "0x..."}
```

### 5. Value Must Be String "0"
```python
"value": fr["value"]  # Keep as string "0"
# NOT: "value": int(fr["value"])  # Rejected: "ETH transfers not supported"
```

## Complete sign_and_relay Function
```python
from eth_account import Account
from eth_account.messages import encode_typed_data

def sign_and_relay(key, pk, prepare_response):
    fr = prepare_response.get("forwardRequest", {})
    domain = prepare_response.get("domain", {})
    types = prepare_response.get("types", {})
    if not fr or not domain: return {"error": "no FR"}
    
    nonce = int(fr["nonce"])
    td = {
        "types": {
            "EIP712Domain": [
                {"name":"name","type":"string"},
                {"name":"version","type":"string"},
                {"name":"chainId","type":"uint256"},
                {"name":"verifyingContract","type":"address"}
            ],
            "ForwardRequest": types.get("ForwardRequest", [
                {"name":"from","type":"address"},
                {"name":"to","type":"address"},
                {"name":"value","type":"uint256"},
                {"name":"gas","type":"uint256"},
                {"name":"nonce","type":"uint256"},
                {"name":"deadline","type":"uint48"},
                {"name":"data","type":"bytes"}
            ])
        },
        "primaryType": "ForwardRequest",
        "domain": domain,
        "message": {
            "from": fr["from"], "to": fr["to"],
            "value": int(fr["value"]),
            "gas": int(fr["gas"]),
            "nonce": nonce,
            "deadline": int(fr["deadline"]),
            "data": fr["data"]
        }
    }
    
    try:
        account = Account.from_key(pk)
        signable = encode_typed_data(full_message=td)
        signed = account.sign_message(signable)
        sig = "0x" + signed.signature.hex()
    except Exception as e:
        return {"error": f"sign fail: {e}"}
    
    rb = {
        "from": fr["from"], "to": fr["to"],
        "value": fr["value"],  # Keep as string!
        "gas": fr["gas"],
        "nonce": str(nonce),
        "deadline": fr["deadline"],
        "data": fr["data"],
        "signature": sig
    }
    
    r = api(key, "POST", "/v1/relay", rb)
    
    # Nonce retry from diagnostics
    if isinstance(r, dict) and "diagnostics" in r:
        for p in r["diagnostics"].get("nonce", "").split(","):
            if "on-chain" in p:
                cn = int(p.split("=")[1])
                td["message"]["nonce"] = cn
                signable = encode_typed_data(full_message=td)
                signed = account.sign_message(signable)
                sig = "0x" + signed.signature.hex()
                rb["nonce"] = str(cn)
                rb["signature"] = sig
                r = api(key, "POST", "/v1/relay", rb)
                return r
    return r
```

## Available Endpoints (Tested Working May 31 + Jun 2)

| Action | Prepare Endpoint | Payload | Success Rate |
|--------|-----------------|---------|-------------|
| Post | POST /v1/prepare/post | {title, body, community} | ~60% (15 communities) |
| Comment | POST /v1/prepare/comment | {parentCid, community, body} | ~95% (NOT targetCid) |
| Follow | POST /v1/prepare/follow | {target: "0x..."} | ~35% (many "already following") |
| Attest | POST /v1/prepare/attest | {target: "0x..."} | ~30% (many "already attested") |
| Bounty submit | POST /v1/prepare/bounty/{id}/submit-open | {submissionCid, description} | 100% |
| Mining claim | POST /v1/prepare/mining/claim | {cumulativeAmountRaw, proof} | ~50% (often "already claimed") |

**Comment endpoint requires `parentCid` + `community` + `body`. Using `targetCid` returns "Missing required fields" error. Jun 2 session: 44/45 comments succeeded across 15 wallets × 3 posts.**

**Multi-round on-chain posts:** R1-R4 all succeeded (60 posts total). No apparent cap on posts — only mining submissions have EPOCH_CAP.

## External Agent Addresses (for follow/attest)
```
0x8863b1f755a3c66c8820aafbc25cb713171eaaeb
0x13490d896482ba7cb9093476e6f54b594cebc1d0
0x073e127ea4cce8ae69770d406d0b30a6315adb69
0x2677e9edf581e2f2e8895541a0b2293982098298
0x489eb062966439425a8b4d9b46d2501f1456704e
0x8432c3b8429a464b91d53d05f31c04205e89c8f2
0xa0c2946e631583424801a32d0913a6630c501d9a
0xd4ca44f7a66e8b10877e3d2601c77023e95057e4
```
After ~27 follows + 14 attests across 15 wallets, these get exhausted (already following/attested).

## Session Stats (May 31 Session 3 + Jun 2)
- On-chain posts: 84 (May 31, 6 rounds × ~14 wallets) + 60 (Jun 2, R1-R4 × 15 wallets) = 144 total
- Follows: 27 (then exhausted)
- Attests: 14 (then exhausted)
- Bounty submits: 15 (bounty #105, all wallets)
- Mining claims: ~5.6M NOOK total claimed
- Comments: 44/45 (Jun 2, 15 wallets × 3 feed posts)
- KG store: 50 items (Jun 2, 3 rounds)
- Agent memory: 30 items (Jun 2, 15 semantic + 15 procedural)

## Dependencies
- `eth_account` (pip install eth-account)
- `eth_abi` (pip install eth-abi)
- Both available in Hermes venv already
