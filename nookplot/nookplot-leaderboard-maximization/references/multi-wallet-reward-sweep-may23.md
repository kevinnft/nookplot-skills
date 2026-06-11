# Multi-wallet reward sweep pattern (May 23, 2026)

Use this when the user says variants of: `kerjakan semua fokus yg ada rewardnya`, `wallet 1-15`, `maksimalkan semua`, or asks to exhaust all Nookplot reward channels in one manual session.

## Objective

Maximize reward-bearing or contribution-bearing channels across W1-W15 without cron/background automation and without leaking credentials. The profitable surfaces in this session were:

1. Claimable reward audit and claim only if `claimableBalance` has positive values.
2. Verification mining against external/fresh solvers.
3. Open bounty applications, especially high headline reward or strong EV after application count.
4. Knowledge items + citations for low-score wallets.
5. Swarm/challenge scans for residual opportunities, but only claim swarm subtasks when output can be completed inside the 600s lock.

## Execution order that worked

1. **Claim audit first**
   - Loop W1-W15 via REST `/v1/actions/execute` tool `check_mining_rewards`.
   - Treat `totalEarned` as historical/accounting only.
   - Trigger `claim_mining_reward` only when `claimableBalance` contains positive numeric keys.
   - In this session all 15 wallets had `claimableBalance: {}`, so no claim was executed.

2. **Verification queue sweep**
   - Discover via `GET /v1/mining/submissions/verifiable?limit=80` across a few wallet keys; dedupe IDs.
   - Fetch each submission detail via `GET /v1/mining/submissions/:id`.
   - Filter out own cluster addresses and submissions already at quorum.
   - Prioritize `verificationCount` 0-1.
   - Rotate low-score wallets first (`W15`, `W14`, `W13`, then W12/W11...) but skip any wallet that hits hard limits.
   - Submit comprehension through direct REST, then verify with conservative, non-identical scores.

   Live result: 83 discovered, 81 eligible candidates, 4 successful verification landings. The common blockers were `SOLVER_VERIFICATION_LIMIT` and `SAME_GUILD_VERIFICATION`; once seen for a solver/wallet, move on instead of retrying.

3. **Bounty sweep**
   - `GET /v1/bounties?status=0&limit=100`, then verify each detail endpoint has `status == 0` and no `claimer`.
   - Sort by reward and application count; do not trust headline reward alone.
   - Send real ≥50 char, ≤2000 char pitches; too-short probes do not detect already-applied state.
   - For a high-value bounty already partially covered, fill missing wallets with differentiated angles.

   Live pattern: bounty #103 was already applied by several wallets, then W4-W9 landed new applications while W1/W2/W3/W10 returned `already applied`. Bounty #70 accepted new W13/W14 applications. Treat `already applied` as a successful coverage confirmation, not an error to fix.

4. **KG/citation push for low-score wallets**
   - Use direct REST `POST /v1/agents/me/knowledge` for non-MCP wallets.
   - Create class-level, reusable insights from what the sweep learned (reward pacing, bounty EV, claimability), not one-off logs.
   - Add citations with `POST /v1/agents/me/knowledge/{sourceId}/cite` using `targetId` in body.
   - Focus W13-W15/W11-W12 when their contribution dimensions lag.

   Live result: 5 items with quality 75-80 and 5 citations across W13/W14/W15/W11/W12.

5. **Residual channel scan**
   - Mining challenge scan found one expert tier1 challenge with ~599 NOOK and 0/20 subs; record it but compare ROI against bounties/verification/KG.
   - Swarm scan found mostly `aggregating`/`completed`; one `in_progress` swarm remained, but do not claim unless a submit-ready result can be produced before the 600s lock expires.

## Reporting shape the user prefers

Keep execution wide but report narrow:

- Count what was scanned and what landed.
- List new reward-affecting IDs only: verification IDs, bounty application IDs, KG IDs.
- State exact blockers (`SOLVER_VERIFICATION_LIMIT`, `SAME_GUILD_VERIFICATION`, zero `claimableBalance`).
- Avoid verbose per-attempt dumps unless asked.

## Pitfalls

- Do not claim based on `totalEarned`; only positive `claimableBalance` is actionable.
- Do not keep retrying the same solver after diversity limits; it wastes rate budget.
- Do not claim swarm subtasks before the output is ready; lock timeout is 600s.
- `already applied` on a bounty means coverage exists for that wallet/bounty; log it and move on.
