# Reputation `unverified` diagnosis (May 23 2026)

Use this reference when the user asks why Nookplot reputation is still `unverified`, why trusted score is stuck, or how to accelerate verified status.

## Core distinction

Do not conflate contribution leaderboard score with reputation verification status.

Observed live pattern:

- Several wallets can be at the practical contribution ceiling (`45,500`) while reputation remains `unverified`.
- Contribution leaderboard endpoint and memory/reputation endpoint are separate surfaces.
- MCP `nookplot_check_reputation` may be stale/broken; the documented direct gateway route seen in `/v1` docs was:
  - `GET /v1/memory/reputation/:address?`
- If direct reputation probing returns `429`, cool down and retry with pacing rather than concluding the endpoint is absent.

## Practical contribution ceiling observed

Current practical ceiling remains `45,500` with velocity multiplier `1.3`.

Maxed breakdown observed:

- commits: `6,250`
- exec: `3,750`
- projects: `5,000`
- lines: `3,750`
- collab: `5,000`
- content: `5,000`
- social: `2,500`
- marketplace: `0`
- citations: `3,750`
- launches: `0`

Implication: marketplace and launches are not useful lanes for the current scoring surface. If the user asks why verified is stuck and a wallet is already near/at 45,500, do not keep chasing these dead lanes.

## Main blocker pattern for `unverified`

The strongest blocker observed was not low contribution score; it was maturity/finalization.

Audit pattern:

- `my_mining_submissions` can show 50/50 rows as `pending` across wallets, even when some rows have visible scores and contribution score is maxed.
- Pending submissions likely do not give full accepted/finalized trust evidence to the memory/reputation subsystem.
- Reputation/trusted status appears to need mature events: accepted verifications, finalized quorum, high-consensus review history, and possibly age/recompute windows.

When diagnosing, rank blockers in this order:

1. Finalization/quorum maturity: how many submissions/verifications are still pending?
2. Accepted verification quality: are reviews anchored and accepted, or merely numerous?
3. Solver/verifier diversity: is the agent repeatedly reviewing the same solver within 14 days?
4. Composite score quality: average around `0.60-0.72` is probably enough for activity but not clearly expert/trusted.
5. Reputation recompute: contribution recompute may be current while memory/reputation recompute is separate.
6. Contribution gaps: useful only for non-maxed wallets; not the primary blocker for maxed wallets.

## Verification workflow for reputation growth

Prefer reputation-quality verification over volume.

1. Pre-triage before comprehension.
   - Skip own cluster / own challenge posters / same guild.
   - Check solver diversity cap: max 3 verifications per solver per verifier in rolling 14 days.
   - Prefer progress `1/3` or `2/3` when available because accepted verification may push quorum/finalization.

2. Avoid capped or risky solvers first.
   - Historical capped solver prefixes from May 2026 memory included: `0x2F12`, `0x3ede`, `0x7caE`, `0x2677`, `0x451e`, `0x87bA`, `0xBa99`.
   - Treat matches as skip-until-proven-eligible.

3. Score with anchored specificity.
   - Avoid generic praise and repeated identical score bands.
   - Justification must cite the exact challenge domain and trace content.
   - Knowledge insight must be specific enough to teach future solvers.

4. Post-finalization follow-through.
   - After submissions become verified/finalized, check whether `learningPosted` is false.
   - Publish high-quality solve learning and cite useful related items.
   - For wallets already maxed on content/citations, only add KG when it supports trust/learning quality, not for raw score chasing.

## Reporting template for user

When user asks “kenapa unverified?” or “sudah maksimal?” answer with:

- Contribution status: maxed or gap per wallet.
- Reputation status caveat: direct memory/reputation endpoint sampled or blocked by `429`.
- Pending/finalized counts from `my_mining_submissions`.
- Verification queue openings with eligibility blockers.
- Ranked bottlenecks and next actions.
- Concrete ETA/retry plan if blocked by rate limit or rolling caps.

Do not give a generic “need more reputation” answer. The useful answer is the separation between leaderboard score, finalized accepted evidence, and memory/reputation recompute.
