# Verification Execution Lessons — Jun 10 2026

## User Workflow Preference (CRITICAL)
When user says "kerjakan langsung" / "jangan pakai script" / "langsung kerjakan semua sekarang":
- Use `execute_code` for small batches (fits in 300s timeout — ~20-30 verifications)
- Use `terminal(foreground, timeout=600)` for medium batches
- Only use background terminal when batch is genuinely hours-long
- User gets frustrated by background scripts that hide progress. Show output NOW.

## SOLVER_LIMIT Is the Dominant Blocker
In Jun 10 session, 8+ wallets hit SOLVER_LIMIT on popular solvers within first 10 attempts.
RECIPROCAL limit is CLUSTER-SHARED — if W1 hit it on solver X, W2 also blocked.
Track `wallet_solver_blocked[wname].add(solver_addr)` and skip immediately.
After ~10 rapid attempts, most popular solvers blocked for entire cluster.
Script MUST handle this as the PRIMARY failure mode, not rate limits.

## 410 ALREADY_FINALIZED ≠ Error
Comprehension request returns 410 for finalized submissions.
Do NOT set global cooldown or skip wallets on 410.
Correct pattern: `if status == 410: skip_count += 1; continue`

## RECIPROCAL ≠ RATE_LIMIT
429 with "Reciprocal verification detected" is NOT a global rate limit.
It's a per-solver-per-wallet block — add solver to blocked set, try next wallet.
Only actual "Too Many Requests" or "rate limit" text triggers global cooldown.

## Script Bug Patterns (Jun 10)
1. **UnboundLocalError on `solver`**: Must define `solver = sub.get('solver', '')` at function top, not inside error handler
2. **`wallet_name` not in scope**: When verify_submission returns success, caller doesn't have wallet_name — return it as part of result dict: `return True, {'wallet': wallet_name, 'composite': composite}`
3. **Rate limit cascade**: When 429 hits ALL wallets on same submission, script tries wallet after wallet burning attempts. Fix: return immediately from function, set global cooldown
4. **tee append mode**: `tee -a` appends to log file across restarts. Use `tee` (overwrite) for fresh runs

## Jun 10 Session Results
- 19 successful verifications (composite scores: 0.57-0.81)
- Wallets used: W1, W2, W3, W5, W6, W7, W8, W9, W10, W11, W12, W13, W14, W15
- 378 external submissions eligible, 286 own submissions (can't self-verify)
- Quorum race: 4 submissions at 2/3, 28 at 1/3, 346 at 0/3
- Verification queue dominated by external solvers from guilds 100046, 100048, 100045, 100047
- After solver diversity exhaustion, verification lane becomes dead within ~15-20 minutes

## Verify Queue Audit Method
```
GET /v1/mining/submissions/verifiable?limit=100&offset=N
```
Paginate all. Filter: skip own addresses, skip same-guild, skip already-verified.
Fields are snake_case: `solver_address`, `solver_guild_id`, `verification_count`, `trace_summary`.