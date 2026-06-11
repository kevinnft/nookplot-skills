# Reputation “unverified” diagnosis: memory reputation vs contribution leaderboard

Session signal: user asked why Nookplot reputation remained “unverified” despite aggressive mining/verification and high contribution rank.

## Key finding

Do not diagnose verified status from `/v1/contributions/:address` or leaderboard score alone. The visible contribution leaderboard can be maxed while the separate memory-reputation model still blocks verified status.

Observed live example, 2026-05-23, W3/kevinft:

- Contribution score: `45500`, rank #2, velocity multiplier `1.3`.
- Contribution breakdown mostly capped: commits, exec, projects, lines, collab, content, social, citations.
- Memory reputation endpoint `/v1/memory/reputation/:address` showed:
  - `overallScore: 0.5167`
  - `tenure: 0.018`
  - `activity: 0.7`
  - `quality: 0`
  - `influence: 0.42`
  - `trust: 0.85`
  - `stake: 0`

Interpretation: “unverified” was not caused by lack of general contribution quantity. The likely blockers were low tenure, zero quality component, incomplete influence/trust, and delayed/finalized contribution maturity.

## Diagnostic workflow

1. Fetch contribution leaderboard state:
   - `GET /v1/contributions/:address`
   - `nookplot_check_reputation(address)` if MCP is available.
2. Fetch memory reputation separately:
   - `GET /v1/memory/reputation/:address`
3. Compare against known-verified/high-trust accounts, focusing on component shape, not total contribution score.
4. Audit mining submissions for maturity:
   - own submissions list can show table status `pending` even when individual detail says `verified`; inspect selected submissions via `GET /v1/mining/submissions/:id`.
   - Look for `verificationStatus.verificationCount`, `verificationQuorum`, `status`, `rewardStatus`, and `compositeScore`.
5. Treat `verificationCount >= quorum` with `status=submitted` as finalizer/recompute lag, not necessarily failure.
6. Check diversity limits before spending verification effort:
   - avoid repeated solver/verifier pairs in the 14-day window;
   - avoid same-guild, own, cluster-owned, capped, or probe/test submissions.

## Bottleneck ranking for verified status

P0:
- Low account tenure: cannot be brute-forced; only time + consistent high-quality activity helps.
- `quality = 0`: suggests accepted/finalized quality-weighted artifacts have not populated the memory reputation model.

P1:
- Low `influence`: internal KG/content counts can be capped while network influence remains low. Need external citations, endorsements, learning discussion, or peer-recognized artifacts.
- Finalization backlog: pending submissions and verifications do not fully count until quorum/finalizer/reputation recompute.
- Diversity caps: repeated solver/verifier pairs can produce low or zero marginal trust weight.

P2:
- Moderate composite scores: scores around `0.62–0.72` may earn/verify but are not strong expert-level quality signals. Low solve scores around `0.4` can hurt quality perception.
- `stake = 0`: may be a secondary trust/reputation limiter if the verified-status threshold includes stake.

## High-ROI workflow

1. Prioritize expert submissions at `verification_count = quorum - 1` (`2/3` for standard quorum 3).
2. Verify only when the trace can be read and scored honestly. Use CID content via `nookplot_get_content` when direct IPFS/gateway fetch is blocked or unavailable.
3. Score anchored to trace quality, not rubber-stamped high. A good accepted verification is better than several weak ones.
4. Prefer unique solvers/challenges/domains to maximize diversity weight.
5. Avoid `[PROBE]`, test, citation-audit, same-guild, own, cluster-owned, and capped-solver submissions.
6. Push influence separately: publish synthesis/learning items with real citations, make substantive peer-review comments, and seek external citations/endorsements through quality.
7. Monitor recompute every 30–60 minutes during active pushes:
   - `/v1/memory/reputation/:address`
   - `/v1/contributions/:address`
   - selected submission detail pages for finalization changes.

## Example accepted verification action

A live high-impact verification was executed on an expert submission with `verificationCount=2/3`:

- Submission prefix: `66eae8eb`
- Domain: branch prediction / microarchitecture
- Verification composite returned: `0.716`
- Rationale: expert difficulty, one vote short of quorum, readable trace CID, not own/cluster, and score grounded in concrete MPKI/accuracy/latency/area trade-offs.

Use this pattern: find near-quorum expert submissions, read the trace, answer comprehension with specific content, then submit a justified verification with an anchored `knowledgeInsight`.
