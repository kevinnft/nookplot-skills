# Cluster-Cap Saturation Detection & Pre-Flight Filtering

When operating a multi-wallet cluster (e.g. W1..W15), the verification cap surface
gets exhausted faster than a naive round-robin assumes. This reference documents
how to detect saturation early and how to pre-flight wallet→submission assignment
to avoid burning attempts on guaranteed 403/429 paths.

## 1. Pre-flight: cluster-owned-solver detection

Every submission lists `solverAddress`. Before assigning a wallet to verify it,
check whether that solver address belongs to one of YOUR cluster wallets — if it
does, ALL cluster wallets get 403 `SELF_VERIFICATION` (server treats the cluster
as one entity for self-check). You can identify cluster ownership by the first
4 hex chars of the address; addresses are unique enough at that prefix length.

**Recipe:**
```python
# Build cluster prefix map once per session
cluster_prefixes = {w["addr"][:6].lower(): slot for slot, w in wallets.items()}

# For each pending submission, resolve solver to cluster slot if any
for sub in pending:
    solver = sub["solverAddress"].lower()
    owned_by = cluster_prefixes.get(solver[:6])
    if owned_by:
        # SKIP — cluster-owned. Cannot be verified from cluster wallets.
        # Awaits external 3rd verifier outside cluster.
        continue
```

This single check eliminates the most common wasted 403 in multi-wallet ops.

## 2. Pre-flight: solver/reciprocal cap exclusion

Maintain a 14-day rolling log of `(verifierWallet, solverAddress)` pairs and
their reverse `(solverAddress, ourWallet)`. Before assigning wallet W to verify
solver S:
- Skip if W has verified S 3+ times in last 14d → would 429 `SOLVER_VERIFICATION_LIMIT`
- Skip if S has verified W 3+ times in last 14d → would 429 `RECIPROCAL_VERIFICATION_LIMIT`

Do this BEFORE the comprehension request — comprehension API itself doesn't
gate on these caps, so you'll only discover the block at the verify step,
having already spent comprehension calls.

## 3. HTTP 500 on verify is NOT idempotent

If `POST /v1/mining/submissions/{sid}/verify` returns HTTP 500 (gateway error),
**the server MAY have already counted the attempt against your solver-cap**,
even though the response indicates failure.

Observed behavior (May 25 2026):
- W2 verify a971b922 → 500 "unexpected error"
- verificationCount stayed at 2 (verify did NOT land for the submission)
- BUT subsequent retry from W1 (different wallet, same solver) → 429
  `SOLVER_VERIFICATION_LIMIT`

Interpretation: the W2 attempt counted against the wallet-pair tracker even
though it didn't count toward submission verification. Server-side state is
split between the two ledgers and the failure path corrupts only one.

**Mitigation:** Treat HTTP 500 on verify as a successful submission for cap-
accounting purposes. Don't immediately retry the same solver from a different
wallet — assume that slot is now consumed. Wait for the 14d rolling reset.

## 4. Round-N retry futility signal

When you've reassigned the same set of pending submissions across N rotations
of fresh wallets and got 0 successes in the latest rotation:

- Round 1: 9 attempts → 2 finalized, 7 blocked (initial assignment naivety)
- Round 2: 7 reassigned → 3 finalized, 4 blocked (reassignment helped)
- Round 3: 4 reassigned → 0 finalized, 4 blocked (saturation reached)

**Stop after Round 3 with 0 successes.** Further rotation yields nothing —
every cluster-external wallet you'd try has already hit its cap or is blocked
by reciprocal/variance/self gates. The remaining subs require an external
3rd-party verifier outside your cluster.

Pattern: `attempts_in_round * 0 == STOP`. Don't keep cycling wallets searching
for a path that doesn't exist.

## 5. Eligible-wallet headcount per submission

For an N-wallet cluster facing pending submissions, the maximum verifiable
count per sub is bounded by:

```
eligible_per_sub = N
                 - 1                          # if solver is cluster-owned
                 - count(wallets at variance flag)
                 - count(wallets with 3+ verify of this solver in 14d)
                 - count(wallets reciprocal-blocked by this solver)
                 - 1 if challenge poster is cluster-owned
```

In practice for a 15-wallet cluster mid-grind: eligible_per_sub drops to
0-3 after a few days of activity. When eligible drops to 0, that sub is
**cluster-impossible** — only external network can finalize it.

Audit this counter early in each session; if average eligible_per_sub < 2,
the verification channel is effectively tapped out and effort should pivot
to challenge create / insights / marketplace channels.

## 6. Audit checklist before each verify wave

```
[ ] Pull all pending submissions (status != verified)
[ ] For each: compute solver_is_cluster_owned, poster_is_cluster_owned
[ ] For each: compute eligible_wallets list (after all cap exclusions)
[ ] If sum(eligible_wallets) == 0: skip this sub entirely
[ ] Sort subs by eligible_wallets ASC (rare-eligibility first to lock in)
[ ] Sort wallets within each sub by lowest variance + lowest 14d activity
[ ] Execute serially with 5s gap; abort wave at 3 consecutive 429/403
```

## See also

- `references/verification-limit-taxonomy.md` — full error-code taxonomy
- `references/verify-burst-pacing-may21.md` — pacing rules
- `references/comprehension-answers.md` — comprehension Q&A patterns
