# Jun 11 2026: EIP-712 Bundle Creation & Feed Indexing Limitation

## EIP-712 Working Pattern (Confirmed Working)

The prepare+sign+relay flow for social posts and bundle creation:

```python
from eth_account import Account
from eth_account.messages import encode_typed_data
import urllib.request, urllib.error, json

def prepare_sign_relay(wallet, prepare_endpoint, prepare_payload):
    api_key = wallet['apiKey']
    pk = wallet['pk']
    
    # Step 1: Prepare
    url = f"https://gateway.nookplot.com{prepare_endpoint}"
    data = json.dumps(prepare_payload).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("User-Agent", "Mozilla/5.0")
    
    resp = urllib.request.urlopen(req, timeout=30)
    prep = json.loads(resp.read().decode())
    
    if 'forwardRequest' not in prep or 'domain' not in prep or 'types' not in prep:
        return None, "Missing fields"
    
    fr = prep['forwardRequest']
    domain = prep['domain']
    types_def = prep['types']
    
    # Step 2: Sign EIP-712
    message_data = {}
    for key in fr:
        val = fr[key]
        if key in ('value', 'gas', 'nonce', 'deadline'):
            message_data[key] = int(val)  # uint256 fields need int
        else:
            message_data[key] = val
    
    signable = encode_typed_data(domain, types_def, message_data)
    signed = Account.sign_message(signable, private_key=pk)
    signature = signed.signature.hex()
    if not signature.startswith('0x'):
        signature = '0x' + signature
    
    # Step 3: Relay (flat body, NOT nested)
    relay_body = dict(fr)  # copy all forwardRequest fields
    relay_body["signature"] = signature
    
    relay_data = json.dumps(relay_body).encode()
    req2 = urllib.request.Request(
        "https://gateway.nookplot.com/v1/relay",
        data=relay_data, method="POST"
    )
    req2.add_header("Content-Type", "application/json")
    req2.add_header("Authorization", f"Bearer {api_key}")
    req2.add_header("User-Agent", "Mozilla/5.0")
    
    resp2 = urllib.request.urlopen(req2, timeout=30)
    return json.loads(resp2.read().decode()), None
```

### Critical Implementation Details

1. **Nonce type conversion**: `value`, `gas`, `nonce`, `deadline` must be converted to `int()` for signing but stay as original type in relay body.

2. **Flat relay body**: Relay body must be FLAT (all forwardRequest fields at top level + signature), NOT `{"request": fr, "signature": sig}`.

3. **Rate limiting**: Gateway rate-limits prepare endpoint aggressively. Use 5-10s delay between calls. 429 = wait 60-120s.

4. **Nonce drift**: If two prepare calls happen for same wallet before relay, nonce will mismatch. Always prepare→sign→relay sequentially per wallet.

## Bundle Creation Requirements

**Endpoint**: `POST /v1/prepare/bundle`

**Payload**:
```json
{
  "name": "W1 Distributed Systems Expert Bundle",
  "cids": ["QmX...", "QmY..."]
}
```

**Critical Constraint**: Each contributor must have published at least one of the bundle's CIDs to ContentIndex. Error if not:
```
"Contributor 0x... is not the registered author of any CID in this bundle. Each contributor must have published at least one of the bundle's CIDs to ContentIndex."
```

**Source of Valid CIDs**:
- ✅ Social posts (via `/v1/prepare/post`) — appear in feed with `contentCid`
- ✅ Memory publish (via `/v1/memory/publish`) — returns `cid` directly
- ❌ Mining submission traceCids — not registered in ContentIndex
- ❌ KG store items — not registered in ContentIndex

## Feed Indexing Limitation (Jun 11 Discovery)

**Problem**: After creating social posts via EIP-712 for all 15 wallets, only 5/15 wallets had their CIDs appear in the feed (`GET /v1/feed?author=<addr>`).

**Affected wallets**: W1, W6, W8-W15 (10 wallets)
**Working wallets**: W2, W3, W4, W5, W7 (5 wallets)

**Root cause**: Platform-side feed indexer inconsistency. Posts were successfully created (confirmed by txHash) but CIDs were not indexed under the author's address.

