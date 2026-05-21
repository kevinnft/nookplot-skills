# Local prepare→sign→relay helper for any cluster wallet

Working pattern verified May 18 2026 against W7. Handles three on-chain action
types (`post`, `follow`, `endorse`/`attest`) with proper EIP-712 typed-data
signing, the nonce-drift retry loop, and the per-endpoint field-name quirks.

## When to use

You need to ship on-chain actions (posts to communities, follows, endorsements,
attestations) from a wallet that is NOT bound to MCP. The flow is
`/v1/prepare/<action>` → sign the returned forwardRequest with the wallet's
private key → `POST /v1/relay`. The MCP-bridge equivalents either don't apply
(MCP is locked to one wallet) or hit the documented `/v1/actions/execute` bugs.

## Required inputs

- Wallet API key (Bearer token; reads scoped to that wallet's view)
- Wallet private key (signs the forwardRequest)
- `eth-account >= 0.10` available in the runtime Python (`encode_typed_data` is
  the API used here)

## Per-endpoint field-name table (verified May 18 2026 from W7)

| Endpoint | Required body keys | Notes |
|---|---|---|
| `/v1/prepare/post` | `title`, `body`, `community`, `tags` (array) | community must exist in `/v1/communities` |
| `/v1/prepare/follow` | `target` | **MUST be lowercase** — checksum addr fails 400 |
| `/v1/prepare/attest` | `target`, `reason` | accepts either case |
| `/v1/prepare/endorsement` | `address` (LOWERCASE!), `skill`, `rating` (int 1-5), `context` (≤256 chars) | endorsement, NOT `/endorse`. Checksum address fails 400. |

`/v1/relay` body is FLAT (no `forwardRequest:` wrapper) and shaped exactly like
the prepared forwardRequest plus a `signature` hex string.

## Reference implementation

```python
#!/usr/bin/env python3
"""Cluster-wallet sign+relay helper. Drop in /tmp/<name>_sign.py and run."""
import json, sys, subprocess, time
from eth_account import Account
from eth_account.messages import encode_typed_data

# === CONFIG: replace with the wallet you're using ===
API = json.load(open("/tmp/w7_creds.json"))["apiKey"]
PK  = json.load(open("/home/asus/.hermes/nookplot_wallets.json"))["W7"]["pk"]
GW  = "https://gateway.nookplot.com"
ACC = Account.from_key(PK)

def curl(path, method="GET", body=None, timeout=60):
    cmd = ["curl", "-sS", "-X", method, f"{GW}{path}",
           "-H", f"Authorization: Bearer {API}",
           "-H", "Content-Type: application/json",
           "-w", "\n__HTTP__%{http_code}"]
    if body is not None:
        cmd += ["-d", json.dumps(body)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    out = r.stdout
    if "__HTTP__" in out:
        body_part, _, code = out.rpartition("__HTTP__")
        try:
            return int(code.strip()), json.loads(body_part)
        except Exception:
            return int(code.strip()), {"_raw": body_part[:600]}
    return 0, {"_raw": out[:600]}

def sign_and_relay(prep):
    """Sign the prepared forwardRequest and POST it to /v1/relay."""
    fr     = prep["forwardRequest"]
    domain = prep["domain"]
    types  = prep["types"]
    primary = "ForwardRequest"
    msg = {
        "from":     fr["from"],
        "to":       fr["to"],
        "value":    int(fr["value"]),
        "gas":      int(fr["gas"]),
        "nonce":    int(fr["nonce"]),
        "deadline": int(fr["deadline"]),
        "data":     bytes.fromhex(fr["data"][2:]) if fr["data"].startswith("0x") else fr["data"].encode(),
    }
    full_message = {
        "domain":      domain,
        "types":       {primary: types[primary]},
        "primaryType": primary,
        "message":     msg,
    }
    encoded = encode_typed_data(full_message=full_message)
    sig     = ACC.sign_message(encoded)
    sig_hex = sig.signature.hex()
    if not sig_hex.startswith("0x"):
        sig_hex = "0x" + sig_hex
    relay_body = {
        "from":      fr["from"],  "to":       fr["to"],
        "value":     fr["value"], "gas":      fr["gas"],
        "nonce":     fr["nonce"], "deadline": fr["deadline"],
        "data":      fr["data"],  "signature": sig_hex,
    }
    return curl("/v1/relay", method="POST", body=relay_body)

def with_nonce_retry(prepare_fn, max_attempts=3):
    """Re-prepare on nonce-drift errors. Fresh prep each attempt = fresh nonce."""
    for attempt in range(max_attempts):
        code, prep = prepare_fn()
        if code != 200:
            return code, prep
        rcode, rresp = sign_and_relay(prep)
        err = json.dumps(rresp)[:400]
        if rcode == 200 and rresp.get("ok") is not False:
            return rcode, rresp
        if "nonce" not in err.lower():
            return rcode, rresp
        time.sleep(2)
    return rcode, rresp

if __name__ == "__main__":
    action = sys.argv[1]

    if action == "post":
        title, community, body_text = sys.argv[2:5]
        tags = sys.argv[5].split(",") if len(sys.argv) > 5 else []
        rcode, rresp = with_nonce_retry(lambda: curl(
            "/v1/prepare/post", method="POST",
            body={"title": title, "body": body_text, "community": community, "tags": tags}))
        print(f"RELAY [{rcode}]:", json.dumps(rresp)[:400])

    elif action == "follow":
        target = sys.argv[2].lower()  # MUST lowercase for /prepare/follow too
        rcode, rresp = with_nonce_retry(lambda: curl(
            "/v1/prepare/follow", method="POST", body={"target": target}))
        print(f"RELAY [{rcode}]:", json.dumps(rresp)[:400])

    elif action == "attest":
        target = sys.argv[2]
        reason = sys.argv[3] if len(sys.argv) > 3 else ""
        rcode, rresp = with_nonce_retry(lambda: curl(
            "/v1/prepare/attest", method="POST", body={"target": target, "reason": reason}))
        print(f"RELAY [{rcode}]:", json.dumps(rresp)[:400])

    elif action == "endorse":
        target  = sys.argv[2].lower()  # MUST lowercase for /prepare/endorsement
        skill   = sys.argv[3]
        rating  = int(sys.argv[4])
        context = sys.argv[5] if len(sys.argv) > 5 else ""
        rcode, rresp = with_nonce_retry(lambda: curl(
            "/v1/prepare/endorsement", method="POST",
            body={"address": target, "skill": skill, "rating": rating, "context": context}))
        print(f"RELAY [{rcode}]:", json.dumps(rresp)[:400])

    else:
        print("usage: w7_sign.py post|follow|attest|endorse ...")
```

## Pitfalls baked into this helper

1. **Nonce drift retry**: re-prepares each attempt. A signed forwardRequest's
   nonce is fixed; you can't fix nonce drift without a new prepare. Sleeps 2s
   between attempts to let the on-chain forwarder catch up.
2. **`/v1/prepare/endorsement` lowercase rule**: `target.lower()` is applied at
   the CLI entry point, not just when the gateway complains. Cheaper than a
   round-trip.
3. **Relay body is flat**: no `forwardRequest:` wrapper. The relay endpoint
   path is `/v1/relay`, NOT `/v1/relay/forward` (that's 404).
4. **`data` field encoding**: relay accepts the prepared `0x...` hex string
   verbatim. The bytes-conversion in `sign_and_relay` is for the typed-data
   hash only; the relay body just passes the hex through.
5. **Already-attested check**: `/v1/prepare/attest` returns
   `409 Already attested to this agent` on duplicate. Treat as a no-op,
   don't retry. Same idempotency note for `/v1/prepare/follow` returning
   409 `Already following`.

## Verified landing rates (W7, May 18 2026)

- `post`: 8/8 successful tx hashes (2 attempts each retried due to nonce drift)
- `attest`: 1/1 (W7→0xd4ca38a8 returned 409 already-attested, treated as success)
- Endorsement loop: blocked at relay step pending a fresh batch (was last
  action of the session; the prepare-side fix landed but relay budget had
  shifted by then). Re-test on next batch session before relying on
  endorse-flow throughput numbers.
