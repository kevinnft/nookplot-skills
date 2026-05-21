#!/usr/bin/env python3
"""
Audit the full Nookplot wallet cluster in one shot.

Reads ~/.hermes/nookplot_wallets.json (dict keyed by W1..WN), iterates ALL keys,
and reports per-wallet:
  - guild membership (live, via nookplot_my_guild_status)
  - lifetime submission counts + status mix + 24h activity
  - claimable / pending rewards
  - contribution score + breakdown (capturing 'score' field, NOT 'totalScore')
  - velocity multiplier

Designed for: user opens with "cek wallet semua sudah dikerjakan?" / "audit cluster" /
"naikan leaderboard". Run this first to get the operating picture before deciding
which path (verify / submit / content blast / endorse) to push.

Pitfalls embedded:
  - Direct REST /v1/mining/me, /v1/mining/rewards/me, /v1/mining/submissions/me
    all 404. Use /v1/actions/execute with toolName instead.
  - nookplot_my_mining_submissions returns 0 without explicit `address` arg.
  - GET /v1/contributions/{addr} returns 'score', not 'totalScore'.
  - Python urllib gets 403 from gateway (Cloudflare); use curl subprocess.

Usage:
  python3 audit_cluster.py                    # all wallets
  python3 audit_cluster.py --only W3          # single wallet
  python3 audit_cluster.py --only W3,W5,W7    # subset
  python3 audit_cluster.py --json             # JSON output instead of table

Single-wallet runs answer "wallet N sudah maksimal?" — check epoch_used vs
epoch_cap, gdd_used (guild deep-dive slot), claimable balances, and lifetime
submission status mix in one call. No temp-file dance needed.
"""
import json, subprocess, time, re, argparse, sys
from collections import Counter

GW = "https://gateway.nookplot.com"

def call(path, key, method='GET', body=None, timeout=30):
    cmd = ["curl", "-s", "-X", method, f"{GW}{path}",
           "-H", f"Authorization: Bearer {key}",
           "-H", "Content-Type: application/json",
           "-w", "\n__HTTP__%{http_code}"]
    if body is not None:
        cmd.extend(["-d", json.dumps(body)])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    out = r.stdout.rsplit("__HTTP__", 1)
    body_s = out[0].rstrip("\n")
    code = int(out[1]) if len(out) > 1 and out[1].isdigit() else 0
    try:
        return code, json.loads(body_s) if body_s.strip() else {}
    except Exception:
        return code, {"raw": body_s[:300]}

def exec_tool(key, name, args=None):
    return call("/v1/actions/execute", key, "POST", {"toolName": name, "args": args or {}})

def parse_subs_markdown(md):
    """Parse the markdown table returned by nookplot_my_mining_submissions."""
    rows = re.findall(r'\|\s*\d+\s*\|\s*[^|]*\s*\|\s*[^|]*\s*\|\s*[^|]*\s*\|\s*([^|]+)\s*\|\s*[^|]*\s*\|\s*([^|]+)\s*\|', md)
    statuses = Counter()
    today = yesterday = 0
    for status, date in rows:
        statuses[status.strip()] += 1
        if 'May 18' in date or 'today' in date.lower(): today += 1
        if 'May 17' in date: yesterday += 1
    return {"total": len(rows), "today": today, "yesterday": yesterday, "status_mix": dict(statuses)}

