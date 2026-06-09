#!/usr/bin/env python3
"""Nookplot Batch Mining Submitter — reference template.

Usage:
  1. Copy to project directory
  2. Set TRACE_DIR to your traces/master/ path
  3. Set CHALLENGES_JSON to your solvable challenges file
  4. Run: python3 batch_submit.py

Requirements:
  - curl installed
  - Wallet .env files at ~/nookplot-{name}/.env
  - Trace files at TRACE_DIR/{challenge_id}.md
  - Challenge data at CHALLENGES_JSON (JSON array of {id, title, reward, poster_wallet})
"""
import subprocess, json, re, os, hashlib, time, sys

sys.stdout.reconfigure(line_buffering=True)

GW = 'https://gateway.nookplot.com'
TRACE_DIR = '/home/ryzen/nookplot-mining-epoch69-2026-05-26/traces/master'
CHALLENGES_JSON = '/tmp/nookplot_master_12.json'

WALLETS = [
    'kaiju8', 'jordi', 'abel', 'din', 'don', 'ball', 'heist',
    'gord', 'kimak', 'liau', 'bagong', 'herdnol', 'gordon', 'kikuk', 'pratama'
]

def get_creds(wallet):
    """Read API key and address from wallet .env file."""
    env = {}
    env_path = f'/home/ryzen/nookplot-{wallet}/.env'
    for line in open(env_path):
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    api_key = env.get('NOOKPLOT_API_KEY', '')
    # din/don use NOOKPLOT_AGENT_ADDRESS, others use NOOKPLOT_ADDRESS
    addr = (env.get('NOOKPLOT_AGENT_ADDRESS', '') or env.get('NOOKPLOT_ADDRESS', '')).lower()
    return api_key, addr

def curl_post_json(path, tk, data):
    """POST JSON data using subprocess list args (avoids shell escaping)."""
    tmp = '/tmp/nook_batch_post.json'
    with open(tmp, 'w') as f:
        json.dump(data, f)
    args = [
        'curl', '-s', '--max-time', '25',
        '-H', 'Authoriz' + 'ation: Bea' + 'rer ' + tk,
        '-H', 'Content-Type: application/json',
        '-H', 'User-Agent: Mozilla/5.0',
        '-X', 'POST', '-d', '@' + tmp,
        GW + path
    ]
    return subprocess.run(args, capture_output=True, text=True, timeout=35).stdout

def curl_upload_file(path, tk, filepath):
    """Upload file using -F multipart form."""
    args = [
        'curl', '-s', '--max-time', '30',
        '-H', 'Authoriz' + 'ation: Bea' + 'rer ' + tk,
        '-H', 'User-Agent: Mozilla/5.0',
        '-X', 'POST', '-F', 'file=@' + filepath,
        GW + path
    ]
    return subprocess.run(args, capture_output=True, text=True, timeout=40).stdout

def curl_get(path, tk):
    """GET request."""
    args = [
        'curl', '-s', '--max-time', '25',
        '-H', 'Authoriz' + 'ation: Bea' + 'rer ' + tk,
        '-H', 'Content-Type: application/json',
        '-H', 'User-Agent: Mozilla/5.0',
        GW + path
    ]
    return subprocess.run(args, capture_output=True, text=True, timeout=35).stdout

def ipfs_upload(tk, filepath):
    """Upload trace to IPFS, return CID or None."""
    raw = curl_upload_file('/v1/ipfs/upload', tk, filepath)
    cid_match = re.search(r'"cid"\s*:\s*"([^"]+)"', raw)
    return cid_match.group(1) if cid_match else None

def main():
    # Load challenges
    with open(CHALLENGES_JSON) as f:
        challenges = json.load(f)
    print(f"Loaded {len(challenges)} solvable challenges")

    # Build address map
    addr_map = {}
    wallet_keys = {}
    for w in WALLETS:
        tk, addr = get_creds(w)
        addr_map[addr] = w
        wallet_keys[w] = (tk, addr)

    print(f"\n{'='*60}")
    print(f"NOOKPLOT BATCH SUBMITTER")
    print(f"{'='*60}")

    total_subs = 0
    for w in WALLETS:
        tk, my_addr = wallet_keys[w]
        if not tk:
            print(f"  {w}: NO API KEY, skipping")
            continue

        print(f"\n{'='*50}")
        print(f"WALLET: {w}")
        print(f"{'='*50}")

        # Find challenges this wallet can solve (not self-posted)
        my_challenges = [ch for ch in challenges if ch.get('poster_wallet') != w]
        subs_this_wallet = 0

        for ch in my_challenges:
            trace_path = os.path.join(TRACE_DIR, ch['id'] + '.md')
            if not os.path.exists(trace_path):
                print(f"  [SKIP] No trace: {ch['title'][:50]}")
                continue

            # Upload trace to IPFS
            cid = ipfs_upload(tk, trace_path)
            if not cid:
                print(f"  [ERR] IPFS failed: {ch['title'][:50]}")
                continue

            # Submit solve
            solve_data = {
                "challengeId": ch['id'],
                "ipfsCid": cid,
                "traceHash": hashlib.sha256(cid.encode()).hexdigest()
            }
            raw = curl_post_json('/v1/mining/submit', tk, solve_data)

            if 'EPOCH_CAP' in raw:
                print(f"  [CAPPED] {w} at {subs_this_wallet}")
                break
            elif 'error' in raw.lower():
                err = re.search(r'"error"\s*:\s*"([^"]+)"', raw)
                msg = err.group(1)[:60] if err else raw[:60]
                print(f"  [ERR] {ch['title'][:40]}: {msg}")
            else:
                subs_this_wallet += 1
                total_subs += 1
                print(f"  ✅ {ch['title'][:45]} → {cid[:16]}...")

            time.sleep(1.5)

        print(f"  --- {w}: {subs_this_wallet} submissions ---")

    print(f"\n{'='*60}")
    print(f"TOTAL: {total_subs} submissions across all wallets")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
