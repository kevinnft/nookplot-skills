#!/usr/bin/env python3
"""Cluster-wide audit probe for the multi-wallet Nookplot setup.

Reads creds from /tmp/wN_creds.json + ~/.env (W2), prints:
  - Per-wallet score, breakdown, leaderboard rank
  - Per-dim cluster headroom (sum vs cap*N_wallets)
  - Mining stake / claimable rewards / pending rewards
  - Daily relay budget status (single cheap probe per wallet)
  - Open verifiable submissions: total + external (cluster-excluded)

When the user says "cek ulang" / "sudah maks" / "audit cluster" — run this.
The output is the right shape to feed the "Reporting pattern for 'sudah maks?'"
audit table (see SKILL.md) without rebuilding the probe each session.

Usage:
  python3 scripts/cluster_audit.py            # full audit
  python3 scripts/cluster_audit.py --probe    # also probe relay budget (uses 1 prep per wallet, no relay)

Wallet credentials format:
  /tmp/w1_creds.json: {"key": "nk_...", "addr": "0x..."}
  /tmp/w3_creds.json+: {"pk": "0x...", "addr": "0x...", "apiKey": "nk_..."}
  ~/.env:             NOOKPLOT_API_KEY, NOOKPLOT_AGENT_ADDRESS, NOOKPLOT_AGENT_PRIVATE_KEY
"""
import json, subprocess, sys, os, glob

GW = "https://gateway.nookplot.com"

CAPS = {
    "commits": 6250, "exec": 3750, "projects": 5000, "lines": 3750,
    "collab": 5000, "content": 5000, "social": 2500, "marketplace": 1250,
    "citations": 3750, "launches": 1250,
}


def call(key, path, method="GET", payload=None, t=15):
    cmd = ["curl", "-sS", "-X", method, f"{GW}{path}",
           "-H", f"Authorization: Bearer {key}",
           "-H", "Content-Type: application/json",
           "--max-time", str(t)]
    if payload is not None:
        cmd += ["-d", json.dumps(payload)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=t + 5)
        return json.loads(r.stdout) if r.stdout.strip() else {"_err": "empty"}
    except Exception as e:
        return {"_err": str(e)[:200]}


def load_wallets():
    wallets = []
    # W1 (MCP-bound, JSON shape: {key, addr, name})
    if os.path.exists("/tmp/w1_creds.json"):
        w1 = json.load(open("/tmp/w1_creds.json"))
        wallets.append({"label": "W1", "name": w1.get("name", "w1"),
                        "addr": w1["addr"], "key": w1["key"]})
    # W2 from ~/.env
    env = subprocess.run(
        ["bash", "-c",
         "source ~/.env 2>/dev/null && echo $NOOKPLOT_API_KEY,$NOOKPLOT_AGENT_ADDRESS,$NOOKPLOT_AGENT_PRIVATE_KEY"],
        capture_output=True, text=True
    ).stdout.strip().split(",")
    if env and env[0]:
        wallets.append({"label": "W2", "name": "w2",
                        "addr": env[1], "key": env[0],
                        "pk": env[2] if len(env) > 2 else None})
    # W3+: shape {pk, addr, apiKey, did, displayName?}
    for path in sorted(glob.glob("/tmp/w[3-9]_creds.json")):
        n = path.split("w")[1].split("_")[0]
        c = json.load(open(path))
        wallets.append({
            "label": f"W{n}",
            "name": c.get("displayName", c.get("wallet", f"w{n}")),
            "addr": c["addr"],
            "key": c["apiKey"],
            "pk": c.get("pk"),
        })
    return wallets


