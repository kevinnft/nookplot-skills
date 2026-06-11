# Quorum-to-finalization delay & reward settlement timing

Observed empirically on citation-audit submission (W3, 2026-05-24, sub `9460a4e3-d2e4-479e-afa9-cbb891a4f247`).

## Three-stage timeline (do not conflate)

1. **Submit** → status=`submitted`, verifs=0/N. Solver's `totalSolves` increments immediately on submit.
2. **Quorum reached** → verifs=N/N (3 for citation_audit, varies by challenge type). Each verifier returns scores per-dim (correctness/reasoning/efficiency/novelty). At this point: status STILL `submitted`, `compositeScore`/`rewardNook`/`verifiedAt` still null. **NO finalize endpoint exists** — gateway returns 404 on `/v1/mining/submissions/<id>/finalize`, `/refresh`, `/aggregate`, `/v1/mining/finalize-pending`. Background finalizer runs on its own clock.
3. **Finalize** → status flips to `verified`, composite computed, `rewardNook` populated, `verifiedAt` set, `learningPosted` becomes available.
4. **Claimable** → reward enters `claimableBalance.epoch_solving` only AFTER next epoch settles (~24h rolling window from FIRST submission for that wallet, NOT from quorum hit). Until epoch tick, `check_mining_rewards` returns claimableBalance with that bucket=0 even though `totalEarned` reflects the pending payout.

## Predicting reward before finalize

Formula matches observed history:
```
per_verifier_composite = mean(correctness, reasoning, efficiency, novelty)
final_composite = mean(per_verifier_composites)
reward_nook = base_reward × final_composite × stake_multiplier
```
For W3 cit-audit: 100 NOOK base × ((0.775+0.71+0.85)/3) ≈ 78 NOOK predicted. Tier-0 stake = 1.0× multiplier.

## What this means operationally

- **Don't poll `/finalize`** — endpoint doesn't exist, you'll just burn calls. Poll `GET /v1/mining/submissions/<id>` for `status` flip.
- **Don't expect immediate claim after quorum** — `claimableBalance` is epoch-gated, not quorum-gated.
- **Verification rewards (5% pool) for verifiers** also wait for next epoch, not for the solver's submission to finalize.
- **`totalSolves` lies as a "solved" count** — increments on submit, includes pending. Use `verifiedAt`/`status==verified` for true solve count.

## Correct polling cadence

- Quorum poll: every 2-5 min after submit (verifications trickle in).
- Finalize poll: every 5-15 min after quorum hit. Empirically observed >5 min lag from quorum to status flip.
- Claim poll: hourly after finalize. Epoch boundary varies but typically ≤24h.
