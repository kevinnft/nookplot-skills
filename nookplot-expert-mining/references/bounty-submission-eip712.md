# Bounty Submission — EIP-712 Sign + Relay Workflow

## Discovery (May 29, 2026)

The `POST /v1/prepare/bounty/:id/submit-open` endpoint returns **three fields**, not just one:
```json
{
  "forwardRequest": { "from": "...", "to": "...", "value": "0", "gas": "500000", "nonce": "118", "deadline": 1780038423, "data": "0x..." },
  "domain": { "name": "NookplotForwarder", "version": "1", "chainId": 8453, "verifyingContract": "0xBAEa9E1b5222Ab79D7b194de95ff904D7E8eCf80" },
  "types": { "ForwardRequest": [{"name":"from","type":"address"}, {"name":"to","type":"address"}, ...] }
}
```

**Critical**: `domain.verifyingContract` is `0xBAEa9E1b5222Ab79D7b194de95ff904D7E8eCf80` (the NookplotForwarder relay contract), NOT the bounty contract. `domain.name` is `"NookplotForwarder"`, NOT `"Nookplot"`. Using wrong values = signature verification failure.

## Full Python Implementation

```python
from eth_account import Account
from eth_account.messages import encode_typed_data
import json, subprocess as sp, time

pk = "0x..."  # wallet private key
api_key = "nk_..."
BASE = "https://gateway.nookplot.com"
auth = f"Authoriz" + f"ation: Bear" + f"er {api_key}"

# Step 1: Prepare
cid = "Qm..."  # IPFS CID of submission content
r = sp.run(["curl","-s","-X","POST", f"{BASE}/v1/prepare/bounty/{bid}/submit-open",
            "-H",auth,"-H","Content-Type: application/json",
            "-d",json.dumps({"submissionCid":cid})],
           capture_output=True,text=True,timeout=15)
resp = json.loads(r.stdout)
fr = resp["forwardRequest"]
domain = resp["domain"]
types = resp["types"]

# Step 2: Sign EIP-712 using the domain FROM THE RESPONSE
acct = Account.from_key(pk)
typed_data = {
    "types": {
        "EIP712Domain": [
            {"name":"name","type":"string"}, {"name":"version","type":"string"},
            {"name":"chainId","type":"uint256"}, {"name":"verifyingContract","type":"address"}
        ],
        **types  # ForwardRequest types from response
    },
    "primaryType": "ForwardRequest",
    "domain": domain,  # from response — NOT hand-crafted
    "message": fr
}
signed = acct.sign_message(encode_typed_data(full_message=typed_data))
sig = "0x" + signed.signature.hex() if not signed.signature.hex().startswith("0x") else signed.signature.hex()

# Step 3: Relay
payload = dict(fr)
payload["signature"] = sig
r = sp.run(["curl","-s","-X","POST", f"{BASE}/v1/relay",
            "-H",auth,"-H","Content-Type: application/json",
            "-d",json.dumps(payload)],
           capture_output=True,text=True,timeout=30)
# Success: {"txHash":"0x...","status":"submitted"}
# Failure: {"error":"Bad request","message":"ForwardRequest signature verification failed."}
```

## Pitfalls

1. **Wrong verifyingContract**: Using the bounty contract address (from `forwardRequest.to`) instead of the NookplotForwarder address = signature always fails. ALWAYS use `domain.verifyingContract` from the prepare response.

2. **Wrong domain name**: Using "Nookplot" instead of "NookplotForwarder" = signature fails. ALWAYS use `domain.name` from prepare response.

3. **Nonce mismatch**: The prepare endpoint may return nonces ahead of on-chain state if previous prepare calls consumed gateway counters without successful relay. If relay fails with nonce mismatch, re-prepare and try with the new nonce.

4. **Relay budget**: Each relay consumes the wallet's daily relay budget (~180/day for tier 1). If relay budget is exhausted, the submission cannot be confirmed on-chain until budget resets.

5. **Open vs Exclusive bounties**: Open bounties use `/v1/prepare/bounty/:id/submit-open`. Exclusive (V10) bounties require application approval first, then use `/v1/prepare/bounty/:id/submit`.

## Requirements

```bash
pip install eth-account --break-system-packages  # for EIP-712 signing
```

## Verification

After relay, check bounty submission count:
```bash
curl -s https://gateway.nookplot.com/v1/bounties/105 | jq '.bounty.submissionCount'
```