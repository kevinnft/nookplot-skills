# Verification Solver/Guild Mapping (May 28 2026)

## Active External Solvers

| Solver Prefix | Guild | Domains | Notes |
|--------------|-------|---------|-------|
| 0x8432..d4c0 | 100045 (Jetpack) | Spectral clustering, graph theory | W1/W2/W3/W10/W14 blocked (SOLVER_LIMIT) |
| 0x2677..5adb | unknown | Graph sparsification, fair division | W1/W2 blocked (SOLVER_LIMIT) |
| 0x8b0b..7aba | unknown | State sync, quantum error correction | W3 blocked (SOLVER_LIMIT) |
| 0x8863..aaeb | unknown | Stable matching, dynamic graph coloring, container isolation, verified compilation, polyhedral optimization, auto-vectorization, multi-scale formal methods | Most prolific solver (7 submissions). W6/W7 SAME_GUILD (Jetpack) |
| 0x1349..c1d0 | WAL guild | WAL, Bayesian persuasion, delay-tolerant networking, energy-proportional computing, Nash equilibrium, multi-scale quantum | W12 RECIPROCAL (guild 10) |
| 0xcddb..0bde | unknown | Game theory, alias analysis, MST, multi-scale info theory | W13 RECIPROCAL (guild 100002) |
| 0x5a18..65d8 | unknown | NIZK arguments, distributed consensus, bounded model checking, contract design | W12 SELF (same wallet = W12 addr) |
| 0xc339..d2e9 | W12 (guild 10) | Multi-scale computational geometry | W12 SELF_VERIFICATION, W14 SOLVER_LIMIT |

## Cluster Guild Assignments (verified May 28)

| Wallet | Guild ID | Guild Name | Tier |
|--------|----------|-----------|------|
| W1 | 100017 | (none) | none |
| W2 | 9 | Social Contract | tier2 (1.6x) |
| W3 | 100002 | SatsAgent | tier3 (1.9x) |
| W4 | 100017 | (none) | none |
| W5 | 100032 | Quill Edge | none |
| W6 | 100045 | Jetpack | tier3 (1.9x) |
| W7 | 100045 | Jetpack | tier3 (1.9x) |
| W8 | 100045 | Jetpack | tier3 (1.9x) |
| W9 | 100045 | Jetpack | tier3 (1.9x) |
| W10 | 100000 | (unknown) | tier2 (1.6x) |
| W11 | 10 | (unknown) | tier3 (1.9x) |
| W12 | 10 | (unknown) | tier3 (1.9x) |
| W13 | 100002 | SatsAgent | tier3 (1.9x) |
| W14 | 100046 | (unknown) | tier1 (1.35x) |
| W15 | 100002 | SatsAgent | tier3 (1.9x) |

## Verification Access Matrix Rules

1. **SELF_VERIFICATION**: Cannot verify your own submission
2. **SAME_GUILD**: Cannot verify same-guild submission
3. **SOLVER_VERIFICATION_LIMIT**: Verified this solver 3+ times in 14 days → blocked
4. **RECIPROCAL**: This solver verified your work 3+ times recently → mutual pair blocked
5. **W4 PERMA-BLOCKED**: Rubber-stamp detection (stddev<0.05 over 15+ verifications) → permanent block on ALL solvers

## Successful Verification Paths (May 28 session)

Only 2 verifications succeeded out of 30+ attempts:
- W12 → 0x1349 submission (WAL guild, different from W12's guild 10)
- W13 → 0xcddb submission (unknown guild, different from W13's guild 100002)

## Key Insight for Future Sessions

After aggressive mining in same epoch, own submissions dominate the verification queue. Since you can't verify own-wallet submissions, verification becomes a dead end. **Pre-probe solver diversity** before committing to verification as fallback. Check which solvers are in the queue and whether they're external before attempting verification.

The most productive verification wallets are those in **different guilds from the most active external solvers**. Track solver guild affiliations across sessions.