def main():
    probe_relay = "--probe" in sys.argv
    wallets = load_wallets()
    if not wallets:
        print("No wallets found. Expected /tmp/wN_creds.json or ~/.env.")
        sys.exit(1)

    self_addrs = {w["addr"].lower() for w in wallets}
    primary_key = wallets[0]["key"]

    # Leaderboard ranks
    lb = call(primary_key, "/v1/contributions/leaderboard?limit=200")
    ranks = {(e.get("address") or "").lower(): i
             for i, e in enumerate(lb.get("entries", []), 1)}

    print("=" * 76)
    print(f"=== {len(wallets)}-WALLET CLUSTER AUDIT ===")
    print("=" * 76)

    cluster_totals = {k: 0 for k in CAPS}
    total_score = 0

    print(f"\n{'Wallet':<6} {'Name':<12} {'Score':<7} {'Rank':<5} {'computedAt':<20}")
    print("-" * 76)
    for w in wallets:
        c = call(w["key"], f"/v1/contributions/{w['addr']}")
        score = c.get("score", 0)
        bd = c.get("breakdown", {})
        for k, v in bd.items():
            if k in cluster_totals:
                cluster_totals[k] += int(v)
        total_score += score
        rank = ranks.get(w["addr"].lower(), "?")
        ca = (c.get("computedAt", "") or "")[:19]
        print(f"  {w['label']:<4} {w['name'][:11]:<12} {score:<7} #{rank:<4} {ca}")

    print(f"\n  CLUSTER TOTAL: {total_score}")

    print(f"\n{'Dim':<13} {'Sum':<8} {'Cap':<8} {'Pct':<7} Headroom")
    print("-" * 50)
    raw = 0
    raw_max = 0
    for k, cap in CAPS.items():
        cur = cluster_totals[k]
        max_ = cap * len(wallets)
        pct = 100 * cur / max_ if max_ else 0
        head = max_ - cur
        raw += cur
        raw_max += max_
        bar = "✓" if head == 0 else " "
        print(f"  {k:<11} {cur:>6}  {max_:>6}  {pct:5.1f}%  {head:<6} {bar}")
    print(f"\n  RAW {raw}/{raw_max} ({100*raw/raw_max:.1f}%)")
    print(f"  ×1.3 velocity: ~{int(raw*1.3)} predicted cluster total")

    # Mining rewards
    print("\n=== MINING REWARDS ===")
    for w in wallets:
        rw = call(w["key"], "/v1/mining/rewards")
        cb = rw.get("claimableBalance", {})
        pe = rw.get("pendingRewards", 0)
        ts = rw.get("totalSolves") or rw.get("total_solves")
        te = rw.get("totalEarned") or rw.get("total_earned")
        print(f"  {w['label']:<4} solves={ts} earned={te} claimable={cb} pending={pe}")

    # External verifiable submissions
    print("\n=== VERIFIABLE QUEUE (external candidates per wallet) ===")
    for w in wallets:
        v = call(w["key"], "/v1/mining/submissions/verifiable?limit=80")
        subs = v.get("submissions", []) if isinstance(v, dict) else []
        ext = [s for s in subs
               if (s.get("solver_address") or s.get("solverAddress", "")).lower()
               not in self_addrs]
        print(f"  {w['label']:<4} total={len(subs):<3} external={len(ext)}")

    # Optional relay budget probe
    if probe_relay:
        print("\n=== RELAY BUDGET PROBE (one prep call per wallet, no signing) ===")
        # Use a known address as a sentinel target; we never sign+relay
        sentinel = "0xREDACTED_WALLET_40CHARS"
        for w in wallets:
            r = call(w["key"], "/v1/prepare/follow", "POST",
                     {"target": sentinel}, t=10)
            if "forwardRequest" in r:
                print(f"  {w['label']:<4} prepare/follow OK  → relay path open")
            elif "Already following" in str(r.get("error", "")):
                print(f"  {w['label']:<4} prepare/follow OK (target already followed) → relay path open")
            elif "Daily relay limit" in str(r.get("error", "")):
                print(f"  {w['label']:<4} TIER-1 DAILY CAP HIT (off-chain only)")
            elif "insufficient" in str(r.get("error", "")).lower():
                print(f"  {w['label']:<4} GATEWAY INSUFFICIENT FUNDS (operator-side)")
            else:
                print(f"  {w['label']:<4} prep err: {r.get('error') or r.get('_err')}")


if __name__ == "__main__":
    main()
