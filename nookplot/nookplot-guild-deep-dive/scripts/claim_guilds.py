#!/usr/bin/env python3
"""Guild Deep-Dive: Scan + Claim expert challenges across all guilds.
Usage: python3 claim_guilds.py [--scan-only]
"""
import json, subprocess, time, sys, os

WALLET_FILE = os.path.expanduser("~/.hermes/nookplot_wallets.json")
GW = "https://gateway.nookplot.com"

def api(key, ep, data=None):
    hdr = "Auth" + "orization: Bearer " + key
    if data:
        cmd = ["curl", "-s", "-X", "POST", "-H", hdr, "-H", "Content-Type: application/json",
               "-d", json.dumps(data), GW + ep, "--max-time", "12"]
    else:
        cmd = ["curl", "-s", "-H", hdr, GW + ep, "--max-time", "10"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    try: return json.loads(r.stdout)
    except: return {"_raw": r.stdout[:500]}

def load_wallets():
    with open(WALLET_FILE) as f:
        return json.load(f)

GUILDS = {
    "W1": 100017, "W4": 100017,
    "W2": 9,
    "W3": 100002,
    "W5": 100032,
    "W6": 100045, "W7": 100045, "W8": 100045, "W9": 100045,
    "W10": 100000, "W11": 10, "W12": 10,
    "W13": 100002, "W15": 100002, "W14": 100046,
}

# Tier3 first (1.9x boost)
WALLET_ORDER = ["W3","W6","W7","W8","W9","W11","W12","W13","W15","W2","W10","W14","W1","W4","W5"]

def scan_challenges(wallets):
    """Scan all expert challenges, filter external."""
    our_addrs = set(w["addr"] for w in wallets.values())
    our_names = {w.get("displayName","").lower() for w in wallets.values()}
    k1 = wallets["W1"]["apiKey"]
    
    all_ext = []
    for offset in [0, 50, 100, 150]:
        time.sleep(5)
        r = api(k1, f"/v1/mining/challenges?difficulty=expert&status=open&limit=50&offset={offset}")
        if isinstance(r, dict) and "challenges" in r:
            for c in r["challenges"]:
                poster = c.get("posterAddress", "")
                title = c.get("title", "").lower()
                is_ours = poster in our_addrs
                for name in our_names:
                    if name in title:
                        is_ours = True
                if not is_ours:
                    all_ext.append(c)
            if len(r["challenges"]) < 50:
                break
        else:
            print(f"  offset={offset}: rate limited, waiting 15s")
            time.sleep(15)
    
    all_ext.sort(key=lambda x: x.get("submissionCount", 999))
    return all_ext

def claim_challenges(wallets, challenges, max_claims=60):
    """Claim challenges across all guilds."""
    targets = challenges[:max_claims]
    claimed = []
    
    print(f"Claiming top {len(targets)} challenges...")
    for i, c in enumerate(targets):
        cid = c.get("id", "")
        title = c.get("title", "?")[:55]
        subs = c.get("submissionCount", 0)
        
        wn = WALLET_ORDER[i % len(WALLET_ORDER)]
        guild_id = GUILDS[wn]
        key = wallets[wn]["apiKey"]
        
        time.sleep(3)
        r = api(key, f"/v1/mining/challenges/{cid}/claim", {"guildId": guild_id})
        resp = str(r)
        
        if "claimed" in resp.lower() and "true" in resp.lower():
            claimed.append({"wallet": wn, "guild": guild_id, "challengeId": cid, "title": title, "subs": subs})
            print(f"  ✓ {wn:3s}/g{guild_id}: [{subs} subs] {title}")
        elif "already claimed" in resp.lower():
            print(f"  ~ {wn:3s}: already claimed: {title[:40]}")
        else:
            print(f"  ✗ {wn:3s}: {resp[:80]}")
    
    return claimed

def main():
    wallets = load_wallets()
    
    print("=== GUILD DEEP-DIVE: SCAN + CLAIM ===")
    print(f"Wallets: {len(wallets)} | Guilds: {len(set(GUILDS.values()))}")
    
    # Scan
    print("\n[SCAN] Expert challenges...")
    challenges = scan_challenges(wallets)
    print(f"Found {len(challenges)} external challenges")
    
    zero_subs = [c for c in challenges if c.get("submissionCount", 0) == 0]
    one_subs = [c for c in challenges if c.get("submissionCount", 0) == 1]
    print(f"Zero-sub: {len(zero_subs)} | One-sub: {len(one_subs)}")
    
    if "--scan-only" in sys.argv:
        # Save and exit
        with open("/tmp/claimable_challenges.json", "w") as f:
            json.dump(challenges, f, indent=2)
        print(f"Saved to /tmp/claimable_challenges.json")
        return
    
    # Claim
    print("\n[CLAIM]")
    claimed = claim_challenges(wallets, challenges)
    
    # Summary
    print(f"\n=== RESULTS: {len(claimed)} new claims ===")
    guild_counts = {}
    for cl in claimed:
        g = cl["guild"]
        guild_counts[g] = guild_counts.get(g, 0) + 1
    for g, count in sorted(guild_counts.items(), key=lambda x: -x[1]):
        print(f"  Guild {g}: {count} claims")
    
    # Save
    with open("/tmp/guild_claims_fresh.json", "w") as f:
        json.dump(claimed, f, indent=2)
    print(f"Saved to /tmp/guild_claims_fresh.json")

if __name__ == "__main__":
    main()
