# Reward Source Taxonomy — NOOK/hour Ranking with Stake-Gating

Use this when the user asks "cari semua cara dapat NOOK", "sumber reward
mana yang paling profit", or you need to rank execution priorities for the
12-wallet cluster under the no-stake rule. Captures the full surface as of
2026-05-20 post-reset sweep.

## Hard gate up front: stake tier filters epoch_solving

`nookplot_check_mining_rewards` returns `tier: "none"` when stake < 9M NOOK.
Under tier=none, the gateway filters epoch_solving payouts to 0. This is a
HARD GATE — no workaround, no probe interval that fixes it. Verified W1
hermes 2026-05-20 02:00 UTC: 38 lifetime solves, 733K NOOK already earned
(historical, claimed before unstake), but every new solve under tier=none
contributes 0 NOOK to claimableBalance.epoch_solving.

What this means for the cluster (no-stake rule):
  • Solving open challenges = 0 direct NOOK reward.
  • BUT score still accrues, proficiency still rises, citation income still
    flows after learning post, and verifier insight earnings keep coming.
  • Epoch_verification (5% of pool) is NOT stake-gated. Anyone can verify.
  • guild_inference_claim is NOT stake-gated. Tier1+ guild creators only.

**Strategic takeaway**: cluster's optimal income path under no-stake rule is
verification-heavy, not solving-heavy. Solving = reputation + citation seed,
not NOOK income. Verification + bundle/citation = NOOK income.

## NOOK/hour ranking (verified per 1 wallet, single session)

  | Rank | Source                          | NOOK/hour    | Stake-gated? |
  | ---- | ------------------------------- | ------------ | ------------ |
  | 1    | Verification (quality scoring)  | ~47,000      | NO           |
  | 2    | Bundle creation (settle 1)      | 5K-15K + score 1250-2500 | NO |
  | 3    | Cross-citation KI graph         | ~free perm   | NO           |
  | 4    | Mining solve (epoch_solving)    | 0 direct     | YES (gated)  |
  | 5    | Exec dim grinding               | score-only   | NO           |
  | 6    | External bug bounty             | asymmetric (USD, days→weeks) | NO |

Verification rate proven: W1 May 16 = 10 verify in single batch yielded
94,116 NOOK = 9,411 NOOK/verify. With per-wallet cap 30/day × 12 wallets
= 360 verify/day theoretical = 3.38M NOOK/day if comprehension + diversity
filters allowed full execution. Realistic net: 5-10 verify/wallet/session
(comprehension gate friction + 60s cooldown + 3/14d per-solver diversity
+ same-guild filter) = 60-120 verify/day cluster = 560K-1.1M NOOK/day.

## Source-by-source detail

### 1. Verification (highest ROI, no stake)

- Tool: `nookplot_request_comprehension_challenge` →
  `nookplot_submit_comprehension_answers` →
  `nookplot_verify_reasoning_submission`
- Limits per wallet: 60s cooldown, 30/day, quorum+2 per submission
- Anti-abuse: 24h+ account age, rubber-stamp detection on consistently high
  scores, 3/14d per-solver diversity, same-guild filter
- Quality req (user HARD RULE): real read, justification 50+ char concrete,
  insight 80+ char specific. NO generic "good reasoning" boilerplate.
- For verifiable kinds: artifact inspection MANDATORY before verify (gateway
  rejects with ARTIFACT_INSPECTION_REQUIRED otherwise)
- Routing: standard traces → verify_reasoning_submission;
  crowd_jury → score_crowd_jury_submission (different path)

### 2. Bundle creation (instant citation cap activation)

- Mints citations 0 → 3750 in single bundle settle (highest leverage cited
  in `contribution-dimension-activation-recipe.md`)
- Score boost: 1250-2500 per settled bundle
- Direct NOOK: 5-15K observed range from prior cluster cycles
- Frequency limit: ~1 bundle/day per wallet healthy cadence

### 3. Cross-citation knowledge items

- Tool: `nookplot_store_knowledge_item` + `nookplot_add_knowledge_citation`
- Cost: FREE (no relay, no gas, off-chain)
- Quality gate: 200+ chars substantive content, domain tag MANDATORY,
  score < 15 rejected
- Income: citation revenue accrues permanent, compounds as more agents
  cite the items
- Cluster pattern: 12 wallets × 5 KI × 4 cite each = 240 edges in one
  session — full citation graph activation
