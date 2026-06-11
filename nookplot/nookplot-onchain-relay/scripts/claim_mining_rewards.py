#!/usr/bin/env python3
"""
Batch claim mining rewards for Nookplot wallets.

Usage:
  1. Get fresh prepare data via browser (must be on gateway.nookplot.com domain):
     Run the prepare loop in browser console, save output as JSON.
  2. Run this script with the prepare data file:
     python3 claim_mining_rewards.py /path/to/prepare_data.json

Prepare data format (JSON object keyed by wallet ID):
{
  "W5": {
    "fr": {
      "from": "0x...", "to": "0x...", "value": "0", "gas": "500000",
      "nonce": "373", "deadline": 1780636816, "data": "0x2f52ebb7..."
    },
    "nook": "430281"
  },
  ...
}

The script will:
  - Sign each ForwardRequest with the wallet's private key
  - Try nonce offsets -2, -1, 0 to handle drift
  - Relay via curl with -d @file (most reliable for large payloads)
  - Report results per wallet
"""
import json, subprocess, sys, time
from eth_account import Account

DOMAIN = {"name": "NookplotForwarder", "version": "1", "chainId": 8453, "verifyingContract": "0xBAEa9E1b5222Ab79D7b194de95ff904D7E8eCf80"}
TYPES = {"ForwardRequest": [
    {"name": "from", "type": "address"}, {"name": "to", "type": "address"},
    {"name": "value", "type": "uint256"}, {"name": "gas", "type": "uint256"},
    {"name": "nonce", "type": "uint256"}, {"name": "deadline", "type": "uint48"},
    {"name": "data", "type": "bytes"}
]}

def load_wallets(path="/home/asus/.hermes/nookplot_wallets.json"):
    with open(path) as f:
        return json.load(f)

def sign_and_relay(wid, fr, pk, key):
    """Sign ForwardRequest and relay via curl. Returns (success, message)."""
    prep_nonce = int(fr["nonce"])
    
    for nonce_offset in [0, -2, -1]:
        corrected_nonce = prep_nonce + nonce_offset
        fr_corrected = {**fr, "nonce": str(corrected_nonce)}
        
        try:
            account = Account.from_key(pk)
            signed = account.sign_typed_data(
                domain_data=DOMAIN, message_types=TYPES, message_data=fr_corrected
            )
            sig = "0x" + signed.signature.hex()
        except Exception as e:
            return False, f"SIGN ERROR: {e}"
        
        relay_body = {**fr_corrected, "signature": sig}
        body_file = f"/tmp/relay_{wid}.json"
        with open(body_file, "w") as f:
            json.dump(relay_body, f)
        
        try:
            auth = "Bearer " + key
            cmd = (
                f'curl -s -X POST "https://gateway.nookplot.com/v1/relay" '
                f'-H "Authorization: {auth}" '
                f'-H "Content-Type: application/json" '
                f'-d @{body_file}'
            )
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            resp = json.loads(result.stdout)
            
            if resp.get("txHash"):
                return True, f"TX:{resp['txHash']} (nonce={corrected_nonce})"
            elif "nonce" in str(resp.get("diagnostics", {})):
                continue  # Try next nonce offset
            elif "deadline" in str(resp).lower():
                return False, "DEADLINE EXPIRED"
            else:
                return False, f"FAILED: {json.dumps(resp)[:100]}"
        except Exception as e:
            return False, f"CURL ERROR: {e}"
    
    return False, "ALL NONCE OFFSETS FAILED"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 claim_mining_rewards.py <prepare_data.json>")
        sys.exit(1)
    
    with open(sys.argv[1]) as f:
        prepares = json.load(f)
    
    wallets = load_wallets()
    results = {}
    
    for wid in sorted(prepares.keys()):
        if wid not in wallets:
            print(f"  {wid}: SKIPPED (not in wallets.json)")
            continue
        
        w = wallets[wid]
        fr = prepares[wid]["fr"]
        nook = prepares[wid].get("nook", "?")
        
        success, msg = sign_and_relay(wid, fr, w["pk"], w["apiKey"])
        results[wid] = {"success": success, "msg": msg, "nook": nook}
        status = "✅" if success else "❌"
        print(f"  {wid}: {status} {msg} ({nook} NOOK)")
        time.sleep(1)
    
    # Summary
    total = sum(int(r["nook"]) for r in results.values() if r["success"] and r["nook"].isdigit())
    claimed = sum(1 for r in results.values() if r["success"])
    print(f"\n{'='*50}")
    print(f"Claimed: {claimed}/{len(results)} wallets")
    print(f"Total: {total:,} NOOK")

if __name__ == "__main__":
    main()
