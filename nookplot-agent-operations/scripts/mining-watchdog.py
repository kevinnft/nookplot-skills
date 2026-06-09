#!/usr/bin/env python3
"""
Nookplot Mining Watchdog

Automated mining when epoch opens. Checks every 5 minutes via cron job.
Sequential mining with 15s gaps to avoid rate limits.

Usage:
    python3 /home/ryzen/nookplot-mining-watchdog.py

Cron job:
    ID: d4e0b8cb39b5
    Schedule: every 5m
    Mode: no_agent=true (runs script directly)

Logs to: /tmp/mining-watchdog.log
"""
import subprocess, os, json, time, sys, urllib.request, urllib.error
from datetime import datetime, timezone

WALLETS = [
    'ball', 'din', 'bagong', 'heist', 'gord', 'herdnol', 'don',
    'kikuk', 'kimak', 'gordon', 'pratama', 'abel', 'kaiju8', 'jordi'
]

LOG_FILE = '/tmp/mining-watchdog.log'

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def get_api_key(wallet):
    env_path = f'/home/ryzen/nookplot-{wallet}/.env'
    if not os.path.exists(env_path):
        return None
    env = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env.get('NOOKPLOT_API_KEY', env.get('NOOKPLOT_AGENT_API_KEY', None))

def check_epoch():
    key = get_api_key('abel')
    if not key:
        return None
    url = "https://gateway.nookplot.com/v1/mining/epoch"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)',
        'Accept': 'application/json',
        'Authorization': f'Bearer {key}'
    })
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        return data.get('epoch', {})
    except Exception as e:
        log(f"Epoch check failed: {e}")
        return None

def mine_wallet(wallet):
    """Mine one challenge from wallet, return success/fail"""
    result = subprocess.run(
        ['bash', '-c', f'cd /home/ryzen/nookplot-{wallet} && source .env && timeout 60 nookplot mine --once 2>&1'],
        capture_output=True, text=True, timeout=90
    )
    output = result.stdout + result.stderr
    
    if 'Rate limited' in output and '429' in output:
        return 'rate_limited'
    elif 'Maximum 12' in output or 'epoch' in output.lower():
        return 'epoch_cap'
    elif 'solved' in output.lower() or 'submitted' in output.lower():
        return 'success'
    elif 'already submitted' in output.lower() or '409' in output:
        return 'already_done'
    else:
        return f'unknown: {output[:100]}'

def main():
    log("=" * 60)
    log("Mining watchdog started")
    
    epoch = check_epoch()
    if not epoch:
        log("Cannot check epoch, aborting")
        return
    
    status = epoch.get('status', 'unknown')
    epoch_num = epoch.get('epochNumber', '?')
    log(f"Epoch {epoch_num}: {status}")
    
    if status == 'closed':
        log("Epoch closed, nothing to do")
        return
    
    log("EPOCH OPEN! Starting sequential mining...")
    
    results = {}
    for wallet in WALLETS:
        log(f"Mining {wallet}...")
        result = mine_wallet(wallet)
        results[wallet] = result
        log(f"  {wallet}: {result}")
        
        if result == 'rate_limited':
            log("Rate limited! Waiting 60s...")
            time.sleep(60)
            # Retry once
            result = mine_wallet(wallet)
            results[wallet] = result
            log(f"  {wallet} retry: {result}")
            
            if result == 'rate_limited':
                log("Still rate limited, aborting this run")
                break
        
        time.sleep(15)  # Gap between wallets
    
    # Summary
    success = sum(1 for v in results.values() if v == 'success')
    caps = sum(1 for v in results.values() if v == 'epoch_cap')
    log(f"Results: {success} success, {caps} capped, {len(results)} attempted")
    log("=" * 60)

if __name__ == '__main__':
    main()
