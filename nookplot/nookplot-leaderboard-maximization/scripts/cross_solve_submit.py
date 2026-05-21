#!/usr/bin/env python3
"""Cross-solve submission helper for non-MCP wallets.

Usage:
    python3 cross_solve_submit.py W2 <challenge_id> trace.md "summary text"

Reads wallet credentials from ~/.hermes/nookplot_wallets.json.
Uploads trace to IPFS, computes SHA-256 hash, submits to challenge.
"""
import json, subprocess, hashlib, sys

WALLETS_PATH = "/home/asus/.hermes/nookplot_wallets.json"
GATEWAY = "https://gateway.nookplot.com"

def load_wallet(wallet_key):
    with open(WALLETS_PATH) as f:
        wallets = json.load(f)
    return wallets[wallet_key]

def ipfs_upload(api_key, trace_content, trace_summary, model="claude-opus-4-6"):
    """Upload trace to IPFS. Returns CID."""
    data = {"data": {"traceContent": trace_content, "traceSummary": trace_summary, "modelUsed": model}}
    cmd = ['curl', '-s', '-X', 'POST', f'{GATEWAY}/v1/ipfs/upload',
           '-H', f'Authorization: Bearer {api_key}', '-H', 'Content-Type: application/json',
           '-d', json.dumps(data)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    resp = json.loads(result.stdout)
    if 'cid' not in resp:
        raise RuntimeError(f"IPFS upload failed: {resp}")
    return resp['cid']

def submit_trace(api_key, challenge_id, cid, trace_hash, trace_summary, model="claude-opus-4-6", step_count=5):
    """Submit to mining challenge. Returns submission data."""
    payload = {
        "traceCid": cid,
        "traceHash": trace_hash,
        "traceSummary": trace_summary,
        "modelUsed": model,
        "stepCount": step_count
    }
    cmd = ['curl', '-s', '-X', 'POST', f'{GATEWAY}/v1/mining/challenges/{challenge_id}/submit',
           '-H', f'Authorization: Bearer {api_key}', '-H', 'Content-Type: application/json',
           '-d', json.dumps(payload)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return json.loads(result.stdout)

def main():
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <wallet_key> <challenge_id> <trace_file> [summary]")
        sys.exit(1)
    
    wallet_key = sys.argv[1]
    challenge_id = sys.argv[2]
    trace_file = sys.argv[3]
    
    wallet = load_wallet(wallet_key)
    api_key = wallet['apiKey']
    
    with open(trace_file) as f:
        trace_content = f.read()
    
    # Summary from arg or first 200 chars of trace
    trace_summary = sys.argv[4] if len(sys.argv) > 4 else trace_content[:200]
    
    # Upload
    cid = ipfs_upload(api_key, trace_content, trace_summary)
    trace_hash = hashlib.sha256(trace_content.encode()).hexdigest()
    
    # Submit
    result = submit_trace(api_key, challenge_id, cid, trace_hash, trace_summary)
    
    if 'id' in result:
        print(f"✅ Submitted: {result['id']}")
        print(f"   Solver: {result.get('solverAddress', '?')}")
        print(f"   Guild: {result.get('solverGuildId', '?')}")
    else:
        print(f"❌ Failed: {result.get('error', result)}")

if __name__ == "__main__":
    main()
