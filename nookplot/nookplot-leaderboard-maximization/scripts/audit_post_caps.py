#!/usr/bin/env python3
"""Audit per-wallet posting-cap state. CORRECT version — filters out
guild_cross_synthesis items (posterAddress=null) that the gateway returns for
every guild-member wallet via `myOwn=true`.

Counts only challenges where posterAddress.lower() matches wallet.addr.lower().

Output table:
  W   name      24h_owned  free_slots  oldest_in_window (UTC)  unlock_at (WIB)

unlock_at = oldest_in_window + 24h, displayed in WIB (UTC+7). When a wallet
has no posts in the window, oldest_in_window is "-" and unlock_at is "now".

Usage: python3 audit_post_caps.py
"""
import json, subprocess
from datetime import datetime, timezone, timedelta

WALLETS_PATH = "/home/asus/.hermes/nookplot_wallets.json"
GW = "https://gateway.nookplot.com"


def main():
    wallets = json.load(open(WALLETS_PATH))
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=24)

    print(f"Now:    {now.isoformat()}")
    print(f"Cutoff: {cutoff.isoformat()}")
    print()
    print(f"{'W':<4}{'name':<10}{'24h_owned':<11}{'free_slots':<12}"
          f"{'oldest_in_window (UTC)':<26}{'unlock_at (WIB)':<22}")
    print("-" * 90)

    cluster_used = 0
    cluster_open = 0

    for wkey, w in wallets.items():
        auth = "Authorization: Bearer " + w['apiKey']
        addr_lower = w['addr'].lower()
        url = GW + '/v1/mining/challenges?postedBy=' + w['addr'] + '&limit=50&status=all'
        cmd = ['curl', '-s', url, '-H', auth]
        chs = []
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            d = json.loads(r.stdout)
            if isinstance(d, dict):
                chs = d.get('challenges', d.get('items', []))
            elif isinstance(d, list):
                chs = d
        except Exception:
            pass

        owned = []
        for c in chs:
            pa = (c.get('posterAddress') or '').lower()
            if pa != addr_lower:
                # Skip system-generated (null) and other-wallet posts.
                continue
            ts = c.get('createdAt', '')
            try:
                t = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                if t >= cutoff:
                    owned.append(t)
            except Exception:
                pass

        owned.sort()
        used = len(owned)
        free = max(0, 10 - used)
        cluster_used += used
        cluster_open += free

        if owned:
            oldest = owned[0]
            unlock_wib = oldest + timedelta(hours=24 + 7)
            oldest_str = oldest.strftime('%Y-%m-%d %H:%M UTC')
            unlock_str = unlock_wib.strftime('%m-%d %H:%M WIB')
        else:
            oldest_str = "-"
            unlock_str = "now"

        print(f"{wkey:<4}{w.get('displayName','?'):<10}{used:<11}"
              f"{free:<12}{oldest_str:<26}{unlock_str:<22}")

    print("-" * 90)
    print(f"CLUSTER  used={cluster_used}/100  free_slots={cluster_open}")


if __name__ == '__main__':
    main()
