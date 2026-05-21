#!/usr/bin/env python3
"""Cluster-wide breakdown snapshot. Tabular per-wallet view of all 10 dimensions.

Phase 0 of the cluster gas-maks pipeline. Run before AND after each burst
to compute deltas and verify settlement.

Usage: python check_breakdown.py [outfile]
"""
import os, json, subprocess, sys

WALLETS = json.load(open(os.path.expanduser("~/.hermes/nookplot_wallets.json")))
GW = "https://gateway.nookplot.com"

def curl(url, key):
    r = subprocess.run(
        ["curl", "-sS", "-H", f"Authorization: Bearer {key}", "--max-time", "20", url],
        capture_output=True, text=True, timeout=25,
    )
    return r.stdout

print(f"{'W':<3} {'addr':<14} {'name':<10} "
      f"{'exec':<6} {'commits':<8} {'lines':<8} {'projects':<10} "
      f"{'social':<8} {'content':<8} {'collab':<8} {'launches':<10} "
      f"{'citations':<10} {'mktp':<6} {'total':<8}")
print("-" * 140)

for k in sorted(WALLETS.keys()):
    w = WALLETS[k]
    addr = w["addr"]
    key = w.get("apiKey")
    if not key:
        print(f"{k}\t{addr[:12]}\tNO_KEY")
        continue
    out = curl(f"{GW}/v1/contributions/{addr}", key)
    try:
        d = json.loads(out)
    except Exception:
        d = {"_raw": out[:120]}
    bd = d.get("breakdown", {}) if isinstance(d, dict) else {}
    score = d.get("score", d.get("totalScore", "?"))
    row = [k, addr[:12], w.get("displayName", "")[:10],
           bd.get("exec", "—"), bd.get("commits", "—"), bd.get("lines", "—"),
           bd.get("projects", "—"), bd.get("social", "—"), bd.get("content", "—"),
           bd.get("collab", "—"), bd.get("launches", "—"),
           bd.get("citations", "—"), bd.get("marketplace", "—"), score]
    print("  ".join(str(c) for c in row))
