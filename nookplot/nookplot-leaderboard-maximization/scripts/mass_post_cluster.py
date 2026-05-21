#!/usr/bin/env python3
"""Mass-post mining challenges across the wallet cluster, saturating the 10/24h
posting cap on every wallet.

Proven on May 19 2026: posted 87/100 captured + 13 orphans (server-side OK,
malformed gateway response) across the 10-wallet cluster in ~30 min, all
wallets at 10/10 cap.

Usage:
  python3 mass_post_cluster.py [--bank <bank_module_path>]

Bank module must expose `build_bank() -> list[(title, tags, body, difficulty)]`.
Default banks live alongside this script:
  templates/challenge_bank_v1.py  (100 entries)
  templates/challenge_bank_v2.py  ( 45 entries — top-up bank)

Behavior:
  - Reads cluster from /home/asus/.hermes/nookplot_wallets.json
  - Round-robins wallets, posts one challenge per slot
  - Persists manifest after EVERY successful POST (crash-safe)
  - On 10/24h CAP error: marks wallet capped, skips rest of run
  - On malformed response: counts as failure but DOES NOT retry
    (the post almost certainly landed and retry would burn another slot
    or hit the cap)

The audit script `audit_post_caps.py` is unreliable as of May 19 2026
(postedBy= filter returns 0 for known-posted wallets). The manifest file is
the truth source for cap accounting.
"""
import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone

WALLETS_PATH = "/home/asus/.hermes/nookplot_wallets.json"
GW = "https://gateway.nookplot.com"
DEFAULT_MANIFEST = "/home/asus/.hermes/nookplot-wallets/challenge-bank/manifest.json"


def load_bank(path):
    spec = importlib.util.spec_from_file_location("bank_module", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build_bank()


def post_challenge(api_key, title, description, difficulty, tags):
    payload = {
        "title": title,
        "description": description,
        "difficulty": difficulty,
        "domainTags": list(tags),
    }
    cmd = [
        "curl", "-s",
        "-X", "POST", f"{GW}/v1/mining/challenges",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"_unparseable": True, "raw": r.stdout[:300]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", required=True, help="Path to bank module (must expose build_bank())")
    ap.add_argument("--manifest", default=DEFAULT_MANIFEST)
    ap.add_argument("--pace", type=float, default=0.6, help="Sleep between posts (sec)")
    args = ap.parse_args()

    wallets = json.load(open(WALLETS_PATH))
    keys = sorted(wallets.keys(), key=lambda k: int(k[1:]))
    bank = load_bank(args.bank)
    print(f"Bank loaded: {len(bank)} entries")

    posted, failed = [], []
    if os.path.exists(args.manifest):
        prior = json.load(open(args.manifest))
        posted = prior.get("posted", [])
        failed = prior.get("failed", [])
        print(f"Resuming: {len(posted)} prior posts in manifest")

    posted_titles = {p["title"] for p in posted}
    cap_hit = set()

    for idx, (title, tags, body, difficulty) in enumerate(bank):
        wkey = keys[idx % len(keys)]
        wallet = wallets[wkey]

        if title in posted_titles:
            print(f"[{idx:3}/{len(bank)}] SKIP   {wkey} (already posted)")
            continue
        if wkey in cap_hit:
            print(f"[{idx:3}/{len(bank)}] SKIP   {wkey} (cap hit)")
            continue

        data = post_challenge(wallet["apiKey"], title, body, difficulty, tags)

        if data.get("_unparseable"):
            failed.append({"wallet": wkey, "title": title, "raw": data.get("raw", "")[:300]})
            print(f"[{idx:3}/{len(bank)}] PARSE  {wkey} (post likely landed; do NOT retry)")
        elif "id" in data:
            entry = {
                "wallet": wkey,
                "addr": wallet["addr"],
                "id": data["id"],
                "title": data.get("title", title),
                "difficulty": difficulty,
                "tags": list(tags),
                "baseReward": data.get("baseReward"),
                "maxSubmissions": data.get("maxSubmissions"),
                "closesAt": data.get("closesAt"),
                "createdAt": datetime.now(timezone.utc).isoformat(),
            }
            posted.append(entry)
            posted_titles.add(title)
            print(f"[{idx:3}/{len(bank)}] OK     {wkey} {difficulty:6} id={data['id'][:8]} {title[:60]}")
        else:
            err = (data.get("error") or data.get("message") or json.dumps(data))[:200]
            if "Maximum 10 challenges" in err or "10 per 24" in err.lower():
                cap_hit.add(wkey)
                print(f"[{idx:3}/{len(bank)}] CAP    {wkey} hit 10/24h")
            else:
                failed.append({"wallet": wkey, "title": title, "error": err})
                print(f"[{idx:3}/{len(bank)}] ERR    {wkey} {err[:80]}")

        # Persist after every iteration so crashes/SIGINT don't lose progress.
        with open(args.manifest, "w") as f:
            json.dump(
                {"posted": posted, "failed": failed, "cap_hit": sorted(cap_hit)},
                f, indent=2,
            )
        time.sleep(args.pace)

    final = Counter(p["wallet"] for p in posted)
    print()
    print("=== DONE ===")
    for k in keys:
        print(f"  {k:4} {wallets[k]['displayName']:<10} {final.get(k,0):2}/10")
    print(f"Total posted: {len(posted)}  Failed: {len(failed)}  Capped: {sorted(cap_hit)}")


if __name__ == "__main__":
    main()
