#!/usr/bin/env python3
"""Retry V3 — slower pacing + larger sleep to avoid IPFS rate-limit."""
import sys, os, json, subprocess, hashlib, time, re
sys.path.insert(0, "/home/asus/.hermes/skills/nookplot/nookplot-leaderboard-maximization/scripts")
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, "/tmp")
from np_mass_solve_v2 import make_trace, ANGLES, TECHNIQUES, best_technique

WALLETS = json.load(open(os.path.expanduser("~/.hermes/nookplot_wallets.json")))
GW = "https://gateway.nookplot.com"
PLAN = json.load(open("/tmp/retry_plan_v3.json"))

# Pre-fetch
print(f"Pre-fetching {len(PLAN)} details...", flush=True)
DETAIL_CACHE = {}
auth_w1 = "Authorization: Bearer " + WALLETS["W1"]["apiKey"]
for entry in PLAN:
    cid = entry["id"]
    for _ in range(3):
        r = subprocess.run(["curl", "-sS", "-H", auth_w1, GW + f"/v1/mining/challenges/{cid}",
                            "--max-time", "20"], capture_output=True, text=True, timeout=25)
        try:
            d = json.loads(r.stdout)
            if d.get("title"):
                DETAIL_CACHE[cid] = d; break
        except: pass
        time.sleep(2)
    time.sleep(0.4)
print(f"Cached {len(DETAIL_CACHE)}", flush=True)

def submit_one(slot, entry):
    apikey = WALLETS[slot]["apiKey"]
    auth = "Authorization: Bearer " + apikey
    cid_full = entry["id"]
    detail = DETAIL_CACHE.get(cid_full)
    if not detail:
        return f"NO_DETAIL {slot}/{entry['short']}"
    
    trace, summary = make_trace(detail, slot)
    trace_hash = hashlib.sha256(trace.encode()).hexdigest()
    
    upload_payload = {"data": {"traceContent": trace, "traceSummary": summary, "modelUsed": "claude-opus-4.7"}}
    cid = None
    for attempt in range(5):  # more retries
        r = subprocess.run(["curl", "-sS", "-X", "POST", GW + "/v1/ipfs/upload",
                            "-H", auth, "-H", "Content-Type: application/json",
                            "-d", json.dumps(upload_payload),
                            "--max-time", "60"],
                            capture_output=True, text=True, timeout=70)
        try:
            cid = json.loads(r.stdout).get("cid")
            if cid: break
        except: pass
        time.sleep(5 + attempt * 2)
    if not cid:
        return f"IPFS_FAIL {slot}/{entry['short']}"
    
    submit_payload = {
        "traceCid": cid, "traceHash": trace_hash, "traceSummary": summary,
        "modelUsed": "claude-opus-4.7", "stepCount": 5,
    }
    r = subprocess.run(["curl", "-sS", "-X", "POST",
                        GW + f"/v1/mining/challenges/{cid_full}/submit",
                        "-H", auth, "-H", "Content-Type: application/json",
                        "-H", "User-Agent: Mozilla/5.0",
                        "-d", json.dumps(submit_payload),
                        "-w", "\n__HTTP__%{http_code}",
                        "--max-time", "60"],
                        capture_output=True, text=True, timeout=70)
    out = r.stdout.rsplit("__HTTP__", 1)
    body = out[0].rstrip("\n")
    code = out[1] if len(out) > 1 else "?"
    try:
        data = json.loads(body)
    except:
        return f"NOT_JSON {slot}/{entry['short']} http={code}"
    if "id" in data:
        return f"OK {slot}/{entry['short']} sub={data['id'][:8]}"
    return f"ERR {slot}/{entry['short']} http={code} {data.get('error','?')[:140]}"

def run_wallet(slot, entries):
    print(f"[{slot}] BEGIN n={len(entries)}", flush=True)
    results = []
    for ch in entries:
        for retry_attempt in range(2):
            r = submit_one(slot, ch)
            if r.startswith("OK") or "Already submitted" in r or "EPOCH" in r:
                break
            if "429" in r or "IPFS_FAIL" in r:
                time.sleep(30)
                continue
            break
        print(r, flush=True)
        results.append(r)
        time.sleep(15)  # bigger gap
    print(f"[{slot}] DONE", flush=True)
    return results

if __name__ == "__main__":
    by_wallet = {}
    for entry in PLAN:
        by_wallet.setdefault(entry["slot"], []).append(entry)
    print(f"V3 Retry: {len(PLAN)} subs across {len(by_wallet)} wallets", flush=True)
    all_results = []
    # SERIAL across wallets to avoid IPFS hammering
    for slot, chs in sorted(by_wallet.items()):
        rs = run_wallet(slot, chs)
        all_results.extend(rs)
        time.sleep(10)
    print("\n=== SUMMARY ===")
    ok = sum(1 for r in all_results if r.startswith("OK"))
    print(f"Submitted: {ok} / {len(all_results)}")
    by_err = {}
    for r in all_results:
        if not r.startswith("OK"):
            by_err[r.split(" ")[0]] = by_err.get(r.split(" ")[0],0)+1
    if by_err: print(f"Errors: {by_err}")
    with open("/tmp/np_mass_solve_v3_log.json", "w") as fp:
        json.dump(all_results, fp, indent=2)
