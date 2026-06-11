# Reward lane live blockers and probe order (May 23 2026)

Use this when the user says variants of "gas cari cara biar maksimal" after verify grinding is already saturated.

## What changed / durable lesson

The right move is NOT to keep hammering the current top lane. Run a live probe sweep in descending ROI order and report which lanes are truly open versus blocked by caps, eligibility, or empty inventory.

This is especially important for this user, who wants action-first execution and a concise report of open-vs-blocked lanes — not generic encouragement to "wait".

## Probe order after verification is saturated

1. `discover_verifiable_submissions` / REST comprehension+verify route
   - Goal: confirm whether verify is still convertible or only requestable.
   - Distinguish:
     - request/comprehension open
     - final verify blocked by `SOLVER_VERIFICATION_LIMIT`
     - wallet blocked by `429` / rate limit

2. Open mining challenges (`discover_mining_challenges`)
   - If only one challenge remains, test a REAL submission attempt.
   - Do not stop at challenge listing.
   - Common blockers that must be surfaced explicitly:
     - `Your guild is none but this challenge requires tier1+`
     - `Maximum 1 guild-exclusive challenge per 24-hour epoch`
     - traceSummary specificity gate (fixable; retry once with concrete comparison/technique/numbers)

3. Swarm / subtask lane
   - Probe both `list_swarms` and `available_subtasks`.
   - Interpretation:
     - swarms visible + subtasks empty = surface exists but no immediate rewardable work
     - no need to invent hidden swarm opportunity if inventory is empty

4. Passive posting / own-challenge lane
   - Probe `discover_mining_challenges(myOwn: true)` and `my_mining_submissions(address=...)`.
   - If own challenges have 0 submissions or submissions remain pending, classify as passive/delayed rather than immediately executable.

5. Claim / delayed payout lane
   - Probe `check_mining_rewards`.
   - If `claimableBalance.* == 0` and `pendingRewards == 0`, report as closed for now.
   - Never imply claimable exists without a live balance.

6. KG / content / captures / citation lane
   - If high-ROI NOOK lanes are closed, this becomes the remaining live lane.
   - Frame honestly: contribution/reputation/citation density yes; big immediate NOOK no.

7. Spot check verification lane (Jun 7 2026)
   - Probe `nookplot_list_pending_spot_checks`.
   - If empty, classify as "open but no inventory yet".
   - If populated, replay sub-call and submit verdict via `nookplot_submit_spot_check_verdict`.

8. Trading edge research lane (Jun 7 2026)
   - Probe `nookplot_test_trading_setup` for exploration.
   - If edge looks promising, register via `nookplot_register_edge_hypothesis`.
   - High ROI if verified REAL by the gauntlet.

## Report shape for this class of task

Keep it compact and operational:

- lane
- live status: open / partially open / blocked
- proof: exact blocker string or inventory result
- next action / unlock condition

Example phrasing:
- "Verification: partially open at request layer on W1/W2/W3, but final verify blocked by `SOLVER_VERIFICATION_LIMIT`; W4+ mostly 429."
- "Mining: one open guild-exclusive challenge exists, but W1 fails tier1 requirement and W2/W3 are epoch-capped, so lane is effectively closed now."
- "Swarms: `list_swarms` returns inventory, `available_subtasks` returns empty array, so no claimable subtask now."

## Durable execution rule

When a lane looks promising on paper, perform one real execution attempt before classifying it as open. For mining this means an actual submit attempt; for verify this means full comprehension + verify; for swarm this means checking claimable subtasks, not only swarm visibility.

## Cross-transport sanity check

If a scripted REST sweep reports a surprising zero inventory — e.g. `bounties=0`, `swarms=0`, empty mining/verify text — do NOT immediately report the lane closed. Re-probe the same lane through the native MCP tools or direct endpoint before finalizing. In May 2026, a custom `/v1/actions/execute` script returned empty verify/mining/bounty/swarm summaries while the native MCP tools and direct `/v1/bounties` endpoint still showed 30 verify submissions, 1 mining challenge, and 20 open bounties. Treat disagreement as a transport/parse problem until one independent read confirms it.

Reporting rule: when sources disagree, say which source was trusted and why. Prefer native MCP tool output for mining/verification queue summaries, and direct REST `GET /v1/bounties?status=0` for bounty inventory.

## Additional references

- `references/cross-transport-zero-inventory-pitfall.md` — independent re-probe rule when one transport reports zero inventory but MCP/direct REST disagree.

## Session-specific evidence pointers

- Verify lane saturation in this session combined two blockers:
  - request-layer `429 Too many requests` on many wallets
  - `SOLVER_VERIFICATION_LIMIT` on wallets that still passed comprehension
- Mining lane had one open challenge `bb5186da-b752-494f-9e46-d28e3dd2a3f5`, but real submit attempts returned:
  - W1: guild none, challenge requires tier1+
  - W2/W3: max 1 guild-exclusive challenge per 24h epoch
- Swarm surface existed, but `available_subtasks` returned empty.
- Claimable on active MCP wallet read as zero across guild_inference_claim / epoch_verification / epoch_solving.

Add a pointer in SKILL.md if repeated again; otherwise this reference is enough.
