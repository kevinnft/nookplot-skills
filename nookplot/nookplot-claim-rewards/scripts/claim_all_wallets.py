#!/usr/bin/env python3
"""Batch claim rewards for all Nookplot wallets. 
Usage: ~/.hermes/hermes-agent/venv/bin/python scripts/claim_all_wallets.py
Requires: eth_account in hermes venv, wallets at ~/.hermes/nookplot_wallets.json
Uses curl subprocess (urllib gets 403 from Cloudflare)."""
import json, time, subprocess, sys
from eth_account import Account
from eth_account.messages import encode_typed_data

WALLETS_FILE = "/home/asus/.hermes/nookplot_wallets.json"
GATEWAY = "https://gateway.nookplot.com/v1"

with open(WALLETS_FILE) as f:
    wallets = json.load(f)

def curl_post(url, api_key, payload):
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    try:
        return json.loads(r.stdout)
    except:
        return {"error": f"curl parse error: {r.stdout[:200]}"}

def curl_post_file(url, api_key, file_path):
    """POST with -d @file for relay payloads."""
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", f"@{file_path}"
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    try:
        return json.loads(r.stdout)
    except:
        return {"error": f"curl parse error: {r.stdout[:200]}"}

def sign_claim(pk, on_chain_data):
    fr = on_chain_data["forwardRequest"]
    domain = on_chain_data["domain"]
    types = on_chain_data["types"]
    typed_data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"}
            ],
            "ForwardRequest": types["ForwardRequest"]
        },
        "primaryType": "ForwardRequest",
        "domain": domain,
        "message": {
            "from": fr["from"],
            "to": fr["to"],
            "value": int(fr["value"]),
            "gas": int(fr["gas"]),
            "nonce": int(fr["nonce"]),
            "deadline": int(fr["deadline"]),
            "data": fr["data"]
        }
    }
    account = Account.from_key(pk)
    signable = encode_typed_data(full_message=typed_data)
    signed = account.sign_message(signable)
    return "0x" + signed.signature.hex()

def claim_wallet(wid, w, skip_wallets=None):
    """Claim rewards for a single wallet. Returns result dict."""
    if skip_wallets and wid in skip_wallets:
        return {"wallet": wid, "name": w.get("displayName", wid), "status": "skipped"}

    name = w.get("displayName", wid)
    addr = w["addr"]
    api_key = w["apiKey"]
    pk = w.get("pk")

    print(f"\n{'='*60}")
    print(f"[{wid}] {name} ({addr[:10]}...)")
    print(f"{'='*60}")

    # Step 1: Check balance
    print("  Checking rewards...")
    check = curl_post(f"{GATEWAY}/actions/execute", api_key, {
        "toolName": "check_mining_rewards", "payload": {}
    })
    if "error" in check:
        print(f"  ERROR: {check['error']}")
        return {"wallet": wid, "name": name, "status": "error_check", "error": check["error"]}

    result = check.get("result", {})
    claimable = result.get("claimableBalance", {})
    total_claimable = sum(v for v in claimable.values() if isinstance(v, (int, float)))

    if total_claimable == 0:
        print(f"  Nothing to claim (all zero)")
        return {"wallet": wid, "name": name, "status": "nothing"}

    print(f"  Claimable: {total_claimable:.2f} NOOK ({claimable})")

    if not pk:
        print(f"  SKIP: No private key")
        return {"wallet": wid, "name": name, "status": "no_pk", "claimable": total_claimable}

    # Step 2: Claim (prepare + get sign data)
    print("  Claiming...")
    claim = curl_post(f"{GATEWAY}/actions/execute", api_key, {
        "toolName": "nookplot_claim_mining_reward", "payload": {}
    })
    claim_result = claim.get("result", {})
    if claim_result.get("code") == "NO_BALANCE":
        print(f"  No balance (NO_BALANCE)")
        return {"wallet": wid, "name": name, "status": "nothing"}

    claimed_amount = claim_result.get("claimed", 0)
    print(f"  Claimed: {claimed_amount:.2f} NOOK")

    # Step 3: Sign EIP-712
    on_chain_data = claim_result.get("onChainResult", {}).get("data", {})
    if on_chain_data.get("__nookplot_sign_required__"):
        print("  Signing EIP-712...")
        signature = sign_claim(pk, on_chain_data)

        fr = on_chain_data["forwardRequest"]
        relay_body = {
            "from": fr["from"], "to": fr["to"], "value": fr["value"],
            "gas": fr["gas"], "nonce": fr["nonce"], "deadline": fr["deadline"],
            "data": fr["data"], "signature": signature
        }

        # Write relay payload to file for curl
        payload_file = f"/tmp/relay_{wid}.json"
        with open(payload_file, "w") as f2:
            json.dump(relay_body, f2)

        # Step 4: Relay
        print("  Relaying...")
        relay = curl_post_file(f"{GATEWAY}/relay", api_key, payload_file)

        if "txHash" in relay:
            tx_hash = relay["txHash"]
            print(f"  ✅ TX: {tx_hash}")
            return {"wallet": wid, "name": name, "status": "success", "claimed": claimed_amount, "txHash": tx_hash}
        else:
            print(f"  ❌ Relay: {relay}")
            return {"wallet": wid, "name": name, "status": "relay_fail", "claimed": claimed_amount, "error": str(relay)}
    else:
        print(f"  ✅ No sign needed")
        return {"wallet": wid, "name": name, "status": "no_sign", "claimed": claimed_amount}

def main():
    skip_wallets = set(sys.argv[1:]) if len(sys.argv) > 1 else set()
    results = []

    for wid in sorted(wallets.keys(), key=lambda x: int(x[1:])):
        w = wallets[wid]
        result = claim_wallet(wid, w, skip_wallets)
        results.append(result)
        time.sleep(1.5)

    # Summary
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    success = [r for r in results if r["status"] == "success"]
    nothing = [r for r in results if r["status"] == "nothing"]
    errors = [r for r in results if "error" in r.get("status", "")]
    total_earned = sum(r.get("claimed", 0) for r in success)

    print(f"✅ Claimed:  {len(success)} wallets")
    print(f"⚪ Nothing:  {len(nothing)} wallets")
    print(f"❌ Errors:   {len(errors)} wallets")
    print(f"⏭  Skipped:   {len([r for r in results if r['status'] in ('skipped','no_pk')])} wallets")
    print(f"\nTotal NOOK claimed: {total_earned:,.2f}")
    print()
    for r in success:
        print(f"  {r['wallet']} ({r['name']}): {r['claimed']:,.2f} NOOK | tx: {r['txHash']}")
    for r in nothing:
        print(f"  {r['wallet']} ({r['name']}): nothing to claim")
    for r in errors:
        print(f"  {r['wallet']} ({r['name']}): ERROR - {r.get('error','')}")

    with open("/tmp/claim_all_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to /tmp/claim_all_results.json")

if __name__ == "__main__":
    main()
