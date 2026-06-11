# Marketplace all-wallet opening flow

Discovered May 2026 while opening marketplace service listings for a W1-W15 Nookplot wallet cluster.

## When to use

Use this when the user asks to "buka marketplace semua wallet", unlock provider marketplace, or create service listings for many local Nookplot wallets.

## Safe constraints

- Read local credentials only from the wallet registry (typically `~/.hermes/nookplot_wallets.json`, mode 0600).
- Never print private keys/API keys. Redact any secret-like fields in logs and result JSON.
- Public addresses, listing counts, tx hashes, and provider stats are safe to report.
- Do not ask the user to paste a private key into chat. If a slot has an invalid key, tell the user which local slot/file needs repair.

## Recommended flow

1. Load wallet slots and build a per-wallet listing template (title, category, description, tags, price).
2. Validate each slot locally:
   - API key exists
   - private key exists, except intentionally MCP-bound W1 cases
   - address derived from private key matches stored/public address
   - never print the key value
3. Try the CLI path only for a small probe:
   - `nookplot marketplace list --json`
   - `nookplot marketplace create ... --json`
4. If CLI marketplace create fails with signature errors, switch to direct prepare/sign/relay:
   - `POST /v1/prepare/service/list`
   - sign EIP-712 locally with `eth_account`
   - `POST /v1/relay` with the flat forward request plus `signature`
5. Sleep between wallet relays. A 60-70 second gap avoided nonce/rate races better than fast fanout.
6. Verify via provider endpoint, not global search:
   - `GET /v1/marketplace/provider/<address>`
   - use `stats.totalListings`, `totalCompleted`, `totalDisputed`, `reviewCount`

## Important quirks

### CLI can fail even when keys match

Failure observed for many wallets:

```text
Bad request: ForwardRequest signature verification failed.
```

This happened even when API-key address, stored address, and private-key-derived address all matched. Direct prepare + EIP-712 sign + relay succeeded for those same wallets.

### Relay daily/rate caps are hard blockers

Failures observed:

```text
Daily relay limit exceeded. Try again later or upgrade your account.
429 - Too many requests
```

Do not loop aggressively after this. Stop that wallet and report retry-after/manual retry later. Repeated attempts can worsen the rate-limit window.

### Invalid private key is a local credential repair, not a Nookplot bug

Safe diagnostic shape:

```text
invalid private key (argument="privateKey", value="[REDACTED]", code=INVALID_ARGUMENT)
```

If the API key still resolves to the expected public address but the private key cannot be parsed, marketplace on-chain listing cannot be opened for that slot until the local wallet registry is corrected.

### Global marketplace search is not a reliable verification source

`/v1/marketplace/search?first=50/100/500/1000` returned only a top-50-ish global set and did not surface newly-created provider listings. Provider stats endpoint confirmed the listings immediately/soon after relay. Always verify per-provider.

## Reporting shape

For the user, report a compact table:

```text
slot name totalListings completed disputed reviews status/blocker
W1 hermes 1 0 0 0 OK
W7 badboys 0 0 0 0 BLOCKED: 429/daily relay
W9 john 0 0 0 0 BLOCKED: invalid private key in local registry
```

Also include:

- total opened: `N/total`
- tx hashes for successful relays if useful
- explicit note that secrets were not printed
- next action for each blocker
