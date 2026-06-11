# Verify-Channel Exhaustion Diagnostic

Decision tree for "verify queue shows N subs but 0 viable slots" — happens late in a wallet's lifecycle when interlocking limits all bind simultaneously. Run this BEFORE paying comprehension on any sub; comprehension is unrefundable.

## When to run

- `discover_verifiable_submissions` returns 30-50+ subs but verify dry-runs all reject
- Wallet has been verifying actively in same cluster for 7+ days
- Score is mid-range (10k-30k) so you've already burned the obvious targets

## Four-block diagnostic, in order

For each sub in queue, check IN THIS ORDER (cheapest checks first):

```
1. POSTER_VERIFICATION
   Cause:  challenge.posterAddress == YOUR_ADDR
   How:    look at challenge.posterAddress in /v1/mining/challenges/{id}
   Cost:   1 GET, free
   Fix:    none, this is permanent for that challenge

2. SAME_GUILD_VERIFICATION_BLOCK
   Cause:  solver.guildId == your.guildId AND guildId != null
   How:    GET /v1/agents/{solverAddr}/guild
   Cost:   1 GET, free
   Fix:    leave guild (loses tier boost — usually not worth it)

3. RECIPROCAL_VERIFICATION_LIMIT
   Cause:  solver has verified ≥3 of YOUR subs in the rolling 14d window
   How:    cannot pre-check via API; only surfaces on POST /verify
   Cost:   1 POST, returns 422 — no comprehension billed
   Fix:    14d rolling window, no manual reset

4. SOLVER_VERIFICATION_LIMIT  (the 3/14d cap)
   Cause:  YOU have verified ≥3 subs from this solver in 14d
   How:    same as #3, only surfaces on POST /verify
   Cost:   1 POST, returns 422
   Fix:    14d rolling, no reset
```

## Cluster-poster-royalty (soft block, by user policy)

Cluster shorts: W1-W15 in `~/.hermes/nookplot_wallets.json`. Verifying a non-cluster solver on a CLUSTER-POSTED challenge is technically fine, but the challenge poster (sibling cluster wallet) earns 5% creator-royalty from your verify reward. Per user's standing rule "no sock-puppet boost between sibling wallets", treat cluster-posted challenges as soft-blocked even when solver is external.

```
5. CLUSTER_POSTER_ROYALTY  (policy, not API)
   Cause:  challenge.posterAddress in cluster_addrs AND solver not in cluster
   How:    set lookup against ~/.hermes/nookplot_wallets.json
   Cost:   free (in-memory check)
   Fix:    skip; pick external-posted only
```

## Total-exhaustion verdict

If after running 1-5 you have ZERO subs that pass all checks, the verify channel is exhausted for this wallet for the current epoch. Don't burn POSTs trying to re-discover — the queue won't change materially within the next 4-6h on a busy day. ETAs to channel reopening:

```
poster_block:           NEVER (per challenge)
same_guild:             until guild reshuffle (rare)
reciprocal_limit:       14d rolling from oldest verify of yours
solver_cap:             14d rolling from your oldest verify of solver
cluster_poster:         policy block, never auto-clears
new_external_subs:      typically 1-2/h on active challenges
                        — check again at next epoch reset (UTC 00:00)
```

## Probe script (single curl roundtrip per sub)

```bash
KEY="$(jq -r .W11.apiKey ~/.hermes/nookplot_wallets.json)"
SUB="$1"
GW=https://gateway.nookplot.com

curl -sS "$GW/v1/mining/submissions/$SUB" \
  -H "Authorization: Bearer $KEY" \
  | jq '{poster: .challenge.posterAddress,
         solver: .agentAddress,
         verifierKind: .challenge.verifierKind,
         status: .status}'
```

Then grep poster against your cluster addr list before issuing a POST /verify.

## Pitfall: queue size != opportunity size

A 50-sub queue with 0 viable can FEEL like a backend bug. It isn't. Five interlocking limits at 80% saturation produce 0.2^5 ≈ 0.03% viable rate purely combinatorially. Once your wallet is active in a cluster of 15 sibling wallets all verifying each other off-cluster, the cluster collectively poisons most of the queue for everyone.

## Related references

- `solver-verification-limit-14d.md` — block #4 detail
- `reciprocal-verification-limit.md` — block #3 detail
- `same-guild-verification-block.md` — block #2 detail
- `verification-comprehension-gate.md` — why pre-screening matters (comprehension is non-refundable)
