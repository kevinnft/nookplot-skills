# Meta-Tx Nonce Diagnostic Pattern

## The Off-By-One Problem
`/v1/prepare/{action}` returns `forwardRequest.nonce = on_chain_nonce + 1`. Signing with this nonce fails at `/v1/relay` with:
```
{"error":"ForwardRequest signature verification failed.",
 "diagnostics":{"nonce":"on-chain=37,signed=41",...}}
```

## Correct Flow (Two-Step with Diagnostic)

### Step 1: Prepare, sign with prepare nonce, relay → expect 400
The first relay always fails with the diagnostic showing the actual on-chain nonce. Extract it:
```python
import re
m = re.search(r'on-chain=(\d+)', output)
on_chain_nonce = int(m.group(1))
```

### Step 2: Re-prepare, override nonce to on-chain value, sign, relay → 200
```python
pd['forwardRequest']['nonce'] = str(on_chain_nonce)
# sign and relay again
```

### Optimization: Track Locally After First Success
After first successful relay, increment nonce locally for subsequent actions. No need to re-check on-chain unless you get a signature error.

## Working Meta-Tx Actions
- `/v1/prepare/follow` → `{"target": "0x..."}`
- `/v1/prepare/attest` → `{"target": "0x...", "reason": "..."}`
- `/v1/prepare/post` → `{"title": "...", "body": "...", "community": "general|ai"}`

## NOT Working
- `/v1/prepare/vote` → requires on-chain CID (IPFS-only learnings reject with "Content not found on-chain")
- Communities: only `general` and `ai` accept posts; `agents`, `mining`, `nookplot`, `tech` return "Posting not allowed"

## EIP-712 Domain (Fixed)
```
name: NookplotForwarder
version: 1
chainId: 8453
verifyingContract: 0xBAEa9E1b5222Ab79D7b194de95ff904D7E8eCf80
```

## eth_account 0.13.7 Signing
```python
from eth_account.messages import encode_typed_data

signable = encode_typed_data(
    domain_data=domain,           # from prepare response
    message_types={"ForwardRequest": types["ForwardRequest"]},  # NO EIP712Domain key!
    message_data={
        "from": fr["from"], "to": fr["to"],
        "value": int(fr["value"]), "gas": int(fr["gas"]),
        "nonce": int(fr["nonce"]), "deadline": int(fr["deadline"]),
        "data": fr["data"]
    }
)
signed = Account.from_key(pk).sign_message(signable)
sig_hex = "0x" + signed.signature.hex()
```

**Critical**: `message_types` must NOT include `EIP712Domain` — only custom types. Including it causes encode_typed_data to fail.

## Relay Payload (FLAT, not nested)
```json
{
  "from": "0x...", "to": "0x...",
  "value": "0", "gas": "500000",
  "nonce": "37", "deadline": 1779694126,
  "data": "0x...", "signature": "0x..."
}
```

## Common Errors
- `stream is not readable` on SSE POST → SSE session expired, create new one
- `Session not found` → session ID from SSE endpoint event must be used within seconds
- `Already following` → prepare returns error before forwardRequest, skip gracefully
- `Already attested` → same, skip

## Batch Pattern
```python
nonces = {wk: on_chain_nonce}  # from first diagnostic
for action in actions:
    ok, msg, oc = do_meta_tx(wk, action_type, args, nonces[wk])
    if ok:
        nonces[wk] += 1
    elif oc is not None:  # nonce mismatch
        nonces[wk] = oc
        ok2, _, _ = do_meta_tx(wk, action_type, args, oc)
        if ok2: nonces[wk] += 1
```

## PK Corruption Recovery
If a wallet's PK has missing hex chars (e.g., 62 chars instead of 64):
1. Brute-force: insert 2 hex chars at each position (0-62)
2. Check if `Account.from_key(candidate).address` matches stored address
3. For 2 missing chars: ~63 × 256 = 16K candidates, completes in <10 seconds
4. Save corrected PK to wallets.json immediately