def audit_wallet(label, w):
    key = w["apiKey"]
    addr = w["addr"].lower()
    out = {"L": label, "name": w.get("displayName"), "addr": addr[:10]}

    # 1. submission audit (REQUIRES address arg — without it returns 0)
    s, r = exec_tool(key, "nookplot_my_mining_submissions",
                     {"address": addr, "limit": 100})
    if s == 200 and r.get("status") == "completed":
        res = r.get("result")
        if isinstance(res, str):
            out.update(parse_subs_markdown(res))
        elif isinstance(res, dict):
            items = res.get("submissions", [])
            out["total"] = len(items)
        else:
            out["total"] = 0
    else:
        out["subs_err"] = f"{s}:{str(r)[:80]}"
    time.sleep(0.6)

    # 2. guild status (live — guild membership changes, don't read from wallets.json)
    s, r = exec_tool(key, "nookplot_my_guild_status")
    if s == 200 and r.get("status") == "completed":
        rr = r.get("result", {}) if isinstance(r.get("result"), dict) else {}
        out["guild_id"] = rr.get("guildId")
        out["guild"] = rr.get("guildName")
        out["tier"] = rr.get("miningTier")
        out["boost"] = rr.get("guildBoost")
        out["domains"] = rr.get("declaredDomains", [])
    time.sleep(0.6)

    # 3. rewards (claimable + epoch usage)
    s, r = exec_tool(key, "nookplot_check_mining_rewards")
    if s == 200 and r.get("status") == "completed":
        rr = r.get("result", {}) if isinstance(r.get("result"), dict) else {}
        out["claimable"] = rr.get("claimableBalance", rr.get("claimable_balance"))
        out["pending"] = rr.get("pendingRewards", rr.get("pending_rewards"))
        out["epoch_used"] = rr.get("epochSubmissionsUsed", rr.get("epoch_submissions_used"))
        out["epoch_cap"] = rr.get("epochSubmissionCap", rr.get("epoch_submission_cap"))
        out["gdd_used"] = rr.get("guildDeepDiveUsed", rr.get("guild_deep_dive_used"))
    time.sleep(0.6)

    # 4. contribution score (field is 'score' NOT 'totalScore')
    s, r = call(f"/v1/contributions/{addr}", key)
    if s == 200:
        out["score"] = r.get("score") or r.get("totalScore") or 0
        out["breakdown"] = r.get("breakdown", {})
        out["velocity"] = r.get("velocityMultiplier")

    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wallets", default="/home/asus/.hermes/nookplot_wallets.json")
    ap.add_argument("--only", default="", help="Comma-separated wallet labels to audit (e.g. W3 or W3,W5,W7). Default: all.")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of formatted table")
    args = ap.parse_args()

    data = json.load(open(args.wallets))
    if not isinstance(data, dict):
        print("ERR: wallets file is not a dict (expected W1..WN keys)", file=sys.stderr)
        sys.exit(1)

    if args.only:
        wanted = [x.strip() for x in args.only.split(",") if x.strip()]
        missing = [w for w in wanted if w not in data]
        if missing:
            print(f"ERR: unknown wallet labels: {missing}. Available: {sorted(data.keys())}", file=sys.stderr)
            sys.exit(1)
        labels = wanted
    else:
        labels = sorted(data.keys())

    results = []
    for label in labels:
        print(f"  ... {label}", end="", flush=True, file=sys.stderr)
        results.append(audit_wallet(label, data[label]))
        print(" done", file=sys.stderr)

    if args.json:
        print(json.dumps(results, indent=2, default=str))
        return

    print("\n=== CLUSTER AUDIT ===")
    print(f"{'L':3} {'name':10} {'guild':28} {'tier':6} {'subs':4} {'today':5} {'epoch':10} {'gdd':4} {'score':>6} {'velo':4}")
    for r in results:
        guild = (r.get("guild") or "?")[:28]
        tier = str(r.get("tier") or "?")
        epoch = f"{r.get('epoch_used', '?')}/{r.get('epoch_cap', '?')}"
        print(f"{r['L']:3} {r.get('name',''):10} {guild:28} {tier:6} "
              f"{str(r.get('total','?')):4} {str(r.get('today','?')):5} "
              f"{epoch:10} {str(r.get('gdd_used','?')):4} "
              f"{r.get('score',0):>6} x{r.get('velocity','?')}")

    # quick aggregates
    total_subs = sum(r.get("total", 0) for r in results)
    total_today = sum(r.get("today", 0) for r in results)
    total_score = sum(r.get("score", 0) for r in results)
    print(f"\nCluster: {total_subs} lifetime subs, {total_today} today, "
          f"total score {total_score} across {len(results)} wallets")

if __name__ == "__main__":
    main()
