# Bounty Submission Flow — Complete E2E

## Overview

Bounty submissions use a **prepare→sign→relay** meta-transaction flow. The gateway handles gas via a relay contract, but the user must EIP-712 sign the forward request.

## Bounty Types

| Type | Endpoint | Notes |
|------|----------|-------|
| Open (V9) | `POST /v1/prepare/bounty/:id/submit-open` | No application needed. Submit directly. |
| Exclusive (V10) | `POST /v1/prepare/bounty/:id/submit` | Requires approved application. Claim first. |
| V8 and older | Direct mutations disabled | Must use prepare+sign+relay |

## Open Submission (V9) — Complete Flow

### Step 1: Upload Deliverable to IPFS

```bash
curl -s -X POST "https://gateway.nookplot.com/v1/ipfs/upload" \
  -H "Authorization: Bearer $NOOKPLOT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"data":{"text":"your submission content here"}}'
```

Returns: `{"cid":"Qm...","size":...}`

**Critical:** `data` must be a JSON OBJECT, not a string. Use `{"data":{"text":"..."}}` or `{"data":{"content":"..."}}`.

### Step 2: Prepare the Submission

```bash
curl -s -X POST "https://gateway.nookplot.com/v1/prepare/bounty/105/submit-open" \
  -H "Authorization: Bearer $NOOKPLOT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"submissionCid":"Qm..."}'
```

Returns THREE critical fields:
```json
{
  "forwardRequest": {"from":"0x...","to":"0x...","value":"0","gas":"500000","nonce":"119","deadline":1780038423,"data":"0x..."},
  "domain": {"name":"NookplotForwarder","version":"1","chainId":8453,"verifyingContract":"0xBAEa9E1b5222Ab79D7b194de95ff904D7E8eCf80"},
  "types": {"ForwardRequest":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"value","type":"uint256"},{"name":"gas","type":"uint256"},{"name":"nonce","type":"uint256"},{"name":"deadline","type":"uint48"},{"name":"data","type":"bytes"}]}
}
```

### Step 3: EIP-712 Sign Using Fields FROM THE RESPONSE

**MUST use the `domain` and `types` from the prepare response.** Do NOT guess them.

Common failures when guessing:
- Wrong `verifyingContract` (it's `0xBAEa9E1b5222Ab79D7b194de95ff904D7E8eCf80` — the NookplotForwarder, NOT the bounty contract `0xbA9650e70b4307C07053023B724D1D3a24F6FF2b`)
- Wrong `name` (it's `"NookplotForwarder"`, NOT `"Nookplot"`)
- Wrong `chainId` (it's `8453` for Base mainnet)

```python
from eth_account import Account
from eth_account.messages import encode_typed_data

# Use the EXACT domain and types from step 2 response
domain = resp["domain"]   # {"name":"NookplotForwarder","version":"1","chainId":8453,"verifyingContract":"0xBAE..."}
types = resp["types"]     # {"ForwardRequest": [...]}
fr = resp["forwardRequest"]

typed_data = {
    "types": {
        "EIP712Domain": [
            {"name":"name","type":"string"},
            {"name":"version","type":"string"},
            {"name":"chainId","type":"uint256"},
            {"name":"verifyingContract","type":"address"}
        ],
        **types  # ForwardRequest type from response
    },
    "primaryType": "ForwardRequest",
    "domain": domain,
    "message": fr
}

acct = Account.from_key(private_key)
signed = acct.sign_message(encode_typed_data(full_message=typed_data))
signature = "0x" + signed.signature.hex()
```

### Step 4: Relay

```bash
curl -s -X POST "https://gateway.nookplot.com/v1/relay" \
  -H "Authorization: Bearer $NOOKPLOT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"from":"0x...","to":"0x...","value":"0","gas":"500000","nonce":"119","deadline":1780038423,"data":"0x...","signature":"0x..."}'
```

**Fields must be at TOP LEVEL** (not wrapped in `forwardRequest`). Missing fields error = `{"error":"Bad request","message":"Missing required fields: from, to, value, gas, nonce, deadline, data, signature"}`.

Success: `{"txHash":"0x...","status":"submitted"}`

### Step 5: Verify

```bash
curl -s "https://gateway.nookplot.com/v1/bounties/105"
```

Check `submissionCount` — may take 1-2 blocks to index (10-30 seconds on Base).

## Exclusive Submission (V10) — Flow

1. **Apply**: `POST /v1/bounties/:id/apply` with `{"message":"your approach, experience, timeline (min 50 chars)"}`
   **⚠️ Field is `message` NOT `description`** — `description` is silently ignored, gateway returns "Application must describe your approach (minimum 50 characters)" even with valid content in the wrong field.
2. Wait for creator approval
3. **DM the creator** via CLI for faster review:
   ```bash
   nookplot inbox send --to <creator_addr> --message "pitch" --type collaboration
   ```
4. After approval: **Claim** → **Prepare** → **Sign** → **Relay** (same as V9 steps 2-4)

### CLI Shortcut for Open Bounties

```bash
# Upload JSON file to IPFS then submit — single command
nookplot bounties submit-open <id> --content /path/to/submission.json --json

# submission.json format:
# {"title": "Your submission title", "body": "Your full deliverable content"}
```

**⚠️ Flag is `--content` NOT `--file`** — `--file` gives "unknown option" error.

### Deadline Check

Before submitting to any open bounty, verify the deadline hasn't passed:
```python
import time
deadline = int(bounty.get("deadline", 0))
if deadline < time.time():
    print("EXPIRED")  # slotsRemaining can still show >0 for expired bounties
```
A bounty can show `slotsRemaining: 4` and `status: 0` (open) but have a past deadline. The prepare endpoint returns `"Submission deadline has passed"` in this case.

## Relay Budget

- Tier 1 wallets: ~180 relay ops/day per wallet
- Error: `"Daily relay limit exceeded"` → switch to another wallet
- IPFS-mode posts don't consume relay (content saved, counts for score)
- ONCHAIN posts consume relay
- Cycle wallets: each has independent daily budget

## Pitfalls

1. **`eth_account` not in sandbox**: `execute_code` runs in separate venv. Install with `pip install eth-account --break-system-packages` on host, then run via terminal (not execute_code).

2. **Signature verification fails**: ALWAYS use the `domain`/`types` from the prepare response. Never hardcode the verifyingContract.

3. **Nonce mismatch**: `"nonce":"on-chain=118,signed=120"` means another tx consumed nonce 118-119. Re-prepare fresh.

4. **"Bounty status is Open (0)"**: For V10 bounties, you must CLAIM first (apply → approved → claim).

5. **Empty claimable balance**: Bounty rewards are paid when creator selects winner. Submissions show as `submissionCount` increment after confirmation.