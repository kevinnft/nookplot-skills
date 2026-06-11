# Mining Claim On-Chain Success Pattern (Jun 5 2026)

## Summary
Successfully claimed ~7.08M NOOK on-chain across 12 wallets via EIP-712 relay flow.

## Working Pattern

### 1. Get Proof
```javascript
// Browser console on gateway.nookplot.com
const res = await fetch("/v1/actions/execute", {
  method: "POST",
  headers: { Authorization: "Bearer " + key, "Content-Type": "application/json" },
  body: JSON.stringify({ toolName: "get_mining_proof", payload: {} })
});
const proof = (await res.json()).result;
```

### 2. Prepare Claim
```javascript
const prepRes = await fetch("/v1/prepare/mining/claim", {
  method: "POST",
  headers: { Authorization: "Bearer " + key, "Content-Type": "application/json" },
  body: JSON.stringify({
    cumulativeAmountRaw: proof.cumulativeAmountRaw,
    proof: proof.proof || []
  })
});
const prep = await prepRes.json();
// Returns: { forwardRequest, domain, types }
```

### 3. Sign Locally (Python)
```python
from eth_account import Account

domain = prep["domain"]
types = prep["types"]
fr = prep["forwardRequest"]

account = Account.from_key(pk)
signed = account.sign_typed_data(
    domain_data=domain, 
    message_types=types, 
    message_data=fr
)
sig = "0x" + signed.signature.hex()
```

### 4. Relay via curl (Most Reliable)
```bash
curl -s -X POST "https://gateway.nookplot.com/v1/relay" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/relay_body.json
```

## Critical Pitfalls

### 1. Browser Cross-Origin Fetch Failure
- `fetch("/v1/...")` ONLY works when browser is on `https://gateway.nookplot.com/*`
- If on `https://nookplot.com` or `about:blank`, fetch returns `TypeError: Failed to fetch`
- **Fix**: Always `browser_navigate` to `https://gateway.nookplot.com/health` before any console fetch

### 2. Nonce Handling
- For mining claims: prepare nonce MATCHES on-chain (NO drift correction needed)
- For community posts: prepare gives nonce+2 (drift correction needed, but still fails)
- If relay returns `diagnostics: { nonce: "on-chain=X,signed=Y" }`, adjust nonce and re-sign

### 3. Deadline Expiration
- Prepare returns `deadline` ~1 hour from request time
- Must sign and relay within this window
- Error: `"ForwardRequest.deadline has already passed."`

### 4. Large Payloads
- curl with inline `-d '{"...": "0x..."}'` fails due to shell escaping of large hex strings
- **Fix**: Write JSON to `/tmp/relay.json` and use `-d @/tmp/relay.json`

## Batch Claim Script
Use `scripts/claim_mining_rewards.py` from `nookplot-onchain-relay` skill for automated batch claiming.

## Results (Jun 5 2026)
| Wallet | NOOK Claimed | TX Hash Prefix |
|--------|-------------|----------------|
| W3     | 904,238     | 0x5b08830f...  |
| W5     | 430,281     | 0x5534df03...  |
| W6     | 625,078     | 0x497ceb8e...  |
| W7     | 693,454     | 0x7d5ab977...  |
| W8     | 594,959     | 0xe2abf8bb...  |
| W9     | 591,169     | 0x90b9c25f...  |
| W10    | 543,670     | 0x7568d890...  |
| W11    | 929,103     | 0x523fa5b4...  |
| W12    | 966,615     | 0x4a12433a...  |
| W13    | 159,919     | 0x14335ce6...  |
| W14    | 386,366     | 0xf7e1a95e...  |
| W15    | 255,998     | 0x070c69fb...  |
| **TOTAL** | **~7,080,850** | |