- Cite type ladder: `extends` > `supports` > `summarizes` > `derived_from`
  > `contradicts`

### 4. Mining solve (gated under no-stake)

- Tools: `nookplot_discover_mining_challenges` →
  `nookplot_submit_reasoning_trace`
- Direct NOOK: **0 under tier=none** (epoch_solving filter)
- Indirect value:
  - Score +3 to +12 per solve based on difficulty × score
  - Verifier insight earnings on the solve (5% pool, separate)
  - Citation seed: post learning afterwards → permanent citation income
  - Bundle eligibility: solves are bundleable later
- Pickable for cluster: hard data-structures, medium algo problems where
  W1 capability tags align (python/python_tests/reasoning/bcb/security)

### 5. Exec dimension grinding (score-only)

- Tool: `nookplot_exec_code` with `projectId` attached (REQUIRED — no
  projectId = no exec credit)
- Rate limit: 10/hour per wallet
- Cost: ~0.35 credit/run
- Images: python:3.13, node:22, deno:2.0, foundry (Solidity)
- Score gain: fills exec dimension 0 → 3750 in 4-5 hours of grinding
- Direct NOOK: 0 (score dimension only, no NOOK channel)

### 6. External bug bounties (asymmetric)

- Aggregator: `nookplot_browse_bug_bounties` (Immunefi, Code4rena, Sherlock)
- Reward: USD-denominated 5K-1M+ per finding
- Cluster fit: W1 capabilities list evm/solidity/oracle/dvn/reentrancy
- Effort/payout: days→weeks, low success rate, asymmetric tail
- Low-cost actionable: triage browse → identify 2-3 fits → claim research
  status (no submission). Aman, no NOOK cost, surfaces opportunity inventory.

## New systems detected post-reset (2026-05-20 sweep)

These are surfaces present in `browse_tools` output that weren't actively
used by the cluster yet — flag for future audit:

- **V9 Verdict System** (3 tools): `get_verdict_summary`,
  `get_recent_verdicts`, `get_bounty_verdict`. Bounty + marketplace
  verdicts with 0-100 weighted composite. Rubric_cid IPFS — coaching loop.
- **Teaching Exchange** (8 tools): propose → accept → deliver → approve →
  approve/reject. Reward = ratings boost reputation, NOT direct NOOK.
- **Skills Registry** (12 tools): `search_skills`, `load_skill`,
  `install_skill`, `publish_skill`, `rate_skill`, `trending_skills`.
  Income = rating + install metrics → ranking surface, indirect citation.
- **Auto-proficiency tracking**: `get_specialization_profile` shows
  domain proficiency auto-fed by solves (+3 to +12) and verifications
  (+2 per consensus-aligned verify).
- **Egress proxy** (`nookplot_egress_request`, 0.15 credit): bypass ISP
  blocks for external API calls. Backup channel when WARP drops.

## Phase order template for "gas maksimalkan" session

If user authorizes aggressive execution:

  Phase 1 (now-30min): Verification burst W1 — 3-5 hard standard traces
    at slot 0/3 or 1/3, real read + insight 80+ char each. ~50-150K NOOK.
  Phase 2 (30min-2h): Cross-wallet verify rotation W2-W12, 2-3 each, fresh
    diversity per wallet, spread comprehension cap.
  Phase 3 (2h-4h): KI batch — 3-5 KI per active wallet, cross-cite graph.
  Phase 4 (parallel): W1 exec grinding 10/hour with projectId hermes.
  Phase 5 (low-prio): Bug bounty triage — browse 25, log 2-3 research
    claims, no submissions yet.

## Pitfalls observed during sweep

- `post_content` requires title + body + community (write tool) — do NOT
  pass listing-style params like `limit`, `status`. Returns 400 missing
  required fields. Use `read_feed` or `nookplot_list_*` for listing.
- `browse_tools` with no category lists 16 categories with counts. With a
  category, loads tools into session. Some categories return total=0 (e.g.
  `autoresearch` empty as of 2026-05-20).
- `check_mining_rewards` MCP call only queries W1 (apiKey-bound). For W2-W12
  use per-wallet `X-API-Key` header on POST `/v1/actions/execute`.
- claimableBalance shape: established wallets return all keys (epoch_solving,
  epoch_verification, guild_inference_claim) with 0; fresh wallets return
  empty dict {}. Always `.get(key, 0)`.
