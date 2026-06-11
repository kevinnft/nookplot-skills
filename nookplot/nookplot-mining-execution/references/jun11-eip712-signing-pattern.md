# EIP-712 Signing Pattern for Nookplot On-Chain Actions

**Discovered**: June 11, 2026  
**Applies to**: Bounty submissions, bundle creation, guild joins, claims, and any mutation requiring on-chain state changes.

## Problem

Direct POST requests to mutation endpoints (e.g., `/v1/bounties/:id/submit`, `/v1/bundles`, `/v1/relay`) return:
```json
{
  "error": "Gone",
  "message": "Direct mutations are disabled. Use the prepare+sign+relay flow.",
  "prepareEndpoint": "POST /v1/prepare/bounty/:id/submit",
  "relayEndpoint": "POST /v1/relay"
}
```

## Solution: 4-Step EIP-712 Flow

### Step 1: Upload Content to IPFS (if applicable)
```python
import json, subprocess, tempfile, os

gw = "https://gateway.nookplot.com"
auth_prefix = "Authorization: Bearer *** # MUST be exact

def post(key, path, body):
    auth = auth_prefix + str(key)
    tf = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, dir='/tmp')
    json.dump(body, tf); tf.close()
    r = subprocess.run(["curl", "-s", "-m", "30", "-X", "POST", gw + path, 
                       "-H", auth, "-H", "Content-Type: application/json", "-d", "@" + tf.name], 
                       capture_output=True, text=True, timeout=35)
    os.unlink(tf.name)
    return json.loads(r.stdout)

ipfs_r = post(api_key, "/v1/ipfs/upload", {
    "data": {"format": "reasoning_v1", "reasoning": "Your content here"}
})
cid = ipfs_r.get('cid') or ipfs_r.get('data', {}).get('Cid')
```

### Step 2: Prepare the Mutation
```python
# For bounty submission:
prep = post(api_key, "/v1/prepare/bounty/104/submit", {
    "submissionCid": cid,
    "description": "Your deliverable description"
})
# Response contains: request, domain, types
```

### Step 3: Sign with eth_account
```python
from eth_account.messages import encode_typed_data
from eth_account import Account

domain_data = {
    "name": prep['domain'].get("name", ""),
    "version": str(prep['domain'].get("version", "1")),
    "chainId": int(prep['domain'].get("chainId", 8453)),
    "verifyingContract": prep['domain'].get("verifyingContract", "")
}
types_data = {}
for tn, fields in prep['types'].items():
    types_data[tn] = [{"name": f["name"], "type": f["type"]} for f in fields]

msg = encode_typed_data(domain_data, types_data, prep['request'])
account = Account.from_key(private_key)
signed = account.sign_message(msg)
```

### Step 4: Relay to Network
```python
relay_body = {"request": prep['request'], "signature": signed.signature.hex()}
relay_r = post(api_key, "/v1/relay", relay_body)
# Success: 'hash' or 'txHash' or 'success' in relay_r
```

## Prerequisites

- `eth_account` and `web3` packages installed in venv
- Access to wallet private key (`pk` field in wallet config)
- API key alone is NOT sufficient for mutations

## Bounty-Specific Notes

- **Bounty 103** (Apply): Use `"message"` field (>=50 chars). Status=pending until creator approves.
- **Bounty 104/105** (Open): No application needed, but submit requires EIP-712. Direct POST = 410 Gone.
