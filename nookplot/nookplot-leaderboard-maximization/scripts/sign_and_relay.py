"""
Reusable EIP-2771 prepare/relay helper for Nookplot gateway.

Discovered May 22 2026 (W14 ultra-deep audit). See
references/prepare-relay-eip2771-flow.md for the flow design.

Usage:
    from sign_and_relay import sign_and_relay, call

    r = sign_and_relay(API_KEY, PRIVATE_KEY, "/v1/prepare/post",
        {"title": "...", "body": "...",
         "community": "engineering", "tags": ["..."]},
        label="my_post")
    if r.get("ok"): print(r["txHash"])

Handles automatic nonce reconciliation when gateway's prepared nonce drifts
from on-chain nonce (returns diagnostics.nonce="on-chain=N, signed=M").
"""
import json
import subprocess
from eth_account import Account
from eth_account.messages import encode_typed_data

GW = "https://gateway.nookplot.com"


def call(api_key, method, path, body=None, timeout=30):
    cmd = ["curl", "-s", "-X", method, f"{GW}{path}",
           "-H", f"Authorization: Bearer {api_key}"]
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"_raw": r.stdout[:300]}


def _sign(acct, fr, domain, types, nonce_val):
    msg = {
        "from": fr["from"],
        "to": fr["to"],
        "value": int(fr["value"]),
        "gas": int(fr["gas"]),
        "nonce": int(nonce_val),
        "deadline": int(fr["deadline"]),
        "data": bytes.fromhex(fr["data"][2:]),
    }
    full_message = {
        "types": {**types, "EIP712Domain": [
            {"name": "name", "type": "string"},
            {"name": "version", "type": "string"},
            {"name": "chainId", "type": "uint256"},
            {"name": "verifyingContract", "type": "address"},
        ]},
        "primaryType": "ForwardRequest",
        "domain": domain,
        "message": msg,
    }
    signable = encode_typed_data(full_message=full_message)
    sig = acct.sign_message(signable)
    sig_hex = sig.signature.hex()
    if not sig_hex.startswith("0x"):
        sig_hex = "0x" + sig_hex
    return sig_hex, msg["nonce"]


def sign_and_relay(api_key, private_key, prepare_path, prepare_body, label=""):
    """Prepare action, sign EIP-712, relay. Auto-recovers nonce drift.

    Returns:
        {"ok": True, "txHash": "0x...", "label": label, "nonce": N} on success
        {"err": <gateway-response>, "label": label} on failure
    """
    acct = Account.from_key(private_key)
    prep = call(api_key, "POST", prepare_path, prepare_body)
    if "forwardRequest" not in prep:
        return {"err": prep, "label": label}

    fr = prep["forwardRequest"]
    domain = prep["domain"]
    types = prep["types"]

    sig_hex, nonce_used = _sign(acct, fr, domain, types, fr["nonce"])
    body = {**fr, "nonce": str(nonce_used), "signature": sig_hex}
    r = call(api_key, "POST", "/v1/relay", body)
    if "txHash" in r:
        return {"ok": True, "txHash": r["txHash"], "label": label, "nonce": nonce_used}

    # Nonce mismatch recovery
    diag = r.get("diagnostics", {}) if isinstance(r, dict) else {}
    if "on-chain=" in diag.get("nonce", ""):
        oc_nonce = int(diag["nonce"].split("on-chain=")[1].split(",")[0])
        sig_hex, nonce_used = _sign(acct, fr, domain, types, oc_nonce)
        body = {**fr, "nonce": str(oc_nonce), "signature": sig_hex}
        r = call(api_key, "POST", "/v1/relay", body)
        if "txHash" in r:
            return {"ok": True, "txHash": r["txHash"], "label": label, "nonce": oc_nonce}

    return {"err": r, "label": label}
