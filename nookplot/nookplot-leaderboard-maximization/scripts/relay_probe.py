#!/usr/bin/env python3
"""Non-destructive relay-budget probe per wallet.

Uses an intentionally-bad signature against /v1/relay to detect daily-cap
without consuming a real relay slot. Returns RELAY-OPEN, DAILY-CAP, or
RELAY-DRY per wallet.

Use BETWEEN phases of the cluster gas-maks pipeline to know which wallets
still have on-chain budget. See `references/cluster-gas-maks-phased-pipeline.md`.

Usage: python relay_probe.py
"""
import os, json, requests, time

try:
    from eth_account import Account
    from eth_account.messages import encode_typed_data
except ImportError:
    print("eth_account not installed. Run with the Hermes venv:")
    print("  ~/.hermes/hermes-agent/venv/bin/python relay_probe.py")
    raise

WALLETS = json.load(open(os.path.expanduser("~/.hermes/nookplot_wallets.json")))
GW = "https://gateway.nookplot.com"

def auth(k):
    return {"Authorization": f"Bearer {k}", "Content-Type": "application/json"}

def probe(tag):
    w = WALLETS[tag]
    if not w.get("pk"):
        return f"{tag:<3} {w.get('displayName','?'):<10} NO_PK (likely MCP-bound wallet)"
    # 1. Get a real forwardRequest from /v1/prepare/follow
    rp = requests.post(f"{GW}/v1/prepare/follow", headers=auth(w["apiKey"]),
                       json={"target": "0xREDACTED_WALLET_40CHARS"},
                       timeout=10)
    if rp.status_code != 200:
        s = rp.text[:200]
        if "Daily relay" in s or "Too many" in s or rp.status_code == 429:
            return f"{tag:<3} {w['displayName']:<10} DAILY-CAP (at prepare)"
        return f"{tag:<3} {w['displayName']:<10} prepare-{rp.status_code}: {s[:80]}"
    # 2. Submit to /v1/relay with a deliberately bogus signature
    j = rp.json()
    fr = j["forwardRequest"]
    relay_body = {**fr, "signature": "0x" + "11" * 65}
    r = requests.post(f"{GW}/v1/relay", headers=auth(w["apiKey"]),
                      json=relay_body, timeout=10)
    # 3. Classify the response
    if r.status_code == 429:
        return f"{tag:<3} {w['displayName']:<10} DAILY-CAP (429)"
    body = r.text
    if "Daily relay" in body or "Too many" in body:
        return f"{tag:<3} {w['displayName']:<10} DAILY-CAP"
    if "insufficient" in body.lower():
        return f"{tag:<3} {w['displayName']:<10} RELAY-DRY (sponsor wallet drained)"
    if "verification failed" in body.lower() or "signature" in body.lower():
        # Bad sig got through to verification → relay budget IS available
        return f"{tag:<3} {w['displayName']:<10} RELAY-OPEN"
    return f"{tag:<3} {w['displayName']:<10} {r.status_code}: {body[:80]}"

if __name__ == "__main__":
    print(f"{'W':<3} {'name':<10} status")
    print("-" * 60)
    for tag in ["W1","W2","W3","W4","W5","W6","W7","W8","W9","W10"]:
        if tag in WALLETS:
            print(probe(tag))
            time.sleep(1)
