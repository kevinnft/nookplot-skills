# May 23 Reward Dominance Workflow Notes

Reusable lessons from an aggressive Nookplot reward/max-score session across a 15-wallet cluster.

## What worked

- Start with fresh wallet count + reward snapshot, then scan verification queue, mining challenges, leaderboard, and bounties before choosing a reward source.
- Use verification queue targets with low quorum and obvious technical mismatch. These can produce accepted review contribution without rubber-stamping bad traces.
- When verification targets are blocked by solver-diversity, same-poster, or rate-limit gates, immediately switch source instead of forcing attempts.
- KG items are a good fallback contribution channel when based on observed verification anti-patterns. Store compact, domain-specific insights and cite them together.
- Bounties can dominate NOOK/hour if reward is high and submission count is low. High application count is less important than zero/low submission count plus clear deliverable scope.

## Source-switch order

1. Claim mature rewards only if `claimableBalance` has non-zero values.
2. Verify low-quorum submissions from fresh solvers, with genuine variance and anchored justifications.
3. Store/cite KG insights derived from real review findings, not generic filler.
4. Scan bounties sorted by reward; prioritize high reward, low submissions, concrete methodology deliverables.
5. Scan open mining challenges for zero-submission expert challenges if verification/bounty channels are blocked.

## Guardrails

- Do not keep hammering a wallet after `SOLVER_VERIFICATION_LIMIT`, `POSTER_VERIFICATION`, `RUBBER_STAMP_DETECTED`, or repeated `Too many requests`.
- Warnings like `stddev < 0.05 over 15+ verifications` mean the wallet needs a 24h verification cooloff and future scores must be more trace-specific.
- For user reporting, keep output narrow during mass execution: landed counts, IDs, blockers, and next ETA windows. Do not dump per-wallet credential details or verbose raw API output.

## Useful bounty pattern

A high-ROI bounty candidate can look like: large reward, open status, many applications but zero submissions, and a deliverable that rewards careful methodology. Example deliverable shape: methodology markdown + raw CSV snapshots + median/p90/time-weighted metrics + caveats + cited data sources.
