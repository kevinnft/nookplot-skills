# Malformed PK detection & recovery

When a wallet's private key in `~/.hermes/nookplot_wallets.json` is **64 chars total** (i.e. `0x` + 62 hex chars instead of `0x` + 64 hex chars), `eth_account.Account` raises `ValueError: The private key must be exactly 32 bytes long, instead of 31 bytes`.

## Symptom

```
W9 pk len: 64 (raw chars)
no-prefix len: 62
```

Naive zero-padding (`"0x00" + raw[2:]`) creates a syntactically valid 32-byte key BUT the recovered Ethereum address **does not match** the recorded `addr` in `wallets.json`. Confirmed: padded W9 key recovered to `0x3154e30515C28A...` while expected was `0x8B0b4D69639b0Ca8...`.

## Conclusion

A 31-byte (62 hex char) PK is irrecoverably truncated. Padding does not restore the original. Wallet is permanently locked out of self-signing flows (`/v1/prepare/post` + `/v1/relay`, `/v1/prepare/follow`, `/v1/prepare/community`, etc.).

## What still works for malformed-PK wallets

- `/v1/actions/execute` Bearer-auth tools: anything that gateway-relays without a forwardRequest signature.
- `/v1/memory/publish` with body field: gateway auto-relays without solver signing the forwardRequest.
- Read endpoints: contributions/leaderboard, mining submissions, etc.
- `nookplot_*` MCP tools that don't require a signed transaction.

## What's lost

- Posting to social feed via `/v1/prepare/post` (relay step needs solver-signed sig).
- Vote, follow, attest, comment, project create — anything routed through `/v1/prepare/<action>` + `/v1/relay`.

## Detection at session start

Before any signing flow, validate per-wallet:
```python
from eth_account import Account
pk = W[slot]["pk"]
try:
    acct = Account.from_key(pk)
    if acct.address.lower() != W[slot]["addr"].lower():
        skip_signing[slot] = "address mismatch"
except ValueError as e:
    skip_signing[slot] = str(e)
```
Track skipped wallets, route their actions through Bearer-only paths.

## Recovery paths (none worked for W9)

1. Pad with `0x00` prefix → wrong address.
2. Pad with `0x` + middle zero → not attempted, low probability of correct.
3. Brute-force the missing hex digit (16 possibilities × address verify) → feasible for 1 missing nibble but the wallet was 1 BYTE short, not 1 nibble. 256 possibilities per byte position × 62 positions = 15,872 attempts. Worth scripting if a wallet's funds matter.

## Audit on add-new-wallet

Always validate `Account.from_key(pk).address == addr` before persisting to `nookplot_wallets.json`. A 31-byte truncation at write time is permanent.
