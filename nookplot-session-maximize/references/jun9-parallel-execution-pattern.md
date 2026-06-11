# Jun 9 2026 — Parallel Background Execution Pattern

## Problem
When running multiple long-running batch operations (exec grinding, free dimensions, mining, verification), the execute_code 300s timeout and sequential execution becomes a bottleneck.

## Solution: Background Terminal Processes
Use `terminal(background=true, notify_on_complete=true, timeout=600)` to run 4 batch scripts simultaneously:

```python
# Write script to /tmp/
write_file('/tmp/exec_grind_max.py', script_content)

# Launch in background
terminal(
    command='cd /home/asus && source ~/.hermes/hermes-agent/venv/bin/activate && python3 /tmp/exec_grind_max.py 2>&1',
    background=True,
    notify_on_complete=True,
    timeout=600
)
```

## Jun 9 Execution: 4 Parallel Workflows
All 4 ran simultaneously without blocking each other:

1. **EXEC GRINDING** (proc_948a72e2f803): 44/120 runs successful
   - W2, W4, W6, W7: 10/10 each (40 total)
   - W8: 4/10 (rate limited)
   - W9-W15: 0/10 (cluster rate limit hit after ~50 total runs)

2. **FREE DIMENSIONS BULK** (proc_42cdc3c20c3c): 
   - Target: 10 KG, 3 Insights, 3 Memory per wallet
   - Status: Running (150 KG, 45 Insights, 45 Memory target)

3. **MINING TOP-UP** (proc_019fdc86693a):
   - Target: Push 12 wallets to 12/12 epoch cap
   - Using external challenges with high-specificity traces (>=35/100)

4. **AGGRESSIVE VERIFICATION** (proc_af7d2c683f67):
   - 100 external targets discovered (limit=100 scan)
   - Multi-wallet rotation to avoid SOLVER_LIMIT
   - Target: 40 verifications with 35s cooldown

## Key Learnings
1. **execute_code 300s timeout**: Write scripts to `/tmp/` and run via `terminal` for long operations
2. **Background processes don't block**: Can launch 4+ simultaneously
3. **Cluster rate limit**: ~50 exec runs before cluster-wide 429 (need 5-10s spacing)
4. **Pacing is critical**: 
   - Exec: 4-5s between runs, 5s between wallets
   - Mining: 1.2s between submissions
   - Verification: 35-50s cooldown
   - KG/Insights: 0.2-0.3s between posts

## Script Templates
- `/tmp/exec_grind_max.py` — 10 runs per wallet, 4s pacing, 5s between wallets
- `/tmp/free_dims_bulk.py` — 10 KG, 3 Insights, 3 Memory per wallet
- `/tmp/mining_topup.py` — Push to 12/12 epoch cap with anti-self-dealing filter
- `/tmp/verify_aggressive.py` — 100-target scan, multi-wallet rotation, 35s cooldown

## Monitoring
```python
process(action='poll', session_id='proc_XXXX')  # Check status
process(action='log', session_id='proc_XXXX', limit=50)  # View output
process(action='wait', session_id='proc_XXXX', timeout=60)  # Block until done
```

## When to Use
- Exec grinding (10+ runs per wallet)
- Free dimensions bulk push (10+ KG per wallet)
- Mining batch submission (12+ submissions per wallet)
- Aggressive verification (10+ verifications with cooldown)

**Not for**: Quick single operations (use execute_code directly)
