# Hidden reward lane audit — May 23 2026

Use this when the user asks `reward tersembunyi`, `celah reward`, or `gas maksimalkan` after standard mining/verification lanes are hot.

## Verified read-only probes

- `nookplot_get_mining_proof` returns the current Merkle proof/cumulative amount per wallet. Compare it to `check_mining_rewards.totalEarned` to estimate historical/non-current-proof delta, but do NOT treat the delta as immediately claimable.
- `check_mining_rewards.claimableBalance` is authoritative for immediate no-argument claims. On May 23, W1-W15 all had `epoch_solving=0`, `epoch_verification=0`, `guild_inference_claim=0` despite positive proof/history gaps.
- `nookplot_claim_pending_guild_mining_treasury` is a safe readiness probe if stopped at `status: sign_required`. It returned `sign_required` for W1-W15 with `preparePath=/v1/prepare/mining/guild/treasury/claim-pending` and method data `0x166b69a3`. This means an on-chain claim transaction can be prepared; amount is not exposed by the gateway until signing/relay or chain inspection.
- Do not relay/sign automatically unless the user explicitly authorizes claim execution. The user's default preference is manual/in-session action, no cron.

## Dead or blocked lanes observed

- Ecosystem/Botcoin tools were present (`nookplot_ecosystem_stats`, `leaderboard`, `stake`, `claim_rewards`) but actions-execute ignored `protocol`/`protocolId` args and returned `Unknown protocol "undefined"`. Direct REST variants under `/v1/ecosystem...` returned 404. Treat this lane as tool-wrapper broken until a new route is found.
- `nookplot_available_subtasks` returned empty; swarm/coordination had no open subtask work.
- Marketplace service listing exists, but REST service routes are mostly 404; marketplace agreements for the audited wallet were empty.
- `nookplot_guild_active_claims` returned `Invalid guildId` for known guild IDs; do not rely on it for guild opportunity discovery.

## Safe actionable openings

1. **Manual guild treasury claim path**: W1-W15 all reached `sign_required`; this is the most concrete hidden-claim opening, but needs signing/relay. Prepare-only is non-destructive; relay is side-effectful.
2. **Bounty portfolio**: many high-value open bounties still show `status=0`, `submissionCount=0`, and no approved claimer. Existing applications may sit pending; do not spam duplicate apps. Best action is deliverable production once approved or a high-quality public deliverable that can be submitted if the bounty flow permits.
3. **Weekly reward pool**: `nookplot_weekly_reward_info` showed epoch `202621`, period `2026-05-18T10:31Z` to `2026-05-25T10:31Z`, poolCredits `15000`, time remaining about `1d 20h` at the May 23 probe. Use this for ETA reports.

## Interpretation pitfalls

- `totalEarned - miningProof.cumulativeAmount` can be large, but it is not a direct claim amount. It may include historical already-claimed amounts, channels outside the Merkle proof, or accounting that has not settled into `claimableBalance`.
- A `sign_required` result is evidence of a viable transaction route, not proof of positive payout size.
- High bounty application counts with `submissionCount=0` indicate open competition, not guaranteed payout.
