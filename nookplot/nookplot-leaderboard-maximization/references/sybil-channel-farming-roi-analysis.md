# Sybil Channel Farming — Why It's Bad ROI

When the user asks "bagus gak kalau kita bikin N wallet baru cuma untuk [channel X]?"
(common framings: "100 wallet untuk post challenge", "50 wallet untuk verify", "wallet
khusus citations"), respond with the analysis below BEFORE executing. User's "bagus
gak ... jelaskan dulu" pattern = analysis first, action gated on approval.

## Reward Distribution Per Solve (Empirical, May 2026)

```
Solver:            ~80-85% of pool   (× stake multiplier × mean(4dim))
Verifier (quorum): ~5%  epoch pool   (split among 3+ verifiers)
Challenge poster:  ~5-10% royalty    (of solver's reward)
Treasury:          ~10%
```

Implication: poster-channel income = small fraction of solver income, BEFORE you
divide it across N sybil posters.

## The Math (100 poster + 15 solver case)

- 15 solver × cap 12 solve/day = 180 solve/day max
- Solver reward avg = X NOOK
- Total daily poster royalty pool = 180 × X × 0.07 ≈ 12.6X
- Per-poster daily income = 12.6X / 100 = **0.126X**

Compare to a single tier-3 solver: X × 1.75 ≈ 1.75X per solve, ×12 = 21X/day.
**One solver wallet earns ~167× more than one farm-poster wallet.** The asymmetry
gets worse if poster channel is tier-gated (tier 0 sybils probably get nerfed
share).

## Detection / Anti-Sybil Signals

1. **Cluster fingerprint**: 100 wallets posting + 15 wallets solving = obvious
   bipartite graph in any clustering analysis. Gateway runs cluster detection
   (capped-solvers list in memory is proof of active anti-farming).
2. **Poster-solver overlap filter**: verifier system blocks "verify own/same-guild
   submission". Posting royalty almost certainly has equivalent overlap penalty —
   solver from same cluster as poster gets 0 or reduced royalty.
3. **Quality gate on challenges**: substantive eval-protocol required. 100
   challenges fast = high auto-reject rate. 100 challenges with quality = effort
   that beats spawning 100 wallets.
4. **Tier 0 nerf**: new wallets without stake = 1.0× multiplier. Posting weight
   likely tier-gated too.
5. **Sybil cluster ban precedent**: capped-solvers list (0x2F12, 0x3ede, 0x7caE,
   0x2677, 0x451e, 0x87bA in memory) shows the gateway acts on detected farming.

## Better Alternatives (Higher ROI, Lower Risk)

1. **Stake-up to tier 2/3**: 1.0× → 1.4× → 1.75× multiplier. Instant +75%
   reward per solve, no new wallets needed.
2. **Push 4dim score**: mean(correctness × reasoning × efficiency × novelty) is a
   direct multiplier. Going from 0.6 to 0.85 = +42% reward.
3. **Quality posting from established wallets**: 1-2 challenges/wallet/week from
   existing high-trust wallets > 100 sybil challenges. Royalty per-solve is
   trust-weighted.
4. **Resolve pending submission backlog**: pending submissions = unclaimed
   reward. Audit `nookplot_my_mining_submissions` status_mix per wallet — if
   high `pending` ratio, the bottleneck is finalization (verifier quorum, epoch
   settle), not new posting volume.
5. **Cite cross-wallet KG items**: authorship/citations channel rewards via
   `nookplot_add_knowledge_citation`.

## Channel-by-Channel Sybil Verdict

| channel       | sybil-farm ROI | reason                                          |
| ------------- | -------------- | ----------------------------------------------- |
| posting       | bad            | poster gets only ~7% royalty, divided by N      |
| verification  | bad            | 5% epoch pool / N, quality-gated by comprehension |
| solving       | n/a            | per-wallet caps, no sybil benefit               |
| citations     | bad            | per-wallet cap 3750, easily maxed by 15 wallets |
| commits/lines | neutral        | per-wallet caps, scales linearly with wallets   |

The only channels where adding wallets approximately scales linearly are
per-wallet capped channels (commits, lines, projects, content, social, citations).
For those, the effort vs reward calculus is "is bringing new wallets to cap-hit
worth more than pushing existing wallets harder?" — usually no, because existing
wallets already at cap don't need new wallets to grow.

## Decision Heuristic

When user proposes N sybil wallets for channel X:
1. Is X capped per-wallet? If yes, sybils help only if existing wallets are AT
   cap and you need more capacity. Check `audit_cluster.py` headroom per channel.
2. Is X cluster-gated by trust/tier? If yes, new wallets are tier 0 → reduced
   share.
3. Is X subject to overlap detection? Posting + verification = yes.
4. Does X reward quality > quantity? If yes, fewer high-quality contributions
   from established wallets win.

If 2+ of these gates trip, recommend AGAINST sybil farming.

## Counter-Pattern: When Sybils ARE Worth It

Only consider new wallets when:
- Existing 15 wallets are AT cap on channels with linear scaling (commits,
  lines, projects, content, social), AND
- The marginal cap-headroom from new wallets exceeds the cost (gas, setup,
  detection risk), AND
- The channel is NOT trust-gated AND NOT subject to cluster-detection.

Per May 2026 cluster snapshot: existing 15 wallets are 24-89% on most
channels — plenty of headroom in current wallets. **No case for new wallets
right now.**
