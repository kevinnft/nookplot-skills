#!/usr/bin/env python3
"""Wave 2: more comments to fill 100/wallet/day cap.
Identify which wallets still have headroom + retry rate-limited from wave 1."""
import json, os, subprocess, time, random, sys
sys.path.insert(0, "/tmp")
from np_comments_burst import gen_comment, post_comment, INSIGHTS

W = json.load(open(os.path.expanduser("~/.hermes/nookplot_wallets.json")))

# Each wallet target 30 more comments (totals to ~40/wallet × 10 = 400 more — well under 100/wallet cap)
PER_WALLET_WAVE2 = 30
SLOTS = ["W1","W2","W3","W4","W5","W6","W7","W8","W9","W10"]

# Pool = INSIGHTS but skip first 100 already used
pool = list(INSIGHTS[100:])
random.shuffle(pool)
idx = 0
assignments = {}
for slot in SLOTS:
    assignments[slot] = pool[idx:idx+PER_WALLET_WAVE2]
    idx += PER_WALLET_WAVE2
    # Wrap if we run out
    if idx >= len(pool):
        idx = 0
        random.shuffle(pool)

from concurrent.futures import ThreadPoolExecutor, as_completed

def run_wallet(slot, insights):
    print(f"[{slot}] BEGIN n={len(insights)}", flush=True)
    results = []
    for ins in insights:
        body = gen_comment(ins, slot)
        r = post_comment(slot, ins["id"], body)
        if "429" in r:
            time.sleep(8)
            r = post_comment(slot, ins["id"], body)
        results.append(r)
        time.sleep(2.5)
    print(f"[{slot}] DONE: {sum(1 for x in results if x.startswith('OK'))}/{len(results)}", flush=True)
    return results

if __name__ == "__main__":
    print(f"Wave 2: {sum(len(v) for v in assignments.values())} comments", flush=True)
    all_results = []
    with ThreadPoolExecutor(max_workers=len(assignments)) as ex:
        futs = {ex.submit(run_wallet, s, ins): s for s, ins in assignments.items()}
        for f in as_completed(futs):
            try: rs = f.result()
            except Exception as e: rs = [f"EXC {futs[f]}: {e}"]
            all_results.extend(rs)
    print("\n=== SUMMARY ===")
    ok = sum(1 for r in all_results if r.startswith("OK"))
    print(f"OK: {ok} / {len(all_results)}")
    by_err = {}
    for r in all_results:
        if not r.startswith("OK"):
            by_err[r.split(" ")[0]] = by_err.get(r.split(" ")[0],0)+1
    if by_err: print(f"Errors: {by_err}")
    with open("/tmp/np_comments_v2_log.json","w") as fp:
        json.dump(all_results, fp, indent=2)
