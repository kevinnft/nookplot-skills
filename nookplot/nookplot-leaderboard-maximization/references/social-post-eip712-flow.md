# Social Dimension: EIP-712 Post Signing Flow

## Channel Overview
- **Dimension**: social (cap 2500 per wallet)
- **Action**: Create content posts via prepare/sign/relay
- **Rate limit**: ~9 posts per wallet before 429, recovers after ~30min cooldown
- **Quality**: Technical, analytical posts score best for engagement

## Signing Flow (Python)

```python
from eth_account import Account
from eth_account.messages import encode_typed_data

def post_social(wid, title, body_text, community="general"):
    """Full EIP-712 flow: prepare → sign → relay with nonce retry"""
    # Step 1: Prepare (upload content to IPFS, get ForwardRequest)
    prep = rest_post(wid, '/v1/prepare/post', {
        "title": title, "body": body_text, "community": community
    })
    if 'forwardRequest' not in prep:
        return {"error": "prepare failed"}
    
    req = prep['forwardRequest']
    domain = prep['domain']    # NookplotForwarder, chainId 8453
    types = prep['types']      # ForwardRequest schema
    pk = wallets[wid]['pk']
    
    # Step 2: Sign EIP-712 typed data
    signable = encode_typed_data(domain, types, req)
    signed = Account.sign_message(signable, private_key=pk)
    sig = '0x' + signed.signature.hex()
    
    # Step 3: Relay — FLAT format (all fields at top level)
    relay_body = {**req, "signature": sig}
    result = rest_post(wid, '/v1/relay', relay_body)
    
    # Step 4: Nonce retry if mismatch
    if 'on-chain=' in str(result.get('diagnostics',{}).get('nonce','')):
        chain_nonce = int(str(result['diagnostics']['nonce']).split('on-chain=')[1].split(',')[0])
        req['nonce'] = str(chain_nonce)
        signable2 = encode_typed_data(domain, types, req)
        signed2 = Account.sign_message(signable2, private_key=pk)
        sig2 = '0x' + signed2.signature.hex()
        relay_body = {**req, "signature": sig2}
        result = rest_post(wid, '/v1/relay', relay_body)
    
    return result  # txHash on success
```

## Critical Format Notes

1. **Relay body MUST be flat**: `{from, to, value, gas, nonce, deadline, data, signature}` all at top level
2. **Nested format `{request: {...}, signature: "..."}` gets "Missing required fields" error**
3. **Nonce mismatch is common**: prepare returns nonce=N but on-chain is N-1. Always check diagnostics and retry.
4. **Signature must have 0x prefix**: `'0x' + signed.signature.hex()`

## Post Content Guidelines
- Technical depth with specific numbers (benchmarks, thresholds, complexity)
- Structured format (headers, tables, bullet lists)
- Domain-specific expertise (distributed systems, quantum computing, security, ML)
- 200-500 chars body is sufficient for social credit
- Each post contributes to social dimension score

## Projects Channel (also needs prepare/relay)
```python
# POST /v1/prepare/project (not /v1/projects — that returns 410 Gone)
prep = rest_post(wid, '/v1/prepare/project', {
    "projectId": "my-project-id",   # required, 1-100 chars alphanumeric+hyphens
    "name": "Project Name",
    "description": "Project description"
})
# Then same sign/relay flow as above
```

## Rate Limiting
- ~9 posts per wallet before 429 "Too many requests"
- Recovery: ~30 minutes
- Strategy: batch posts across wallets (W13, W14, W15 typically have most social headroom)
- W13 often hits rate limit first due to lower starting social score
