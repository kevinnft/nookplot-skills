# Global Quality Rule — User Directive (May 18 2026)

## Status

HARD RULE, all sessions, all wallets W1-W9, all Nookplot tools (mine, verify,
post, comprehension, RLM, dataset_royalty access, citation creation). User
stated this verbatim mid-session after a deep audit reply about wallet 2 / 4
reward replication. Treat as standing constraint — load this file before any
solve / verify / post action and re-confirm the rule is being honored before
hitting any submit endpoint.

## Verbatim text

```
Untuk semua session dan semua wallet:
- Prioritaskan HIGH VALUE QUEST terlebih dahulu
- Jangan pernah asal jawab
- Jangan submit jawaban random
- Selalu analisa context/task sebelum submit
- Fokus accuracy, accepted score, reputation, dan reward maksimum

ANSWERING STRATEGY:
1. Baca seluruh task secara detail
2. Analisa requirement dan expected output
3. Cross-check context sebelum submit
4. Berikan jawaban paling relevan dan berkualitas
5. Hindari spam/repetitive answer
6. Prioritaskan accepted verification daripada speed

VERIFY RULE:
- Scoring harus konsisten dan masuk akal
- Jangan random scoring
- Review submission sebelum verify
- Fokus accepted score rate tinggi

QUEST PRIORITY:
1. High value quest
2. Reputation multiplier quest
3. Verification reward
4. Guild/inference reward
5. Contribution-heavy task
6. Remaining quests

IMPORTANT:
- Quality > quantity
- Jangan farming asal submit
- Semua action harus terlihat natural dan thoughtful
- Maintain high acceptance rate

FINAL OBJECTIVE:
Selesaikan semua high value quest dengan jawaban berkualitas tinggi untuk
memaksimalkan reward, reputation, contribution, dan accepted score rate.
```

## Operational mapping — what this means in practice

### Solve / submit_reasoning_trace

- BEFORE submit: read full challenge body, identify the actual deliverable
  shape (paper-reproduction artifact? exact answer? code? trace?), cross-check
  any required domains against the wallet's guild specializations
- traceContent must be PER-TASK, not a templated boilerplate. If the same trace
  body would fit two unrelated challenges, it is templated → rewrite
- traceSummary must score ≥34/100 on the anti-slop gate. Concrete numbers,
  named methods, explicit comparisons ("X outperforms Y by N%"), equations
  where applicable. No filler ("comprehensive", "various", "interesting").
  Min 100 chars (standard) or 50 chars (verifiable)
- Skip easy/medium spam. Allocate effort to expert (base ~6K) and hard (base
  ~2K) when both are open
- When pool is empty across ALL filters (verifiable_code, multi_step,
  standard, expert, hard), DO NOT lower quality bar by inventing solves —
  pivot to verification or posting instead, then re-poll in 30-60 min

### Verify / verify_reasoning_submission

- BEFORE scoring: read the trace IPFS body in full. Open it via the CID returned
  in the verifiable submission listing
- Scoring spread: dimensions should NOT be identical across all 4 (correctness,
  reasoning, efficiency, novelty). A submission that is correct + structured
  but unoriginal earns ~0.85/0.85/0.80/0.55 — not 0.80/0.80/0.80/0.80
- Justification text MUST reference specific content from the trace ("the
  pivot from BFS to Dijkstra in step 3 saved O(n log n)", not "good reasoning")
- Min 50 char justification, target 100-300 chars. Generic "good"/"solid"/
  "well-structured" without anchoring is anti-gaming-detected
- knowledgeInsight must be a specific takeaway, min 80 chars. Generic advice
  ("use X") is rejected by the platform validator
- Cap: 5-10 quality verifications per wallet per day under this rule (NOT the
  raw 30/day platform cap). The cluster cap of 270/day is a CEILING, not a
  TARGET — under quality rule, target ~45-90/day total cluster

### Post / mining challenges

- Each posted challenge must have: clear problem statement, concrete acceptance
  criteria, expected output shape, at least one example, domain tags that
  match real verifiable territory
- Difficulty mix per posting batch: 1 expert + 2 hard + maybe 1 medium per
  wallet — NOT 10 medium. Expert pays poster ~300 NOOK/solve passive, hard
  pays ~100, medium pays ~28
- Do NOT post placeholder or test challenges. Deleted challenges still
  consume the 24h posting cap, so a "let me try posting" trial burns a slot
  permanently for 24h

### Discover / browse_network_learnings / KG store

- Stored knowledge items must have substantive content (≥200 char body). The
  capture quality gate rejects shorter
- Citations between KG items must reflect real relationships, not fabricated
  links. `supports`/`contradicts`/`extends`/`summarizes`/`derived_from` chosen
  to match the actual semantic relationship

## Explicit anti-patterns (do NOT do under this rule)

- Mass-submit identical or near-identical traceContent across cluster wallets
- Fill verification quota with random 0.7/0.7/0.7/0.7 scoring + "looks good"
  justification just to bag epoch_verification share
- Post 10 medium-difficulty challenges per wallet to hit posting cap fast
- Submit traceContent generated from a template like "## Approach\n## Steps\n
  Step 1: I read the challenge..." — this is the slop pattern the gate flags
- Use "gas" / "gas semua" as license to bypass quality checks. The user's
  "gas tapi aman" / "gas semua maksimalkan" still imposes this rule —
  aggressive parallel execution AT QUALITY, not aggressive bypass
- Run cron / background loops for solving (user policy: agent executes inline,
  no auto-loops)

## When user says "gas verify" / "gas posting" / "gas mine"

The signal is: execute aggressively across viable wallets in parallel,
WITHOUT re-asking confirmation between each step, BUT keep this quality rule
intact. Read each task before submit. Score each verification with real spread.
Post real challenges with real acceptance criteria.

## When pool is empty

Discovered May 18 2026 18:20 WIB: `discover_mining_challenges` returned 0
across every filter (status=open, difficulty=expert/hard, type=verifiable_*
/ multi_step / standard, with and without filters). Cluster had 50/50/25/28/
25/13 pending submissions awaiting verifier quorum.

Right move under this rule when pool is empty:

1. Path A — Quality verification grind on the 20 verifiable submissions visible
   per wallet POV, 5-10 per wallet, real spreads, real justifications
2. Path B — Post 3-5 high-value challenges per wallet (mix expert/hard) using
   the 90 free posting slots
3. Path C — Idle, re-poll in 30-60 min

Wrong move under this rule when pool is empty: lower the bar, recycle old
trace template into "submit anyway", or score random verifications to fill
the 30/day cap. Idle is acceptable. Slop is not.

## Reporting back to user under this rule

When asked "sudah maksimal?" while honoring this rule, the answer should
explicitly distinguish:

- "Quality cap hit on verification: 5 high-quality verifs per wallet today,
  done — reaching the platform cap of 30 would require lowering scoring
  rigor"
- vs "Pool empty for solves, idle 45 min before next re-poll"
- vs "Posting at 3/10 per wallet — 7 slots saved for the next high-value
  challenge worth posting (don't burn slots on filler)"

The user prefers an honest "we're done at quality" over a fake "we're
maxed out" backed by 30 random 0.7-flat verifications.

## Cross-references

- references/verification-anti-gaming-constraints.md — platform-side anti-
  gaming detection patterns (5 known checks)
- references/00-hard-rules.md — pre-existing hard rules (no stake, no leave
  guild, no auto-loops, etc)
- references/sudah-maksimal-eta-reporting.md — report shape when user asks
  status / "sudah maksimal"
