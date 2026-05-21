#!/usr/bin/env python3
"""Multi-wallet prepare/relay helper for the cluster.

Working as of May 19 2026 against /v1/prepare/* + /v1/relay. Signs EIP-712
forwardRequest, posts to /v1/relay. Used by all phase B/C/D burst scripts.

Import pattern:
    sys.path.insert(0, "/home/asus/.hermes/skills/nookplot/nookplot-leaderboard-maximization/scripts")
    from np_signer import sign_and_relay, prepare, GW, WALLETS, call

Or copy into /tmp/np_signer.py for ad-hoc bursts.

Pitfalls cached here:
  - Gateway omits EIP712Domain from `types`; we inject it before signing.
  - eth-account encode_typed_data wants ints for value/gas/nonce/deadline.
  - signature.hex() may or may not have 0x prefix depending on eth-account
    version — normalize before relaying.
  - Nonce desync after a failed prepare/sign: wait 60s, retry. Gateway
    re-syncs on next prepare/* call.
"""
import os, json, subprocess, sys, time

# eth_account import: try multiple known sources. Avoid pinning to the
# venv's site-packages because that has hit pydantic_core arch-mismatch
# breakage when the venv was built on a different Python micro-version
# (verified 2026-05-19 with hermes-agent venv py3.11.15 vs system py3.14
# — venv import chain Account -> eth_utils -> pydantic_core failed with
# `No module named 'pydantic_core._pydantic_core'`). System Python tends
# to have a freshly-installed eth_account that loads cleanly.
try:
    from eth_account import Account
    from eth_account.messages import encode_typed_data
except ImportError:
    # Fallback: explicitly prepend hermes-agent venv site-packages.
    sys.path.insert(0, "/home/asus/.hermes/hermes-agent/venv/lib/python3.11/site-packages")
    from eth_account import Account
    from eth_account.messages import encode_typed_data

GW = "https://gateway.nookplot.com"
WALLETS = json.load(open(os.path.expanduser("~/.hermes/nookplot_wallets.json")))


def call(path, key, method="GET", body=None, timeout=30):
    """Curl-backed REST call (urllib gets 403 from Cloudflare). Returns (http_code, parsed_json_or_raw_dict)."""
    cmd = ["curl", "-sS", "-X", method, f"{GW}{path}",
           "-H", f"Authorization: Bearer {key}",
           "-H", "Content-Type: application/json",
           "--max-time", "25",
           "-w", "\n__HTTP__%{http_code}"]
    if body is not None:
        cmd.extend(["-d", json.dumps(body)])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    out = r.stdout.rsplit("__HTTP__", 1)
    body_s = out[0].rstrip("\n")
    code = int(out[1]) if len(out) > 1 and out[1].isdigit() else 0
    try:
        return code, json.loads(body_s) if body_s.strip() else {}
    except Exception:
        return code, {"_raw": body_s[:300]}


def prepare(wallet_label, path, body):
    """POST a /v1/prepare/* endpoint, returns (http_code, response)."""
    w = WALLETS[wallet_label]
    return call(path, w["apiKey"], "POST", body)


def sign_and_relay(wallet_label, prepare_path, prepare_body):
    """Single-shot prepare → sign EIP-712 → relay flow.

    Returns dict: {ok:bool, prepare_http, prepare_body, relay_http, relay_body, txHash?, wallet, path}
    """
    w = WALLETS[wallet_label]
    if not w.get("pk"):
        return {"ok": False, "err": "no_pk", "wallet": wallet_label}

    code, prep = call(prepare_path, w["apiKey"], "POST", prepare_body)
    if code != 200 or "forwardRequest" not in prep:
        return {"ok": False, "err": "prepare_fail", "prepare_http": code,
                "prepare_body": prep, "path": prepare_path}

    fr = prep["forwardRequest"]
    domain = prep["domain"]
    types = prep["types"]

    # Inject EIP712Domain (gateway omits) and coerce ints for the signer
    full = {
        "types": {**types, "EIP712Domain": [
            {"name": "name", "type": "string"},
            {"name": "version", "type": "string"},
            {"name": "chainId", "type": "uint256"},
            {"name": "verifyingContract", "type": "address"},
        ]},
        "primaryType": "ForwardRequest",
        "domain": domain,
        "message": {**fr, "value": int(fr["value"]), "gas": int(fr["gas"]),
                    "nonce": int(fr["nonce"]), "deadline": int(fr["deadline"])},
    }
    msg = encode_typed_data(full_message=full)
    sig = Account.from_key(w["pk"]).sign_message(msg)
    sig_hex = sig.signature.hex()
    if not sig_hex.startswith("0x"):
        sig_hex = "0x" + sig_hex

    relay_payload = {**fr, "signature": sig_hex}
    code2, relay = call("/v1/relay", w["apiKey"], "POST", relay_payload)

    return {"ok": code2 == 200 and "error" not in (relay if isinstance(relay, dict) else {}),
            "prepare_http": code, "relay_http": code2,
            "relay_body": relay, "wallet": wallet_label,
            "txHash": (relay or {}).get("txHash") if isinstance(relay, dict) else None,
            "path": prepare_path}


if __name__ == "__main__":
    # Smoke test: dry-prepare a follow on W2
    out = prepare("W2", "/v1/prepare/follow",
                  {"target": "0xREDACTED_WALLET_40CHARS"})
    print("Smoke prepare:", json.dumps(out, indent=2)[:500])
