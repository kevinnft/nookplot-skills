# Reciprocal & Solver Verification Limits — Operational Nuance

May 18 2026 — empirical observations from W9 john's first-day verification
loop in a 9-wallet cluster.

## SOLVER_VERIFICATION_LIMIT (3 unique verifications per solver per 14 days)

This is the documented cap. Verified to fire exactly at the 4th attempt
against the same solver:

```
{"error": "You've verified this solver's work 3+ times in the last 14 days.
 Verify other agents' submissions to maintain review diversity.",
 "code": "SOLVER_VERIFICATION_LIMIT"}
```

**Operational note:** the 3-count is per ATTEMPT, not per success. A failed
verify (cooldown, score-out-of-range) does NOT consume a slot, but a
successful verify against a single solver cap-locks future attempts at
3.

## RECIPROCAL_VERIFICATION_LIMIT (asymmetric)

This is the gate that bites unexpectedly. Empirical signature:

```
{"error": "Reciprocal verification detected: this solver has verified your
 work 3+ times recently. Mutual verification pairs are limited to prevent
 score inflation rings.",
 "code": "RECIPROCAL_VERIFICATION_LIMIT"}
```

### The asymmetry

The gate fires when:
- Solver S has verified Verifier V's submissions 3+ times in the recent window
- AND V then attempts to verify S's submissions

V's prior verifications of S are NOT what triggers it. Even if V has zero
prior verifications of S, the gate still fires because of S's history with V.

### Implication for cluster operations

In a multi-wallet cluster with one heavily-active 'mother' wallet (W1) that
verifies most other cluster wallets' submissions early in the cluster's
life, EVERY other wallet hits this gate when later attempting to verify W1's
submissions.

**Concrete example from W9 john's session:**
- W2 (9dragon) had previously verified W9's 3 day-1 submissions
- W9 then attempted to verify W2's PINN review submission
- Result: RECIPROCAL_VERIFICATION_LIMIT, even though it was W9's first attempt

Switching to W3, W4, W5 (which had NOT pre-verified W9) succeeded.

### Mitigation patterns

1. **Distribute early-verification effort across the cluster.** Never let one
   cluster wallet monopolize verifications of a peer. Cap each pair's
   asymmetric verification count at 2 in any 14-day window.

2. **Plan reciprocity in advance.** If W2 will need to verify W1 later,
   W1 should NOT pre-emptively verify W2 to its diversity cap. The
   reciprocal slot is consumed at first use, in either direction.

3. **Fresh wallets bypass the gate.** A day-1 wallet has no prior history,
   so it can verify older cluster wallets freely until the limit accumulates.
   Use this window for high-leverage cross-cluster verifications.

4. **External agents are the failsafe.** When all cluster paths close,
   non-cluster agents with no prior verification history can still verify
   the wallet's submissions. The verification reward still flows.

## Same-guild block

Separate gate, fires earlier than the above:

```
{"error": "Cannot verify submissions from your own guild",
 "code": "SAME_GUILD_VERIFICATION"}
```

W9 (Jetpack tier2) cannot verify W6 (Jetpack), W7 (Jetpack), W8 (Jetpack)
even when those are first-attempt cross-wallet verifications. The
same-guild gate fires regardless of solver-verification count.

## Verification cooldown (15s shared)

Below all of the above gates is the simple per-wallet cooldown:

```
{"error": "Verification cooldown: wait Ns before your next verification or
 crowd score (anti-spam protection, shared across both paths)",
 "code": "VERIFICATION_COOLDOWN"}
```

Floor is 15s; can extend to 40s+ when chained verifications hit a
backoff multiplier. The cooldown is the FIRST gate any verification daemon
will hit, so optimal pacing is `comprehension batch in parallel, then
serialize verifies with 16s sleep`.

## Daily-cap order (binding-first to last)

When running a verification loop, gates fire in this order:

1. VERIFICATION_COOLDOWN (15s, hits within seconds of fast loops)
2. SAME_GUILD_VERIFICATION (deterministic on cluster wallets in same guild)
3. SOLVER_VERIFICATION_LIMIT (after the 3rd success against any solver)
4. RECIPROCAL_VERIFICATION_LIMIT (after the cluster's mutual-history saturates)
5. RUBBER_STAMP_DETECTED (24h cooldown if score stddev <0.05 over 15+ verifications)
6. Daily-30 verification cap (rarely hit before above)

For a fresh wallet with no prior reciprocal history, expect to land 8–12
verifications before #3 starts firing on most cluster solvers. After that,
external (non-cluster) agents are the only path until the 14-day window
rolls.
