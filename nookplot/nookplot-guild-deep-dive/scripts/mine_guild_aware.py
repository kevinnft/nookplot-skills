#!/usr/bin/env python3
"""Guild-aware mining: assigns challenges per guild to avoid cross-guild blocking.
Usage: python3 mine_guild_aware.py"""
import json, time, subprocess, hashlib

with open("/home/asus/.hermes/nookplot_wallets.json") as f:
    wallets = json.load(f)

GW = "https://gateway.nookplot.com"

GUILD_MAP = {
    "W1": 100017, "W2": 9, "W3": 100002, "W4": 100017,
    "W5": 100032, "W6": 100045, "W7": 100045, "W8": 100045,
    "W9": 100045, "W10": 100000, "W11": 10, "W12": 10,
    "W13": 100002, "W14": 100046, "W15": 100002
}

GUILD_WALLETS = {}
for w, gid in GUILD_MAP.items():
    GUILD_WALLETS.setdefault(gid, []).append(w)

def get(wname, path):
    r = subprocess.run(["curl", "-s", "-H", "@/tmp/hdr_" + wname + ".txt", GW + path], capture_output=True, text=True, timeout=30)
    try: return json.loads(r.stdout)
    except: return {"_raw": r.stdout[:500]}

def post(wname, path, body):
    with open("/tmp/api_body.json", "w") as f: json.dump(body, f)
    r = subprocess.run(["curl", "-s", "-X", "POST", "-H", "@/tmp/hdr_" + wname + ".txt", "-H", "Content-Type: application/json", "-d", "@/tmp/api_body.json", GW + path], capture_output=True, text=True, timeout=30)
    try: return json.loads(r.stdout)
    except: return {"_raw": r.stdout[:500]}

def upload_trace(wname, reasoning_text):
    trace_obj = {"format": "reasoning_v1", "reasoning": reasoning_text}
    trace_json = json.dumps(trace_obj, separators=(",", ":"))
    r = post(wname, "/v1/ipfs/upload", {"data": {"content": trace_json, "name": "trace.json"}})
    return r.get("cid", ""), trace_json

def submit(wname, challenge_id, cid, trace_json, summary):
    trace_hash = hashlib.sha256(trace_json.encode()).hexdigest()
    return post(wname, "/v1/mining/challenges/" + challenge_id + "/submit", {"traceCid": cid, "traceHash": trace_hash, "traceSummary": summary})

# Scan, filter external, assign per guild, mine
# See /tmp/nookplot_mine_r2.py for full implementation
print("Guild-aware mining script — see /tmp/nookplot_mine_r2.py for full version")
