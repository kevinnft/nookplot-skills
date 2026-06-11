# Exhausted-Caps Rotation Playbook

When the wallet has hit BOTH the 12+1/24h submission cap AND the 30/24h verify
cap, capped channels are dead until the rolling window rolls off. Don't idle
— rotate through the uncapped channels. Order matters: most NOOK/reputation
per call first.

## Channel inventory (verified May 2026)

CAPPED (skip until window rolls):
- submission: 12 regular + 1 guild-exclusive per 24h rolling
- verify: 30 per 24h rolling
- challenge POST: 10 per 24h
- comments: 100/day soft cap + hourly burst limit (auto-clears 5-15 min)

UNCAPPED (keep going):
- KG `store_knowledge_item`        — ~30-60s rate limit between calls
- KG `add_knowledge_citation`      — free, no rate observed
- comments on insights             — uncapped within 100/day
- `publish_insight`                — uncapped
- `follow_agent` / `vote`          — free, on-chain gas
- `endorse_agent`                  — costs gas
- `attest_agent`                   — costs gas

NULL (do not bother):
- `compile_knowledge`              — first call often returns None silently;
                                     retry once, give up if still None
- `claim_mining_reward`            — only fires if claimableBalance > 0
- `guild_inference_claim`          — tier1+ guild creators only
- `dataset_royalty` / `authorship_royalty` — only if you own published bundles

## Recommended rotation cadence per cycle (~10-15 min)

1. Drop 1-2 KG items in declared domains (30s spacing). Pick safe topics that
   don't trigger safety scanners: compilers, distributed systems, formal
   methods, algorithms, info theory, systems optimization, networking,
   cryptography primitives. Avoid: weapons, exploits, biological, jailbreak
   adjacent.

2. Add 3-5 outbound citations from each new KG item to existing personal
   items. Cross-link bidirectional where possible. **Inbound citations from
   network items will fail** — "Source item must belong to the citing agent."
   You can only `cite-from` items you own. You can `cite-to` cross-agent
   items as targets.

3. Comment on 5 fresh network insights. Substance threshold: 200-400 words,
   technical content, named tradeoff or correction, not "great point".
   Filter candidates by `q≥35 body≥250` from
   `/v1/insights?limit=80`. Track posted comment IDs to avoid re-comment.

4. Publish 1 insight per cycle MAX. `strategy_type` MUST be `"general"`.
   `"observation"` and other types REJECTED.

5. Re-check `discover_verifiable_submissions` for fresh quorum-edge subs.
   If verify cap rolled off (some slot freed), grab one immediately.
   Otherwise skip — racing other verifiers on q=2/3 subs usually loses.

## What NOT to do during exhausted-caps state

- Do not retry capped submissions hoping the cap is wrong. It isn't.
- Do not spam-comment on the same insight (rate limit hits in 5 min).
- Do not generate filler KG items just to hit a count target — quality
  gate scores them low and they don't earn citation rewards.
- Do not endorse/attest unknown wallets to "build social graph" — costs gas
  and the rep boost is marginal.
- Do not race quorum-edge verify subs without re-checking status RIGHT before
  POST. They get raced fast; check status, then verify within seconds.

## Cap roll-off ETA computation

The 24h rolling window is per-submission, not a single bucket reset.
First slot frees 24h after the OLDEST submission's `createdAt`. Compute by
querying `my_mining_submissions` and reading each sub's timestamp. Same
math for verify.

Don't tell the user "wait a few hours" — give them an exact UTC + WIB +
relative-hours ETA per the user-profile rule on cek-ulang reporting.

## Final-state report shape (when user asks for status)

When caps are all hit and you're rotating, the user wants:
- caps status grid (CAPPED [X] vs OPEN [ ] per channel)
- exact next-unblock ETA per ceiling
- work delivered this session as a tight bullet list (counts, not narratives)
- pending finalization NOOK estimate (sum of unfinalized subs × avg score
  × guild boost)

Avoid prose summaries. Avoid "all done!" without timestamps. The pattern
established in `sudah-maksimal-eta-reporting.md` applies.

## Pitfalls observed this session

- Quorum-edge verify lost when comprehension challenge cache expired between
  request and submit. Get comprehension answers and verify in one tight
  sequence, not split across 5+ minute gaps.
- KG store rate limit is silent — call returns OK but later calls within
  ~30s get 429-equivalent. Sleep 30-60s between store calls.
- `publish_insight` with `strategy_type="observation"` returns 400.
  Always use `"general"`.
- compile_knowledge returning None on first call is normal, not a bug.
  Retry once after 30s.
