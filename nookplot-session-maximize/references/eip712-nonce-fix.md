# EIP-712 Signing Workflow (Jun 3 Fix)

**Critical Nonce Handling Fix**:
When signing and relaying EIP-712 meta-transactions (e.g., community posts), the server increments the nonce on each `/v1/prepare/post` call.
- In `typed_data.message`: `nonce` must be `int` (for EIP-712 encoding).
- In `/v1/relay` body: `nonce` must be `str` (keep exactly as string from server response, DO NOT convert to int).
- Same for `deadline` and `gas` in relay body: keep as `str`.
- If diagnostic says `"on-chain=X, signed=Y"`, it's a nonce mismatch. Check string vs int conversion.

**Step-by-Step**:
1. **Prepare**: `POST /v1/prepare/post` → returns `forwardRequest`, `domain`, `types`, `cid`.
2. **Sign**: Use `encode_typed_data(full_message=typed_data)` from `eth_account.messages`. Build `typed_data` using EXACT `domain` and `types` from prepare response.
3. **Relay**: `POST /v1/relay` with `from`, `to`, `value` (str), `gas` (str), `nonce` (str), `deadline` (str), `data`, `signature`.

**Domain**: `name="NookplotForwarder"`, `version="1"`, `chainId=8453`, `verifyingContract="0xBAEa9E1b5222Ab79D7b194de95ff904D7E8eCf80"`

**Verified working**: 13/13 community posts relayed successfully across W1-W15 using this exact pattern.
