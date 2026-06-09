#!/usr/bin/env python3
"""
V9 EIP-712 Signed Action Executor for Nookplot
Corrected version using encode_typed_data (NOT personal_sign).

Usage:
  python3 v9_signer.py <wallet_name> <action> '<payload_json>'

Examples:
  python3 v9_signer.py kaiju8 post '{"title":"Test","body":"Testing V9","community":"general"}'
  python3 v9_signer.py jordi vote '{"cid":"Qm...","type":"up"}'
  python3 v9_signer.py abel follow '{"target":"0x..."}'
"""

import os, sys, json, re
from eth_account import Account
from eth_account.messages import encode_typed_data

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

GATEWAY = "https://gateway.nookplot.com"
WALLET_DIR = "/home/ryzen"


def load_wallet(name):
    """Load wallet from ~/nookplot-{name}/.env using line-by-line parsing."""
    env_dict = {}
    env_path = os.path.join(WALLET_DIR, f"nookplot-{name}", ".env")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env_dict[k] = v.strip().strip('"').strip("'")

    api_key = env_dict.get("NOOKPLOT_API_KEY", "")
    pk = env_dict.get("WALLET_PRIVATE_KEY", "") or env_dict.get("NOOKPLOT_AGENT_PRIVATE_KEY", "")
    address = env_dict.get("NOOKPLOT_AGENT_ADDRESS", "") or env_dict.get("NOOKPLOT_ADDRESS", "")

    if not api_key or not pk:
        raise ValueError(f"Missing NOOKPLOT_API_KEY or private key in {env_path}")

    return {
        "api_key": api_key,
        "private_key": pk,
        "account": Account.from_key(pk),
        "address": address,
    }


def v9_execute(wallet_name, action, payload):
    """Full prepare → EIP-712 sign → relay pipeline."""
    wallet = load_wallet(wallet_name)

    if HAS_REQUESTS:
        headers = {
            "Authorization": f"Bearer {wallet['api_key']}",
            "Content-Type": "application/json",
        }

        # Step 1: Prepare
        resp = requests.post(
            f"{GATEWAY}/v1/prepare/{action}",
            headers=headers,
            json=payload,
            timeout=20,
        )
        data = resp.json()
    else:
        # Fallback to curl
        import subprocess
        cmd = [
            "curl", "-s", "-m", "20", "-X", "POST",
            "-H", f"Authorization: Bearer {wallet['api_key']}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload),
            f"{GATEWAY}/v1/prepare/{action}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        data = json.loads(result.stdout)

    # Check for errors
    if "error" in data:
        return False, data.get("error", data.get("message", str(data)))

    # Extract EIP-712 components
    fr = data.get("forwardRequest", {})
    domain = data.get("domain", {})
    types = data.get("types", {})
    cid = data.get("cid", "")

    if not fr or not domain:
        return False, f"Missing forwardRequest or domain in response: {list(data.keys())}"

    # Step 2: EIP-712 Sign
    full_message = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "ForwardRequest": types.get("ForwardRequest", [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "gas", "type": "uint256"},
                {"name": "nonce", "type": "uint256"},
                {"name": "deadline", "type": "uint48"},
                {"name": "data", "type": "bytes"},
            ]),
        },
        "domain": domain,
        "primaryType": "ForwardRequest",
        "message": fr,
    }

    signable = encode_typed_data(full_message=full_message)
    signed = wallet["account"].sign_message(signable)
    sig = signed.signature.hex()
    if not sig.startswith("0x"):
        sig = "0x" + sig

    # Step 3: Relay
    relay_payload = {
        "from": fr.get("from", wallet["address"]),
        "to": fr["to"],
        "value": fr.get("value", "0"),
        "gas": fr.get("gas", "100000"),
        "nonce": fr.get("nonce", "0"),
        "deadline": fr.get("deadline", "0"),
        "data": fr["data"],
        "signature": sig,
    }

    if HAS_REQUESTS:
        resp2 = requests.post(
            f"{GATEWAY}/v1/relay",
            headers=headers,
            json=relay_payload,
            timeout=20,
        )
        relay_data = resp2.json()
    else:
        import subprocess
        cmd = [
            "curl", "-s", "-m", "20", "-X", "POST",
            "-H", f"Authorization: Bearer {wallet['api_key']}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(relay_payload),
            f"{GATEWAY}/v1/relay",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        relay_data = json.loads(result.stdout)

    # Check result
    if "txHash" in relay_data or relay_data.get("success"):
        return True, cid if cid else "OK"
    elif "error" in relay_data:
        return False, relay_data.get("error", relay_data.get("message", ""))
    elif "already" in str(relay_data).lower():
        return True, "already"
    else:
        return True, cid if cid else json.dumps(relay_data)[:80]


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    wallet_name = sys.argv[1]
    action = sys.argv[2]
    payload = json.loads(sys.argv[3])

    ok, result = v9_execute(wallet_name, action, payload)
    if ok:
        print(f"✅ {action} success: {result}")
    else:
        print(f"❌ {action} failed: {result}")
    sys.exit(0 if ok else 1)
