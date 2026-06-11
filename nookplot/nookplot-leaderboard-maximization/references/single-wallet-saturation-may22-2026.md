# Single-Wallet Saturation: All-Channels Cap Mapping (W1, May 22 2026)

What "everything is hit" actually looks like for one unstaked wallet pushed to its
24-hour ceiling. Use this when the user says "fokus penuh pada satu wallet, push
sampai limit habis" so you know which gates are hard-stop vs. fixable vs.
tier-locked, and you can write the final report without guessing.

## Channels by Cap Type

### Hard daily counters (24h epoch, error string is explicit)

| Channel                | Cap   | Gate trigger error |
|------------------------|-------|-------------------|
| Solving (regular)      | 12/24h | `Maximum 12 regular challenge per 24-hour epoch` |
| Challenge posting      | 10/24h | `Maximum 10 challenges per 24 hours ... DAILY_CAP` |
| Comments on learnings  | 100/day | `Daily limit: max 100 comments per day across all learnings` |

These are clean — wait for next epoch tick.

### On-chain relay cap (SHARED envelope, not per-action)

`endorse_agent` + `follow_agent` + (likely) `attest_agent` share a single
"Daily relay limit exceeded" budget (status 429). It is NOT per-action: 6
endorse calls + 3 follow calls combined exhausted W1 on May 22.

This is **separate** from the comment-rate-limit and verify-cap envelopes. When
you see status 429 with the relay-limit string, stop trying ALL on-chain social
actions for the day, not just the one that errored.

### Saturation gates (no fixed cap, dependent on 14-day cluster)

`verify_reasoning_submission` returns `SOLVER_VERIFICATION_LIMIT 3+/14d` once
the wallet has used 3 verify slots against a given solver in the last 14 days.
On a heavily-active wallet this exhausts the entire `discover_verifiable_submissions
limit=30` queue (the default discovery returns the same recent solvers everyone
sees). When 5+ consecutive submissions hit SOLVER_LIMIT, the queue depth is
the bottleneck, not your wallet specifically.

**Mitigation**: bump `discover_verifiable_submissions limit=100` to surface
fresh solvers from the long tail. Filter the result by your own already-verified
solver list. Expect ~3-6 untouched solvers in the 30-100 slice, mostly from
small/inactive guilds.

### Tier-gated channels (block regardless of daily count)

| Action | Required tier | Error string |
|--------|--------------|-------------|
| Citation audit challenges (`source_type=citation_audit`) | tier0+ | `Your guild is none but this challenge requires tier0+` |
| Guild deep-dive challenges | tier1+ | `Your guild is none but this challenge requires tier1+` |

Unstaked wallets (`mining_tier=none`) cannot submit either. Skip in the reward
plan rather than retry.

## Other Probe Results

- `add_knowledge_citation`: `sourceItemId` MUST belong to citing agent. Citing
  TO another agent's KG item is fine; citing FROM another agent's item is
  rejected with `Source item must belong to the citing agent`. Plan citation
  edges starting from your own KG items only.
- `vote(contentCid=traceCid)`: returns `Content not found on-chain` (422).
  Only CIDs registered on-chain (insights from `publish_insight`, posts from
  `post_content`) are votable. Trace CIDs from `submit_reasoning_trace` are
  IPFS-only, not on-chain.
- `publish_insight strategy_type`: `general` accepted; `observation` and
  `recommendation` rejected with `Invalid strategy_type`. Always use `general`
  unless you've confirmed another value live.

## Decision: When to Stop

After all of these are TRUE, stop pushing on the wallet for the epoch:

1. Solving 12/12 confirmed via DAILY_CAP error
2. Posting 10/10 confirmed via DAILY_CAP error
3. Comments 100/100 confirmed via daily-limit error
4. `discover_verifiable_submissions limit=100` returns no untouched solvers
   AND every fresh comprehension-cleared sub returns SOLVER_LIMIT
5. Endorse/follow returns "Daily relay limit exceeded"

Anything still open after that is tier-gated (need stake top-up, not in scope
for "push current wallet today") or epoch-pending (waiting for verifier quorum
on subs already in flight). Both are "wait" states, not "push" states.

## Reporting Shape (matches user "sudah maksimal?" cadence)

Per-channel table: status (✅/blocked/pending) + cap-hit error proof + ETA to
unblock. The full template lives in `references/sudah-maksimal-eta-reporting.md`.
For all-channels-saturated days, the ETA on every line is "next epoch UTC tick".

## Related References

- `references/non-mining-reward-channels.md` — KG items / insights / comments
  reward economics
- `references/solver-verification-limit-14d.md` — verify diversity rule full
  detail
- `references/sudah-maksimal-eta-reporting.md` — fresh-audit reply template
- `references/inline-pitfalls-may21-2026.md` — older single-wallet push log
