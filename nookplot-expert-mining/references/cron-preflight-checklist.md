# Cron Job Pre-Flight Checklist for Expert Mining

Created: 2026-06-01 (epoch 74, all wallets at cap)

## Problem Pattern

Cron jobs for expert mining batch submissions often fail silently or waste rate limit budget because they skip pre-flight validation. Common failure modes:

1. **Missing trace file** — Cron references `/tmp/nook_hemi_traces.json` or similar, but the file was never created or was cleaned up.
2. **Epoch closed** — Mining during closed epoch earns 0 NOOK. Traces are stored but wasted effort.
3. **All wallets at cap** — 12/12 submissions used in rolling 24h window. No free slots.
4. **Target challenges missing** — The specific challenge category (hemi framework, formal methods, etc.) isn't in the open pool or is fully submitted (20/20).

## Pre-Flight Sequence

Execute these checks BEFORE building the submission pipeline:

```python
import os, json, subprocess

# 1. Check trace file exists
TRACE_FILE = "/tmp/nook_hemi_traces.json"  # or wherever
if not os.path.exists(TRACE_FILE):
    # Check alternate locations
    for alt in ["~/nookplot-expert-traces.json", "~/nookplot-mining-*/traces/master/"]:
        if os.path.exists(os.path.expanduser(alt)):
            TRACE_FILE = alt
            break
    else:
        print("[ABORT] No trace file found")
        exit(1)

# 2. Check epoch is open
epoch = curl_get(f"{API}/mining/epoch")
if epoch.get("epoch", {}).get("status") != "open":
    print("[SILENT] Epoch closed — mining earns 0 NOOK")
    exit(0)

# 3. Check challenge pool for expected types
challenges = curl_get(f"{API}/mining/challenges?status=open&limit=200", api_key=key)
expected_keywords = ["model check", "smt", "theorem", "hemi", "formal"]  # adjust per job
matches = [c for c in challenges if any(kw in c.get("title","").lower() for kw in expected_keywords)]
if not matches:
    print(f"[ABORT] No matching challenges found. Pool has {len(challenges)} challenges but none match keywords.")
    exit(1)

# 4. Check wallet free slots (use nookplot status, not limit=20 heuristic)
# The limit=20 API returns up to 20 most recent — can't distinguish 12 from 20+
free_wallets = []
for w in WALLETS:
    # Option A: CLI (accurate)
    result = subprocess.run(["nookplot", "status"], capture_output=True, text=True, 
                          cwd=f"/home/ryzen/nookplot-{w}", env={...})
    # Parse output for epoch usage
    
    # Option B: REST with timestamp filtering
    submissions = curl_get(f"{API}/mining/submissions/agent/{addr}?limit=20", api_key=key)
    # Filter by epoch start time if available
    count = len([s for s in submissions if within_epoch(s)])
    free = max(0, 12 - count)
    if free > 0:
        free_wallets.append((w, free))

if not free_wallets:
    print("[SILENT] All wallets at epoch cap")
    exit(0)
```

## Submission Count Detection: Why `limit=20` Fails

`GET /v1/mining/submissions/agent/{addr}?limit=20` returns the **20 most recent** submissions, not "submissions within current epoch". 

- If wallet has 8 submissions: returns 8, free=4 ✓
- If wallet has 12 submissions: returns 12, free=0 ✓  
- If wallet has 20+ submissions: returns 20, free=**unknown** ✗

When all wallets show "20/12 used" it means they all have ≥20 total submissions (possibly spanning multiple epochs), and they're definitely at the current epoch cap. But you can't use this to identify wallets with 1-5 free slots.

### Better approaches:
1. **`nookplot status` CLI** — Shows "Mining: X/12 this epoch" directly
2. **Timestamp filtering** — If API returns submission timestamps, filter by epoch start time
3. **Track locally** — Maintain a local ledger of submissions per wallet per epoch

## When to Return [SILENT]

Cron jobs should return `[SILENT]` (suppress delivery) when:
- Epoch is closed
- All wallets are at cap (0 free slots)
- No matching challenges exist in pool
- Trace file missing and no alternate found

This avoids spamming the user with "nothing to report" messages.

## Observed: June 1, 2026 (Epoch 74)

- Epoch: **closed** (status: "closed", consecutiveReserveDays: 0)
- Challenge pool: 100 total, only 1 marginal "Temporal GNN" match for formal methods keywords
- Wallet status: All 15 wallets at "20/12" (≥20 total submissions, definitely at cap)
- Trace file: `/tmp/nook_hemi_traces.json` does NOT exist
- Correct response: `[SILENT]` — no action possible

## Challenge Pool Volatility

The 500K expert standard challenges are NOT permanent fixtures:

| Topic | Status (June 2026) |
|-------|-------------------|
| PQ Crypto (Kyber/Dilithium) | Fully submitted (20/20) |
| DB Sharding (Vitess/CockroachDB) | Fully submitted |
| LLM Inference (vLLM/PagedAttention) | Fully submitted |
| ZK Circuits (Groth16/Plonk) | Fully submitted |
| Byzantine Consensus (HotStuff/Tendermint) | Fully submitted |

Formal methods challenges (Model Checking, SMT Solving, etc.) were either never in the pool or rotated out. The pool composition changes as challenges fill and new ones are posted.

**Always scan live. Never hardcode challenge IDs in cron jobs.**
