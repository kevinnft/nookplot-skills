#!/usr/bin/env python3
"""
Fast claimable-balance snapshot across the full Nookplot wallet cluster.

Designed for the recurring user question: "ada reward unlock gak" /
"cek claimable" / "ada yang bisa di-claim?". Lighter than audit_cluster.py —
ONLY hits check_mining_rewards per wallet (1 call/wallet, no submission walk,
no leaderboard, no guild query). Returns in ~5-10s for the 9-wallet cluster.

Pitfalls embedded:
  - Wallets file is ~/.hermes/nookplot_wallets.json (FLAT, no subfolder).
    Do NOT look under ~/.hermes/nookplot/wallets.json — that path doesn't exist.
  - Gateway host is gateway.nookplot.com (NOT api.nookplot.com — that DNS
    is NXDOMAIN). Direct GET /v1/mining/rewards/me returns 404 — must go
    through /v1/actions/execute toolName=check_mining_rewards.
  - claimableBalance ALWAYS exposes 3 keys: epoch_solving,
    epoch_verification, guild_inference_claim (value 0 when nothing).
    dataset_royalty / authorship / posting are NOT in this response —
    they only show up in lifetime totalEarned reconciliation, not here.
  - tier=none + multiplier=1 in this response = STAKING tier (user does
    not stake). Guild multiplier (1.35x / 1.6x) is baked into totalEarned
    at submit time and is NOT a separate field here. Do not confuse the
    two when reporting.

Usage:
  python3 cluster_claimable_snapshot.py            # table
  python3 cluster_claimable_snapshot.py --json     # JSON
"""
import json, subprocess, argparse, sys, os

GW = "https://gateway.nookplot.com"
WALLETS_PATH = os.path.expanduser("~/.hermes/nookplot_wallets.json")


def exec_tool(key, name, args=None, timeout=25):
    payload = json.dumps({"toolName": name, "args": args or {}})
    r = subprocess.run(
        ["curl", "-s",
         "-H", f"Authorization: Bearer {key}",
         "-H", "Content-Type: application/json",
         "-d", payload, f"{GW}/v1/actions/execute"],
        capture_output=True, text=True, timeout=timeout,
    )
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"error": r.stdout[:200]}


def snapshot(label, w):
    key = w["apiKey"]
    name = (w.get("displayName") or "?")[:10]
    out = {"L": label, "name": name}
    r = exec_tool(key, "check_mining_rewards")
    if r.get("status") != "completed":
        out["err"] = str(r)[:120]
        return out
    res = r.get("result") or {}
    cb = res.get("claimableBalance") or {}
    out["tier"] = res.get("tier", "?")  # STAKING tier, not guild
    out["mult"] = res.get("multiplier", 1)
    out["solves"] = res.get("totalSolves", 0)
    out["lifetime"] = res.get("totalEarned", 0) or 0
    out["epoch_solving"] = float(cb.get("epoch_solving", 0) or 0)
    out["epoch_verification"] = float(cb.get("epoch_verification", 0) or 0)
    out["guild_inference"] = float(cb.get("guild_inference_claim", 0) or 0)
    out["pending"] = float(res.get("pendingRewards", 0) or 0)
    out["claimable_total"] = (
        out["epoch_solving"] + out["epoch_verification"] + out["guild_inference"]
    )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wallets", default=WALLETS_PATH)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    data = json.load(open(args.wallets))
    rows = [snapshot(k, data[k]) for k in sorted(data.keys())]

    if args.json:
        print(json.dumps(rows, indent=2, default=str))
        return

    def fmt(n):
        return f"{n:,.2f}" if n else "-"

    print(f"\n{'W':<3} {'name':<10} {'tier':<5} {'solves':>6} {'lifetime':>14} "
          f"{'epochSolve':>11} {'epochVer':>10} {'guildInf':>11} {'CLAIMABLE':>11}")
    print("-" * 100)
    g_life = g_claim = 0.0
    any_claimable = False
    for r in rows:
        if "err" in r:
            print(f"{r['L']:<3} {r['name']:<10} ERR {r['err']}")
            continue
        g_life += r["lifetime"]
        g_claim += r["claimable_total"]
        if r["claimable_total"] > 0:
            any_claimable = True
        print(f"{r['L']:<3} {r['name']:<10} {r['tier']:<5} {r['solves']:>6} "
              f"{fmt(r['lifetime']):>14} {fmt(r['epoch_solving']):>11} "
              f"{fmt(r['epoch_verification']):>10} {fmt(r['guild_inference']):>11} "
              f"{fmt(r['claimable_total']):>11}")
    print("-" * 100)
    print(f"Cluster lifetime earned : {g_life:>14,.2f} NOOK")
    print(f"Claimable RIGHT NOW     : {g_claim:>14,.2f} NOOK")
    if not any_claimable:
        print("\n→ Nothing to claim. Next unlock:")
        print("  • epoch_solving / epoch_verification → next epoch finalize (UTC midnight)")
        print("  • guild_inference_claim (W3 SatsAgent) → guild #100000 drip, poll 1-2h")


if __name__ == "__main__":
    main()