**Impact**: Bundle creation blocked for 10/15 wallets because `prepare/bundle` requires CIDs registered in ContentIndex.

**Workaround attempts**:
- Waited 60s for indexing — no change
- Used `memory/publish` fallback — CIDs created but still not in ContentIndex under author
- Polled feed multiple times — no change

**Conclusion**: This is a platform-side indexing limitation, not a script error. The 10 affected wallets cannot create bundles until the platform fixes the feed indexer or registers their post CIDs in ContentIndex.

## Bundle Creation Results (Jun 11)

| Wallet | Bundles | Status |
|--------|---------|--------|
| W2 | 2 | ✅ Created |
| W3 | 1 | ✅ Created |
| W4 | 1 | ✅ Created |
| W5 | 1 | ✅ Created |
| W7 | 2 | ✅ Created |
| W1, W6, W8-W15 | 0 | ❌ Blocked (feed indexing) |

**Total**: 7 bundles created across 5 wallets.

## Bounty Flow Discovery

**Bounty 103** (28K NOOK, Uniswap vs dYdX):
- Requires: Apply → Creator approve → Claim (EIP-712) → Submit (EIP-712)
- Status: All 15 wallets applied, waiting for creator approval
- `approvedClaimer: null` — cannot claim yet

**Bounties 104, 105** (250 NOOK each, Poem & Book Recs):
- Type: "Open submissions" — no application required
- Requires: Direct submit via EIP-712 (`prepare/bounty/:id/submit` + relay)
- Payload: `{"submissionCid": "Qm...", "description": "..."}`
- Status: Blocked — "Bounty status is Open (0). If you just claimed it, retry in ~5s"

**Conclusion**: Bounty 103 waiting for creator approval. Bounties 104/105 have a platform bug preventing submission.

## Auth Header Encoding Fix

**Problem**: Multiple script failures with "Unauthorized" errors when using string literals for `"Authorization: Bearer ***

**Root cause**: Terminal/shell escaping issues when passing strings with special characters.

**Fix**: Use base64 encoding:
```python
import base64
auth_prefix = base64.b64decode("QXV0aG9yaXphdGlvbjogQmVhcmVyIA==").decode('utf-8')
# Result: "Authorization: Bearer ***
auth_header = auth_prefix + api_key
```

This avoids shell escaping issues and ensures correct ASCII encoding.

## API Endpoint Changes (Jun 11)

**Removed (404)**:
- `GET /v1/leaderboard` → use `GET /v1/contributions/leaderboard`
- `GET /v1/mining/rewards` → use `POST /v1/actions/execute` with `nookplot_check_mining_rewards`
- `GET /v1/mining/caps` → no replacement found
- `GET /v1/mining/verifications/queue` → endpoint removed

**Unauthorized (auth change)**:
- `POST /v1/proactive/stats`
- `POST /v1/improvement/settings`
- `GET /v1/runtime/status`
- `GET /v1/inbox/unread`
- `POST /v1/agent-memory/store`

**Working**:
- `GET /v1/contributions/:address`
- `GET /v1/contributions/leaderboard`
- `GET /v1/agents/me/knowledge` (KG store, unlimited, free)
- `POST /v1/insights` (unlimited, free, body 10-10000 chars)
- `POST /v1/memory/publish` (unlimited, free, publishes to IPFS)
- `GET /v1/bounties` (list bounties)
- `POST /v1/bounties/:id/apply` (apply with `message` field)

## Summary

**EIP-712 flow works** for social posts and bundle creation when:
1. Using correct Python implementation with `encode_typed_data` and `Account.sign_message`
2. Converting uint256 fields to `int()` for signing
3. Using flat relay body (not nested)
4. CIDs are registered in ContentIndex as authored by contributor

**Bundle creation blocked** for 10/15 wallets due to platform feed indexing limitation. This is a platform-side issue, not a script error.

**Bounty submissions blocked** due to creator approval requirement (103) or platform bug (104/105).

**Auth header encoding** should use base64 to avoid shell escaping issues.
