# Mining Pool Exhaustion Patterns (May 18 2026)

When the user says "kerjakan challenge lain" and the pool is exhausted, this
reference documents the confirmed exhaustion states and correct responses.

## Challenge pool exhaustion (all non-guild challenges are RLM)

As of May 18 2026, the open challenge pool contains:
- 6 guild deep-dive (tier1+ required, 1/guild/epoch)
- 46 RLM challenges (encrypted prompts, workspace tool not available)
- 0 verifiable_code, 0 verifiable_exact, 0 standard non-RLM

The RLM dominance is structural — the platform generates RLM challenges
automatically but non-RLM challenges (BCB python_tests, citation_audit,
doc_gaps, paper_review) appear to be posted by specific agents or the
platform on a slower cadence. When the pool is 100% RLM + guild, there is
genuinely nothing submittable.

**Correct response**: Tell the user explicitly that the pool is exhausted,
list what's blocked and why, and offer alternatives (off-chain work, prepare
traces for next epoch, verification mining if not diversity-gated).

## Verification mining exhaustion (diversity gate saturated)

The 5-wallet cluster shares ONE diversity budget per external solver. With
only 4-5 distinct external solvers in the verify queue, the cluster can
exhaust all of them in 2-3 sessions (3 verifications × 4 solvers = 12 total
verifications before complete saturation).

**Detection pattern (fast-fail)**:
1. First verify attempt → diversity gate error
2. Try ONE more distinct solver → diversity gate error
3. STOP. Declare verification exhausted. Don't iterate through remaining queue.

Each failed attempt still burns:
- comprehension_challenge request (API call)
- comprehension_answers submission (API call)
- artifact inspection for python_tests (API call)
- The actual verify call that fails (API call)
= 4 wasted API calls per failed attempt

With 20 queue entries and 4 distinct solvers, naive iteration wastes 80 API
calls to discover what 8 calls (2 probes × 4 calls each) would reveal.

## Combined exhaustion state

When BOTH challenge pool AND verification mining are exhausted simultaneously,
the mining dimension of Nookplot is completely blocked. Remaining productive
actions are all off-chain:

| Action | Dimension | Cap |
|--------|-----------|-----|
| Store knowledge items | content | no observed daily cap |
| Add citations | citations | no observed daily cap |
| Comment on learnings | social | 100/day/wallet |
| Publish insights | content | ~10-15/day/wallet |
| Claim rewards | — | once per epoch per source |
| Prepare traces for next epoch | — | unlimited |

## "Kerjakan challenge lain" decision tree

```
User: "kerjakan challenge lain yang non-guild"
  │
  ├─ Check discover_mining_challenges(challengeType=verifiable_code) → any results?
  │   └─ YES → submit from all eligible wallets
  │   └─ NO ↓
  ├─ Check discover_mining_challenges(challengeType=verifiable_exact) → any results?
  │   └─ YES → submit from all eligible wallets
  │   └─ NO ↓
  ├─ Check discover_mining_challenges(challengeType=standard) → filter out RLM
  │   └─ Any non-RLM standard? → submit
  │   └─ ALL are RLM ↓
  ├─ Check discover_verifiable_submissions → any verifiable?
  │   └─ YES → try verify, fast-fail on diversity gate (2 probes max)
  │   └─ NO or all diversity-gated ↓
  └─ REPORT: "Mining pool exhausted. All challenges are RLM (unsolvable) or
     guild-exclusive (capped). Verification queue diversity-gated. Remaining
     options: off-chain work or wait for next epoch."
```

## How to identify RLM challenges without reading each one

All RLM challenges share these markers:
- Title starts with "RLM " (RLM Security, RLM Algo, RLM Bio, RLM Math, RLM Code, RLM Doc)
- submissionCount is always 0/20 (no agent has ever solved one)
- The prompt CID resolves to AES-256-GCM encrypted JSON
- verifierKind is null but submissionArtifactType would be "rlm_replay"

Quick filter: if `title.startswith("RLM ")` → skip. This avoids fetching
challenge details for challenges that are structurally unsolvable.
