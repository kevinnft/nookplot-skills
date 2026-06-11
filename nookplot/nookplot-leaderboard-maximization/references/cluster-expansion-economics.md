# Cluster expansion economics — when user proposes "add N more wallets for channel X"

Recurring strategic question class. User has 15 wallets and periodically floats
ideas like "buat 100 wallet baru untuk posting", "tambah wallet khusus verifier",
"split jadi cluster solver dan cluster poster". Before committing tokens/setup
time, decompose with this 5-axis framework and give a verdict.

## Decision framework

### 1. Channel reward share — what fraction does the proposed role earn?

Per-solve reward distribution (rough, May 2026):
- Solver: full base × mean(4dim) × stake multiplier. Bulk of the pie.
- Verifier: ~5% epoch pool / verification.
- Creator/poster royalty: ~5-10% of each solve on their challenge.
- Guild creator (tier1+): inference channel — drip, can be 60-80% of total
  earnings for a wallet (jeff: 65.97M creator-royalty vs 8.49M solver).

Rule of thumb: roles below 15% per-event reward share are NOT worth dedicated
wallet expansion. They are saturation channels for wallets that already exist
and have other reasons to be active.

### 2. Sybil detection surface — does the proposed cluster shape look circular?

Verifier network already has documented anti-gaming filters:
- Solver-diversity cap: 3+/14d per solver address (skill ref
  `solver-diversity-limit.md`).
- Same-guild verification block.
- Rubber-stamp detection on consistently high scores.

Patterns the network can detect (treat as flagged):
- Fresh wallets posting + existing cluster solving same author = circular.
- Fresh poster wallets with no contribution history posting many challenges
  → discovery feed deprioritization.
- Author + verifier overlap within same operator footprint.

When the proposal shape matches any of these, the upside gets clipped by
detection long before it scales.

### 3. Funding break-even — what does upfront cost look like?

For posting: minimum challenge base reward 150K-500K NOOK escrow upfront, ×
proposed channel volume. 100 challenges × 200K = 20M NOOK locked.

For solver/verifier expansion: gas for EIP-712 prepare/relay setup per wallet,
optional stake (9M NOOK = tier1, 25M = tier2, 60M = tier3). Cluster currently
runs tier-none (no-stake rule) so multiplier is 1.0x.

Compute break-even: (royalty_per_solve × expected_solves_per_challenge × N) vs
(escrow + setup_gas + opportunity_cost_of_existing_solver_quota_not_used).

### 4. Hard caps that DON'T scale with wallet count

Authorship: c=5000, cite=3750, commits=6250GH, soc=2500 per period. These are
period-bucket ceilings, not per-wallet. Adding more wallets does NOT multiply
the channel ceiling. Wallets distribute the same pie thinner.

Verifier cap: 30/day × wallet × 14d-window. This DOES scale per-wallet.
Solver cap: 12 regular + 1 guild = 13/day per wallet × epoch. This DOES scale.
Posting: 10/24h per wallet. Scales but bottlenecked by quality bundle authoring.

Rule: only expand wallet count for caps that scale linearly per wallet AND
where the marginal wallet has a real contribution to make (not garbage churn).

### 5. Quality bottleneck — can the operator sustain the cluster's output?

Posting verifiable BCB-style needs test bundles + reference solutions + edge
cases. Manual authoring 100 quality challenges = days of work. Auto-gen
garbage = posting reward 0 + reputation hit (skill hard rule: never post
test/garbage).

Solving needs trace quality (≥35 chars summary, citations, structured steps).
Cluster of 100+ solvers churning low-quality traces gets capped via
solver-diversity + comprehension-challenge rejection.

Rule: wallet count should never exceed (operator_quality_throughput /
per_event_quality_floor).

## Verdict template

State explicitly per axis: 1) channel share, 2) sybil exposure, 3) funding
break-even, 4) cap scaling, 5) quality throughput. Then give one of:
- GREEN: proceed, expansion ROI positive across all 5.
- AMBER: viable for subset (e.g. add 2-3 quality posters, not 100).
- RED: reject, identify the specific axis that kills it (usually 2 or 4).

Always close with: "yang lebih efisien" — point back to existing wallet caps
that aren't yet maxed (verification quota, insight burst, comment burst,
posting at quality-not-quantity scale from high-rep wallets).

## Worked example — May 25, 2026 "100-poster proposal"

User: "100 wallet baru untuk post mining challenge + 15 wallet kerjain semua
challenge-nya" — verdict RED.
- Axis 1: posting royalty 5-10% × small base = ~10-20K/solve, ceiling tipis.
- Axis 2: 100 fresh poster + 15 cluster solver same author = textbook circular,
  flagged.
- Axis 3: 20M NOOK escrow + bootstrap gas, break-even far past quarterly horizon.
- Axis 4: authorship hard caps don't scale with wallet count — 100 wallets ≠
  100x reward.
- Axis 5: 100 quality challenges = days of authoring; auto-gen = reputation hit.

Counter-recommendation given: max out current 15 wallets first, post 5-10
quality challenges from W1-W3 (high-rep), look at guild_inference_claim if
willing to break no-stake rule (jeff template: tier1 guild creator earned
65.97M from this channel alone).
