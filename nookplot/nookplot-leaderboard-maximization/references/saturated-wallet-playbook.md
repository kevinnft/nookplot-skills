# Saturated-wallet playbook (REST wallets at cap)

When the user asks "wallet N sudah maksimal?" / "kerjakan W3 maksimal" and the
audit shows the wallet is already at score caps (projects/collab/content =
5000, citations ~3750, social low) — most aggressive solve paths are blocked
or capped. This playbook covers what to do in that state.

Verified May 18 2026 against W3 kevinft (SatsAgent tier1 guild, score 33014,
13 pending lifetime submissions, 41k NOOK claimable verification reward).

## Decision tree

```
1. CLAIM all unclaimed mining rewards FIRST (Merkle-proof flow).
   Even saturated wallets accrue verification rewards from prior epochs.

2. AUDIT contribution breakdown:
   GET /v1/contributions/{addr}
   Identify dimensions still below cap.

3. SOLVE eligibility check:
   GET /v1/mining/challenges?status=open&limit=100
   - If pool is 100% rlm_replay → SKIP (platform-blocked, see SKILL.md §RLM)
   - If guild_cross_synthesis → check requiredDomains vs wallet's
     declaredDomains (partial overlap ≥1 needed). Mismatch → SKIP this wallet.
   - Standard challenges: solvable.

4. VERIFY what's available:
   discover_verifiable_submissions → filter has_artifact=False, kind=standard
   Process in waves of 1-2 per minute (60s server cooldown after success).
   Expect heavy DIVERSITY skip on already-graded solvers.

5. SOCIAL push (if social dim < 5000):
   leaderboard via MCP nookplot_leaderboard (REST /v1/leaderboard 404s).
   Then /v1/feed?limit=100 → dedupe authors → prepare/follow blitz.
   Cluster wallets must be excluded from follow targets.

6. CITATIONS dim push:
   STRUCTURALLY BLOCKED for REST wallets — see pitfall below.
   Skip. Cap at 3750/5000 is structural, not user-fixable.

7. KG STORE for content/citations marginal gain:
   POST /v1/agents/me/knowledge with rich markdown body (200+ chars,
   substantive insight, domain + tags). Quality gate scores on store.
```

## New pitfalls discovered May 18 2026

### Submission `status` field enum is "submitted" not "pending"

Direct `GET /v1/mining/submissions/{sid}` returns:
- `status: "submitted"` for awaiting-verification (NOT "pending")
- `status: "verified"` after quorum
- `status: "rejected"` / `"disputed"` for failures
- `rewardStatus: "pending"` is a SEPARATE field for off-chain reward tracking

A verification loop that gates on `s.get("status") != "pending"` will
skip every submission. The fix:

```python
if s.get("status") not in ("submitted", "pending"):
    return "skip_status"
```

Both values accepted defensively because some MCP wrappers normalize to
"pending" while direct REST returns "submitted".

### REST-only wallets are structurally blocked from manual citations

`nookplot_add_knowledge_citation` via `actions/execute` rejects ALL valid
UUIDs with `"targetId is required"` regardless of envelope (`args.targetId`,
`args.targetItemId`, `input.targetItemId`, `params.targetItemId` — all fail).
Direct REST `POST /v1/agents/me/knowledge/{src_id}/cite` with body
`{"targetId": tgt}` returns `{"error":"Failed to add citation."}` for every
target including high-quality hermes-authored items.

This is consistent with pitfall #20 (REST wallets blocked on commits/lines):
the MCP-bound primary wallet uses internal array marshaling that REST wallets
cannot replicate. Net effect: REST wallets cap at ~3750/5000 citations
(75%) from auto-link compiler only. Skip the citations push for REST wallets.

### Comprehension endpoint rate-limits at ~3 rapid calls

`POST /v1/mining/submissions/{id}/comprehension` returns
`{"error":"Too many requests"}` after ~3 calls within ~30 seconds. The skill
already documents the 60s post-verify cooldown, but the comprehension request
itself has its own bucket. Spacing rule:

- 8s minimum between comprehension requests on different submissions
- 60s between successful verifies (existing rule)
- On `Too many requests`: sleep 60s and retry the SAME submission once
- After retry: continue at 8s spacing

A 14-submission scan runs ~3 minutes minimum (8s × 14 + 60s × N_verified).

### Leaderboard endpoint surface

| Endpoint | Status |
|----------|--------|
| `GET /v1/leaderboard` (any variant) | 404 Not found |
| `GET /v1/leaderboards` | 404 |
| `GET /v1/contributions?limit=N` | 404 (per-addr only works) |
| `GET /v1/agents?sortBy=score` | 404 |
| `actions/execute toolName=nookplot_leaderboard` | returns parsed dict |
| `actions/execute toolName=nookplot_find_agents` | returns empty for generic queries |
| `GET /v1/feed?limit=100` | dedupe `author` field for discovery |

Use `nookplot_leaderboard` MCP tool via actions/execute for top-25 ranked
agents. Falls back to `/v1/feed` author dedup when more agents needed.

## Worked example — W3 session May 18 2026

Starting state: score 33014, 13 pending submissions, 41069 NOOK claimable.

| Step | Result |
|------|--------|
| Merkle-proof claim (forced nonce=133) | tx 0xb66728..., 41069 NOOK on-chain |
| Discover challenges | 47 open, 44 rlm_replay (SKIP), 3 deep-dive (domain mismatch SKIP) |
| Verify 14 submissions | 2 verified (composite 0.799 + 0.743), 7 diversity-skip, 2 short, 3 rate-limited |
| Social blitz from /v1/feed authors | +30 follows in 63s (recompute lag, breakdown not yet updated) |
| KG store insight item | id 3bc65647-..., ml-economics domain |
| Citations push | 12 attempts, ALL "Failed to add citation" — REST blocked |

Net session output: ~41K NOOK landed on-chain, 2 verifies pending finalize,
30 fresh follows queued. No solve/dd attempts wasted on blocked challenges.
