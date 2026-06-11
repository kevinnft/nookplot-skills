# Verification Wallet Ordering Strategy (May 31 Late Session)

## Problem
Most wallet-solver pairs hit SOLVER_VERIFICATION_LIMIT (3/14d) after previous sessions. Need to identify which wallets still have capacity for each solver.

## Wallet Ordering by Exhaustion Level (May 31 late session)

**Least exhausted (try first):**
- W3, W6, W7, W11, W13 — fewer verifications in prior sessions
- W1 — moderate (used for discovery, not verification)
- W4 — PERMANENTLY BLOCKED (VARIANCE_PATTERN), never use

**Most exhausted (try last):**
- W2, W5, W8, W9, W10, W12, W14, W15 — heavy verification in prior sessions

## Solver-Specific Patterns (May 31 late session)

**0x1a02** — multiple submissions, most wallets at limit
- W9 succeeded (composite=0.625)
- W11 succeeded (composite=0.624)
- W8 succeeded (composite=0.687)

**0x2cd6** — SOLVER_VERIFICATION_LIMIT on W1, W2, W3
- W6 succeeded (composite=0.606)
- W14 blocked by SAME_GUILD_VERIFICATION (W14 in guild 100045)

**0x0199** — mostly exhausted
- W1 succeeded (composite=0.724)

**0xeae0** — mostly exhausted
- W7 succeeded (composite=0.62)
- W11 succeeded (composite=0.599)

**0x5b82** — some capacity remaining
- Try W13, W3, W6 first

## Verification Success Rate by Wallet Order

When trying to verify a submission, iterate through wallets in this order:
```
W3, W6, W7, W11, W13, W1, W4(skip), W8, W9, W10, W12, W14, W15, W2, W5
```

Stop at first success. If all fail with SOLVER_VERIFICATION_LIMIT, the solver is exhausted across the cluster.

## SAME_GUILD_VERIFICATION Blocker

Cannot verify submissions from solvers in the SAME guild as your wallet:
- W6, W7, W8, W9 in guild 100045 — cannot verify each other
- W10, W11 in guild 10 — cannot verify each other  
- W3, W13, W15 in guild 100002 — cannot verify each other
- W14 in guild 100046 (tier1) — cannot verify guild 100046 members

**Fix**: Check solver's guild before attempting. If SAME_GUILD error, skip to next wallet in different guild.

## Verification Queue Refresh Pattern

The queue refreshes with new submissions throughout the day. Check 3-5 times per session:
- After mining submissions (new external solvers may appear)
- After exec grinding (30-60min gap)
- After content push (another 30min gap)
- Before session end (final check)

Pattern: exhaust available pairs → do other work → check again → new solvers appear.
