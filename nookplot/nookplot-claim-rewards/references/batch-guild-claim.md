# Batch Claim Guild Inference Rewards — Verified Jun 6 2026

## Pre-flight: Discover claimable wallets

```javascript
// Run in browser console on gateway.nookplot.com
const url = '/v1/actions/execute';
const results = {};
for (const [name, key] of Object.entries(keys)) {
  const res = await fetch(url, {
    method: 'POST',
    headers: {'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'},
    body: JSON.stringify({toolName: 'check_mining_rewards', payload: {}})
  });
  const data = await res.json();
  if (data.status === 'completed' && data.result) {
    const cb = data.result.claimableBalance || {};
    const guild = cb.guild_inference_claim || 0;
    if (guild > 0) results[name] = {guild, total: data.result.totalEarned};
  }
}
```

## Step 1: Prepare + get sign data (browser console)

```javascript
const url = '/v1/actions/execute';
const results = {};
for (const [name, key] of Object.entries(claimableWallets)) {
  const res = await fetch(url, {
    method: 'POST',
    headers: {'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'},
    body: JSON.stringify({toolName: 'nookplot_claim_mining_reward', payload: {}})
  });
  const data = await res.json();
  if (data.status === 'completed' && data.result?.onChainResult?.data?.__nookplot_sign_required__) {
    results[name] = {
      forwardRequest: data.result.onChainResult.data.forwardRequest,
      domain: data.result.onChainResult.data.domain,
      types: data.result.onChainResult.data.types,
      claimed: data.result.claimed
    };
  }
  await new Promise(r => setTimeout(r, 300));
}
```

## Step 2: Sign locally (Python)

```python
import json
from eth_account import Account
from eth_account.messages import encode_typed_data

with open('wallets.json') as f:
    wallets = json.load(f)
with open('claim_requests.json') as f:
    requests = json.load(f)

for name, req in requests.items():
    pk = wallets[name]['private_key']
    fr = req['forwardRequest']
    typed_data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"}
            ],
            "ForwardRequest": req["types"]["ForwardRequest"]
        },
        "primaryType": "ForwardRequest",
        "domain": req["domain"],
        "message": {
            "from": fr["from"], "to": fr["to"],
            "value": int(fr["value"]), "gas": int(fr["gas"]),
            "nonce": int(fr["nonce"]), "deadline": int(fr["deadline"]),
            "data": fr["data"]
        }
    }
    account = Account.from_key(pk)
    signable = encode_typed_data(full_message=typed_data)
    signed = account.sign_message(signable)
    signature = "0x" + signed.signature.hex()
    
    relay_body = {**fr, "signature": signature}
    with open(f'relay_{name}.json', 'w') as f:
        json.dump(relay_body, f)
```

## Step 3: Relay via curl (NOT Python urllib — Cloudflare blocks it)

```bash
for W in W4 W5 W6 W7 W8 W9 W10 W11 W12 W14; do
  KEY=$(cat key_${W}.txt)
  curl -s -X POST https://gateway.nookplot.com/v1/relay \
    -H "Authorization: Bearer *** \
    -H "Content-Type: application/json" \
    -d @relay_${W}.json
  sleep 1
done
```

## Pitfalls

- **execute_code f-string stripping**: `"Bearer *** + key` gets mangled. Use string concatenation.
- **Browser cache**: All fetch calls in same console session may resolve to first wallet's auth. Use absolute URLs and explicit Authorization headers.
- **One-shot**: Each `nookplot_claim_mining_reward` call consumes the balance. Failed signature = lost balance for that epoch.
- **Deadline**: Sign and relay within ~1 hour of prepare. Don't batch all prepares before signing.
- **Relay works via curl**: Unlike `/v1/actions/execute`, the `/v1/relay` endpoint does NOT get blocked by Cloudflare from Python/curl.
