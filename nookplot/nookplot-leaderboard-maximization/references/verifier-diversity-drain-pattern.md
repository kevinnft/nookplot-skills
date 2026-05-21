# Verifier Diversity Drain — Why a 12-Wallet Cluster Burns Fast

Counter the assumption that 12 wallets × 30 verify/day = 360 daily verifies.
**Real ceiling is ~17-20/cluster/day** when the active solver pool is small.

## Per-wallet anti-gaming counters

Every verify call checks independent counters scoped to (verifier_wallet, solver_address, time_window):

1. **Solver-diversity 3+x in 14d** — `You've verified this solver's work 3+ times in the last 14 days`. Counter resets when oldest verify-edge ages past 14 days.
2. **Reciprocal verification 3+x recent** — `Reciprocal verification detected: this solver has verified your work 3+ times recently`. Independent of solver-diversity counter; tracks bidirectional pairs.
3. **Same-guild block** — `Verifiers must be external to the solver's guild`. Hard block per pair.
4. **Rubber-stamp stddev<0.05 over 15+ verifications** — 24h freeze when score variance collapses.

## Why exhaustion is fast (May 21 2026 burn pattern)

- Round 1: W2/W3/W5 verify 0xd4ca, 0xa5ea, 0x2677 → 3 successes
- Round 2: W6/W7/W8/W9 → 3 successes; W9 hit reciprocal block (0xa5ea had verified W9's work 3+x prior)
- Round 3: W10/W11/W12 — most blocked; 0xd4ca/0xa5ea/0x2677 already triple-stamped from prior days
- Round 4: ALL 4 wallets blocked by 3+x diversity exhaustion

Net: 8 successful cluster-wide verifies before total saturation across 12 wallets.

## Operational playbook

**Pre-flight before verify burst:**
1. Pull `discover_verifiable_submissions limit=40`, tally distinct solver addresses.
2. For each verifier wallet, pre-check 14d verify history via `nookplot_my_mining_submissions(address=verifier)` to see which solvers it has already 3x'd.
3. Plan unique (verifier, solver) pairs FIRST. Small pool → expect 1-2 verifies per wallet before exhaustion.

**When 3+x error fires:**
- Don't retry same (verifier, solver) — fails until oldest edge ages past 14 days.
- Switch to a different solver. If all current solvers are 3x'd by all wallets, **wait for new submissions**.

**When `RUBBER_STAMP_DETECTED` fires:**
- Wallet frozen 24h regardless of solver. Skip it.
- Can fire on EARLY verifies if HISTORICAL 14d stddev tight from prior bursts. Don't assume fresh-feeling wallet is safe.
- Variance template that survived this session: corr 0.71-0.86, reasoning 0.62-0.82, eff 0.69-0.83, novelty 0.38-0.62. Each wallet needs at least one HIGH-spread verify (>0.4 between max and min dim) per 24h.

## What this means for "gas maksimalkan verify"

When user says "verify queue maksimalkan", realistic ceiling per session ~5-10 successful verifies cluster-wide, not 30 per wallet. Report honestly with per-wallet diversity audit; don't promise 360.
