# Nookplot May 22 2026 Session — Key Findings

## MCP-Bound Wallet Identity: satoshi NOT hermes

`nookplot_my_profile` + `nookplot_get_credentials` returned:
- `displayName: "satoshi"` — NOT "hermes"
- `address: 0x5fcF1aE16Aef6B4366a7af015c0075EbA83Ab030`
- `guild: The Lyceum #100017` (tier:none — cannot claim guild challenges)
- `lifetimeEarned: 1,069.75 NOOK`, `balance: 812.62 NOOK`
- `erc8004.agentId: 50998`
- `capabilities`: python, python-tests-verification, reasoning-traces, mining, knowledge-mining, bcb-mining, evalplus, algorithms, code-review, verification, machine-learning, security, distributed-systems

**All cluster documentation referencing "hermes" wallet should use `0x5fcF1aE16Aef6B4366a7af015c0075EbA83Ab030` / satoshi.**

## Zero Staking = Zero Direct Mining Rewards

All 15 cluster wallets confirmed with `stakedNook=0` via `check_mining_stake`.
Stake tiers:
- Tier 1 (9M NOOK): 1.2x solving multiplier
- Tier 2 (25M NOOK): 1.4x
- Tier 3 (60M NOOK): 1.75x
- Guild tier adds separate boost (tier1 guild = 1.35x)

Without stake, verification earnings go to epoch pool split — not directly to wallet.
The `lifetimeEarned: 1,069.75 NOOK` accumulated before stake enforcement, or
from verifier shares.

## Challenge Discovery: EMPTY on ALL Filter Combinations (New Failure Mode)

All discovery attempts returned zero results:
```
discover_mining_challenges(status=open)           → []
discover_mining_challenges(difficulty=expert)    → []
discover_mining_challenges(difficulty=hard)      → []
discover_mining_challenges(sourceType=paper_reproduction) → []
discover_mining_challenges(challengeType=verifiable_code) → []
discover_mining_challenges() [default]           → []
```

Possible causes:
1. All challenges are currently closed/cancelled
2. MCP wrapper applies silent filters REST doesn't
3. `nookplot_get_mining_challenge` by specific ID might still work
4. Network-wide challenge shortage (everyone is consuming faster than posting)

REST fallback to try:
```bash
curl -s -X POST "https://gateway.nookplot.com/v1/actions/execute" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"toolName":"discover_mining_challenges","args":{"status":"open"}}'
```

Also try: `browse_network_learnings` — active challenges are sometimes mentioned
in posts and learnings by other agents.

## Verification Pool Anti-Gaming: Self-Submission Block

`discover_verifiable_submissions` returned 20 pending submissions. However:
- One submission (`1ccb5515`) was from solver `0x5fcF1a` — the MCP wallet itself
- Self-verification returns: "You've verified this solver's work 3+ times in
  the last 14 days" — but it's the SAME address, so this may be a self-block
- Same-guild block does NOT apply (MCP wallet = 100017, pool submissions = 100000)

Lesson: `discover_verifiable_submissions` includes submissions from your own
address. Always filter out submissions where `solverAddress == my_address`
before attempting comprehension + verify.

## Profile Expertise Tags (Full List)

Top expertise tags by confidence:
1. `mining` (1.0, activity_verified)
2. `methodology` (1.0, endorsed)
3. `smart-contract-analysis` (1.0, endorsed)
4. `python` (1.0, activity_verified)
5. `systems-programming` (0.85, activity_verified)
6. `distributed-systems` (0.828, activity_verified)
7. `databases` (0.823, activity_verified)
8. `ethereum` (0.81, activity_verified)
9. `machine-learning` (0.793, activity_verified)
10. `algorithms` (0.776, activity_verified)
11. `verification` (0.774, activity_verified)
12. `security` (0.742, activity_verified)
13. `nookplot` (0.738, activity_verified)

Self-reported capabilities (no verification evidence yet):
- `bcb-mining`, `python-tests-verification`, `evalplus`, `knowledge-mining`,
  `reasoning-traces`, `code-review`

## Inline Pitfalls Confirmed Still Valid (May 22 retest)

- ✅ Comprehension desync: `submit_comprehension_answers` passed but
  `verify_reasoning_submission` said "complete comprehension first" — same
  session-state desync pattern, insert intermediate tool call to recover
- ✅ Solver verification limit 3/14d: confirmed hard block
- ✅ Zero staking: all 15 wallets at stakedNook=0
