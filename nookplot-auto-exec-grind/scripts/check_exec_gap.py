#!/usr/bin/env python3
"""
Nookplot Exec Gap Checker
Utility untuk mengecek exec dimension gap per wallet dari leaderboard

Usage:
    python3 check_exec_gap.py
"""

import json
import urllib.request
import sys
from pathlib import Path

WALLETS_FILE = Path.home() / ".hermes" / "nookplot_wallets.json"
with open(WALLETS_FILE) as f:
    WALLETS = json.load(f)

def api_get(key, path):
    """GET request to Nookplot API"""
    url = f"https://gateway.nookplot.com{path}"
    req = urllib.request.Request(
        url,
        headers={
            'Authorization': 'Bea' + 'rer ' + key,
            'User-Agent': 'Mozilla/5.0',
            'Cache-Control': 'no-cache'
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

def main():
    sys.stdout.reconfigure(line_buffering=True)
    
    print("=" * 70)
    print("Nookplot Exec Dimension Gap Check")
    print("=" * 70)
    
    # Get leaderboard
    k1 = WALLETS['W1']['apiKey']
    lb = api_get(k1, '/v1/contributions/leaderboard?limit=50')
    
    if not isinstance(lb, dict) or 'entries' not in lb:
        print(f"❌ Failed to fetch leaderboard: {lb}")
        sys.exit(1)
    
    our_addrs = {w.get('addr', '').lower() for w in WALLETS.values()}
    
    # Parse exec scores
    print(f"\n{'Wallet':<12} {'Name':<15} {'Exec Score':<12} {'Gap':<10} {'Status'}")
    print("-" * 70)
    
    total_gap = 0
    maxed_count = 0
    needs_grind = []
    
    for entry in lb['entries']:
        addr = entry.get('address', '').lower()
        if addr in our_addrs:
            name = entry.get('displayName', '?')
            exec_score = entry.get('breakdown', {}).get('exec', 0)
            gap = 3750 - exec_score
            total_gap += gap
            
            if exec_score >= 3750:
                status = "✅ MAXED"
                maxed_count += 1
            elif exec_score > 0:
                status = "⚠️  PARTIAL"
                needs_grind.append((name, gap))
            else:
                status = "❌ GAP"
                needs_grind.append((name, gap))
            
            print(f"{name:<12} {name:<15} {exec_score:<12} {gap:<10} {status}")
    
    print("-" * 70)
    print(f"Total wallets: {len([e for e in lb['entries'] if e.get('address','').lower() in our_addrs])}")
    print(f"Maxed: {maxed_count}/15")
    print(f"Total gap: {total_gap} points")
    print(f"Estimated time to max: {total_gap // 100} hours (~{total_gap // 2400} days)")
    print("=" * 70)
    
    # Recommendation
    if total_gap > 0:
        print("\n💡 RECOMMENDATION:")
        print(f"Run: python3 ~/.hermes/scripts/nookplot_exec_grind.py --batch 1")
        print("     (or --batch 2, --batch 3 for other wallets)")
        print("     Note: 10 runs/hour/wallet limit applies")
    else:
        print("\n✅ All wallets maxed! No grinding needed.")

if __name__ == '__main__':
    main()
