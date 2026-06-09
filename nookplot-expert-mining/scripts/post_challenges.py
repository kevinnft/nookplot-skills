#!/usr/bin/env python3
"""Nookplot Challenge Poster — posts expert-level mining challenges from a plan JSON.

Usage:
    python3 post_challenges.py [--plan PATH]

Default plan: /home/ryzen/nookplot-mining-challenges-2026-05-25/remaining_plan.json
Plan format: {"wallet_name": [{"title": "...", "description": "...", "domains": "tag1,tag2"}, ...]}

Cap: 10 challenges per wallet per 24h rolling window.
Script breaks out of a wallet's loop on CAP detection to avoid wasting time.
"""

import subprocess, json, os, re, time, sys, argparse

WALLET_NAMES = [
    'kaiju8','jordi','abel','din','don','ball','heist','gord','kimak','liau',
    'bagong','herdnol','gordon','kikuk','pratama'
]

DEFAULT_PLAN = '/home/ryzen/nookplot-mining-challenges-2026-05-25/remaining_plan.json'

def load_wallets():
    wallets = {}
    for name in WALLET_NAMES:
        env_path = os.path.expanduser(f'~/nookplot-{name}/.env')
        if os.path.exists(env_path):
            env = {}
            with open(env_path) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        k, v = line.split('=', 1)
                        env[k] = v.strip().strip('"').strip("'")
            wallets[name] = env.get('NOOKPLOT_API_KEY', '')
    return wallets

def curl_post(path, api_key, data_dict):
    payload = json.dumps(data_dict)
    tmp = "/tmp/nookpost_payload.json"
    with open(tmp, 'w') as f:
        f.write(payload)
    cmd = (
        f'curl -s -X POST '
        f'-H "Authorization: Bearer {api_key}" '
        f'-H "Content-Type: application/json" '
        f'-H "User-Agent: Mozilla/5.0" '
        f'-d @{tmp} '
        f'"https://gateway.nookplot.com{path}"'
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout

def post_challenge(api_key, title, description, domains):
    domain_tags = [d.strip() for d in domains.split(',')] if isinstance(domains, str) else domains
    data = {
        "title": title,
        "description": description,
        "difficulty": "expert",
        "domainTags": domain_tags
    }
    raw = curl_post("/v1/mining/challenges", api_key, data)
    
    if '"id"' in raw or '"challengeId"' in raw:
        cid = re.search(r'"(?:id|challengeId)"\s*:\s*"([^"]+)"', raw)
        return 'ok', cid.group(1) if cid else 'unknown'
    elif 'maximum' in raw.lower() or 'limit' in raw.lower():
        return 'cap', raw[:200]
    elif '429' in raw or 'Too many' in raw:
        return 'rate_limit', raw[:200]
    else:
        return 'error', raw[:200]

def main():
    parser = argparse.ArgumentParser(description='Post Nookplot challenges')
    parser.add_argument('--plan', default=DEFAULT_PLAN, help='Path to plan JSON')
    args = parser.parse_args()
    
    if not os.path.exists(args.plan):
        print(f"Plan file not found: {args.plan}")
        sys.exit(1)
    
    with open(args.plan) as f:
        plan = json.load(f)
    
    wallets = load_wallets()
    print(f"Loaded {len(wallets)} wallets, {sum(len(v) for v in plan.values())} challenges to post")
    
    results = {'ok': 0, 'cap': 0, 'rate_limit': 0, 'error': 0}
    wallet_results = {}
    
    for wallet_name, challenges in plan.items():
        if wallet_name not in wallets:
            print(f"  SKIP {wallet_name}: no credentials")
            continue
        
        api_key = wallets[wallet_name]
        w_ok = 0
        w_cap = 0
        w_err = 0
        
        for i, ch in enumerate(challenges):
            domains = ch.get('domains', '') or ch.get('domainTags', [])
            if isinstance(domains, list):
                domains = ','.join(domains)
            
            status, detail = post_challenge(api_key, ch['title'], ch['description'], domains)
            
            if status == 'ok':
                results['ok'] += 1
                w_ok += 1
            elif status == 'cap':
                results['cap'] += 1
                w_cap += 1
                print(f"  [{wallet_name}] #{i+1} CAP — stopping this wallet")
                break
            elif status == 'rate_limit':
                results['rate_limit'] += 1
                print(f"  [{wallet_name}] #{i+1} RATE_LIMIT — sleeping 10s...")
                time.sleep(10)
                status2, _ = post_challenge(api_key, ch['title'], ch['description'], domains)
                if status2 == 'ok':
                    results['ok'] += 1
                    w_ok += 1
                else:
                    w_err += 1
                    results['error'] += 1
            else:
                results['error'] += 1
                w_err += 1
                if 'cap' in str(detail).lower() or 'limit' in str(detail).lower():
                    w_cap += 1
                    break
                print(f"  [{wallet_name}] #{i+1} ERR: {detail[:120]}")
            
            time.sleep(1.5)
        
        wallet_results[wallet_name] = {'ok': w_ok, 'cap': w_cap, 'error': w_err}
        if w_ok > 0 or w_cap > 0 or w_err > 0:
            print(f"  {wallet_name}: {w_ok} OK, {w_cap} CAP, {w_err} ERR")
    
    print(f"\n=== RESULTS ===")
    print(f"Posted: {results['ok']}, Capped: {results['cap']}, Rate-limited: {results['rate_limit']}, Errors: {results['error']}")

if __name__ == '__main__':
    main()
