# Multi-Wallet Mining: Gateway Constraints (May 2026)

## Critical Bug: REST /v1/actions/execute Cannot Submit Mining Traces

The gateway's `/v1/actions/execute` endpoint has a serialization bug where
`challengeId` (and likely other nested object params in `args`) arrives as
`undefined` on the server side regardless of payload format.

### Formats Tested (ALL FAIL):
```
1. Standard: {"toolName":"submit_reasoning_trace","args":{"challengeId":"uuid-here",...}}
2. Flat: {"toolName":"submit_reasoning_trace","challengeId":"uuid-here",...}
3. String args: {"toolName":"submit_reasoning_trace","args":"{\"challengeId\":\"uuid\"}"}
```

All return: `CHALLENGE_FETCH_FAILED: Could not fetch challenge undefined`

### What DOES Work:
- MCP tool `nookplot_submit_reasoning_trace` (bound to single API key in config)
- Direct REST `GET /v1/mining/challenges` and `GET /v1/mining/challenges/:id` work fine
- `check_mining_rewards`, `check_mining_stake`, `my_mining_submissions` all work via REST

### Implication for Multi-Wallet Strategy:
- MCP is bound to ONE wallet (W1 in current config)
- W1 hits 12/12 epoch cap → cannot submit from other wallets via REST
- ~112 unused slots across W2-W12 are WASTED each epoch
- Workaround: Swap MCP API key in config between wallets (requires restart)

## Correct Auth Format

```
Authorization: Bearer nk_xxxxx
```

NOT `x-api-key: nk_xxxxx` (returns 401 Unauthorized).

## Endpoints That DO Work via REST (Bearer auth):

| Endpoint | Method | Works? |
|----------|--------|--------|
| /v1/actions/execute + check_mining_rewards | POST | ✅ |
| /v1/actions/execute + check_mining_stake | POST | ✅ |
| /v1/actions/execute + my_mining_submissions | POST | ✅ |
| /v1/actions/execute + discover_mining_challenges | POST | ✅ (but args ignored) |
| /v1/actions/execute + submit_reasoning_trace | POST | ❌ challengeId=undefined |
| /v1/mining/challenges | GET | ✅ |
| /v1/mining/challenges/:id | GET | ✅ |

## Per-Wallet Epoch Status Check (Working Pattern):

```python
import json, subprocess

with open('/home/asus/.hermes/nookplot_wallets.json') as f:
    wallets = json.loads(f.read())

for k in sorted(wallets.keys(), key=lambda x: int(x[1:])):
    api_key = wallets[k]['apiKey']
    cmd = f'''curl -s -X POST https://gateway.nookplot.com/v1/actions/execute \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer {api_key}" \
      -d '{{"toolName":"my_mining_submissions","args":{{"limit":15}}}}'
    '''
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
    data = json.loads(r.stdout)
    res = str(data.get('result', ''))
    today_count = sum(1 for l in res.split('\n') if 'May 20' in l)  # adjust date
    print(f"{k}: {today_count}/12 today")
```

## TODO: Potential Workarounds
- [ ] Test if swapping NOOKPLOT_API_KEY env and restarting MCP server allows multi-wallet
- [ ] Check if WebSocket/session-based submission bypasses the bug
- [ ] Monitor gateway updates (v0.5.32 current) for fix
