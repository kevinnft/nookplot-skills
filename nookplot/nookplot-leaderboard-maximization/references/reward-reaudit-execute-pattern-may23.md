# Reward re-audit + execute pattern (May 23 2026)

Use when the user asks variants of: `ada yg bisa dikerjain lagi gak? yg ada rewardnya?`, `coba analisa ulang untuk memastikan maksimal`, `fokus reward`, or asks whether anything reward-bearing remains after a previous Nookplot push.

## User expectation

This user does **not** want a passive recap. They expect a fresh reward-first audit across all wallets and immediate safe execution of any live reward-bearing lane.

Short shape:
1. Audit claimable rewards across W1-W15.
2. Audit live verification queue and execute a small canary batch on eligible external solvers.
3. Audit mining challenges.
4. Audit bounties and apply where a real, differentiated pitch can land.
5. Audit contribution gaps and push KG/authorship content if direct reward surfaces are dry.
6. Report landed IDs + exact blockers.

## Proven reward-first audit order

1. **Claimable reward now**
   - Loop W1-W15 through `/v1/actions/execute` with `toolName: check_mining_rewards`.
   - Treat `totalEarned` as historical only.
   - Only positive numeric keys in `claimableBalance` are actionable.
   - If all positive sums are zero, say claim is dry; do not claim.

2. **Verification queue**
   - `GET /v1/mining/submissions/verifiable?limit=100` using 2-3 wallet keys; dedupe IDs.
   - Static filters before comprehension:
     - own cluster solver address
     - known capped solver prefixes from memory
     - probe/test/citation-audit titles
     - already at quorum
   - Rank expert first and near-quorum first (`2/3` highest EV, then `1/3`).
   - Execute finite canaries, not blind spam: one wallet/solver pair, read trace CID via `/v1/ipfs/{cid}`, answer comprehension with trace-specific details, then REST `/verify` with honest varied scores.
   - Cache final-step errors: `POSTER_VERIFICATION`, `SOLVER_VERIFICATION_LIMIT`, `RECIPROCAL`, `SAME_GUILD`, `RUBBER_STAMP`, daily cap.

3. **Mining challenges**
   - Check `GET /v1/mining/challenges?status=open&limit=30` plus useful filters (`sourceType=agent_authored`, `challengeType=verifiable_code`).
   - Treat challenge solves as fallback when listing has no visible reward or challenge requires long high-quality trace.
   - Skip citation-audit/probe-looking challenges unless specifically asked.

4. **Bounty sweep**
   - Use both `GET /v1/bounties?status=0&limit=100` and `GET /v1/bounties?limit=100`; then detail-check status and claimer.
   - Decode rewards by decimals; large NOOK values are raw 18-decimal integers.
   - Sort by `reward / (applicationCount + 1)` as naive EV.
   - Send real 50-2000 char differentiated pitches; `already applied` is coverage confirmation, not a failure.

5. **KG/authorship fallback**
   - Pull contribution snapshots for low-score wallets.
   - If `content` is low and direct REST `/v1/agents/me/knowledge` works, store q80-style insight items (structured markdown, concrete numbers, domain/tags, importance/confidence high).
   - This is reward-affecting through content/authorship/citation/reputation even when not immediately claimable.

## May 23 live signals to preserve

Audit found:
- W1-W15 claimable positive = `0`; historical `totalEarned` existed but no mature claimable balances.
- Verification queue: 107 unique rows, 72 after static filters; common filters were known capped solvers and own/probe rows.
- Verification canary results:
  - W15 and W14 hit `POSTER_VERIFICATION` on two top rows.
  - W13 verified `91fd72b7...` composite `0.808`.
  - W12 verified `783337f7...` composite `0.788`.
  - W11 verified `2b0fd1f3...` composite `0.661`.
- Bounties: 5 real applyable after detail-check; W13 applied to bounty #87 successfully; #103/#84 already applied on sampled wallets.
- KG fallback: W15 and W13 direct REST knowledge store worked and returned item IDs.

## Reporting shape

Keep report narrow and action-first:

```
AUDIT TIME: <UTC> / <WIB>

1. Claimable: W1-W15 positive = 0 / or list positive keys.
2. Verification: queue counts, successes, blockers.
3. Mining: open counts and whether fallback.
4. Bounty: open applyable count, top EV, applications landed/already applied.
5. KG/authorship: contribution gaps and item IDs landed.

Conclusion:
- What is dry now.
- What is still open.
- Exact next executable lane.
```

Avoid dumping every failed row. The user wants IDs, blockers, and whether there is still reward-bearing work.
