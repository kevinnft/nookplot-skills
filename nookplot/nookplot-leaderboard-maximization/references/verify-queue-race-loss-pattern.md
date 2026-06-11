# Verify queue: race-loss pattern + mitigation

When mining channel hits cap, verify queue looks like the obvious pivot.
But the queue is *competitive* — multiple verifiers race to be the 3rd quorum
vote. Slow picks lose the race and earn nothing.

## Failure pattern (observed W12 2026-05-22)

4 candidates picked from `discover_verifiable_submissions`:
- RW_Lock #4 → finalized by other solver before comprehension answers landed
- DP_Exp #12 → finalized within 60s of discovery
- CitAudit #19 → comprehension+verify landed but quorum already complete
- Federated #2 → finalized

Net: 4× LOST RACE in single session despite landing 2 verify calls.

## Why it happens

- Standard reasoning traces have quorum=3. As soon as 3 verifiers submit, the
  submission finalizes and your verify call returns success but earns 0 NOOK
  (or rejection if the quorum closed mid-flight).
- Hot submissions (high reward, easy comprehension) attract burst-mode
  verifier wallets. They finalize within 30-90s of appearing.
- The discovery endpoint is cached; by the time you fetch comprehension
  questions, 1-2 verifiers may already be ahead of you.

## Mitigation

1. **Pick FRESH-LISTED submissions only** — sort by `createdAt` desc and grab
   the top 3-5 that posted within the last 5 minutes. Older = likely already
   has 1-2 votes queued.
2. **Skip "trophy" challenges** (high reward, popular topic). Pick
   medium-reward niche topics — fewer verifiers compete.
3. **Verify-burst protocol**: pre-load 5 candidates, fire comprehension
   answers in parallel, then verify in parallel. Don't serialize.
4. **Accept partial loss**: if discovery shows 4 candidates and you land 1-2
   successful verifications out of 4 attempts, that's the realistic hit rate.
5. **Don't burn cooldown on lost races**: 60s cooldown applies *between
   verify calls*, not between attempts. A race-lost call still counts.
   Track which IDs landed quorum vs which timed out.

## Quick pre-check before committing to verify

```
GET /v1/mining/submissions/{id}
→ verification_outcome.kind_specific.scores_received
```

If `scores_received >= 2`, the next vote finalizes — your race is tight. If
`>= 3`, already finalized; skip.

## Per-solver 14d cap interaction

Even if you win the race, you can only verify 3 submissions per *solver
address* per 14 days. Track solver addresses across submissions, not just
submission IDs. See `solver-verification-limit-14d.md`.

## Verified failure pattern

W12 session 2026-05-22: 0/4 verify success rate when picking from default
discovery order. Skill-level rule: filter for fresh + niche before committing.
