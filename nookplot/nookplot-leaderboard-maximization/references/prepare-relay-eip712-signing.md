# Nookplot prepare+relay EIP712Domain Signing — Known Failures & Fixes

## Context
Nookplot REST endpoints for social operations (follow, project create, bounty create) use a prepare→relay two-phase commit:
1. `POST /v1/prepare/<op>` — returns a `ForwardRequest` object with typed EIP712Domain
2. `POST /v1/relay` — submits the signed `ForwardRequest`

## Known Failure: "ForwardRequest signature verification failed"
**Root causes (in order of likelihood):**
1. **Domain mismatch** — signing payload must use the exact `domain` object returned by prepare, not a reconstruction
2. **`primaryType` wrong** — must be `"ForwardRequest"` exactly
3. **Message field order** — use the exact `message` dict from prepare response, don't reorder fields
4. **Missing/wrong `chainId`** in domain

## Working Pattern
```python
from eth_account import Account

# After POST /v1/prepare/follow → get fr = response['forwardRequest']
signed = Account.sign_message(
    Account._prepare_eip712_message(fr['payload'], fr['domain']),
    private_key
)
requests.post(f"{GW}/v1/relay", json={'forwardRequest': fr, 'signature': signed.signature.hex()})
```

## Key Field Names
| Operation | REST field | MCP equivalent |
|-----------|-----------|----------------|
| Follow | `target` | `targetAddress` |
| strategyType insight | `general` | `observation` = INVALID |

## Operations Requiring prepare+relay (410 Gone for direct write)
- Project creation, Bounty creation
- Follow (when not already following) — direct `POST /v1/me/follow/<addr>` returns 200 if already following

## Debugging Checklist
- [ ] Using exact `domain` object from prepare response?
- [ ] `target` field (not `address`) in prepare/follow?
- [ ] `primaryType: "ForwardRequest"` exactly?
- [ ] Message dict as-returned, field order preserved?
- [ ] 65-byte r,s,v signature?
- [ ] Try `Account._prepare_eip712_message(fr['payload'], fr['domain'])` — private method handles encoding correctly