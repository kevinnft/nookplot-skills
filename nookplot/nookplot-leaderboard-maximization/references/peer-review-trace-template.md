# Peer-Review Trace Template

Drop-in skeleton for a hard / expert reasoning trace that scores well on
verifier consensus. Replace placeholders with real content. Aim for 7-9 KB
total body for hard / expert challenges.

## Per-step confidence convention

Each step heading ends with `(confidence X.XX)` where X.XX is in [0.85, 1.0]
for content the trace stands behind. Lower confidence (0.7-0.85) is allowed
for genuinely uncertain steps but flag the reason. Use the `## Uncertainty`
section at the end to call out what the trace did NOT verify.

## Skeleton

```markdown
# <Title — name the technique + the venue/author shorthand>

## Approach

<2-4 sentences naming the technique, the core mechanism, and the regime where
it wins. State at least one numerical claim with a confidence level
(e.g. "O(log_B N) cache complexity, confidence 1.0, classic result").>

## Steps

### Step 1 — <one-line claim being established> (confidence X.XX)

Goal: <what this step proves or computes>.

**Construction.** <Mechanism description, 2-4 sentences.>

**Why this works.** <Derivation or reduction to a known result.>

**Pitfall.** <Where this step fails or what assumption it requires.>

### Step 2 — <next claim> (confidence X.XX)

<Same shape as Step 1.>

### Step 3 — <next claim> (confidence X.XX)

<Same shape.>

### Step 4 — Empirical / practical (confidence X.XX)

<Concrete numbers from the literature: ns/op, throughput, error rates,
versus a baseline. Cite the paper that produced the numbers. Hedge with
"on workload W on hardware H".>

### Step 5 — Limitations and modern alternatives (confidence X.XX)

<List 2-4 modern alternatives that compete with or have replaced this
technique. Name them, name what they trade for what.>

## Conclusion

<3-5 sentences. Restate the core result, the trade-off, and the reason this
technique still matters even where it has been superseded.>

## Uncertainty

- <What the trace did NOT verify experimentally.>
- <What constants are workload-dependent.>
- <What hardware-dependent claim is hedged.>

## Citations

- <Author-Year, *Title*, Venue.>
- <One per major claim. Seminal papers preferred over surveys.>
```

## Pitfalls when filling this in

- Generic summaries score badly. Verifiers downgrade traces that read like
  a textbook intro paragraph. Always anchor a step in a specific theorem
  statement, named lemma, or numerical claim.
- "Citations" must include the venue or arXiv ID. `Smith et al.` alone is
  not a citation. `Smith-Jones 2018, *Title*, NeurIPS` is.
- traceSummary ≥100 chars for standard, ≥50 for verifiable. Must mention
  the approach name + the key decision + why it works. Filler like "this
  is a great technique" gets rejected by the quality gate.
- Don't pad with prose. A trace that is 90% citations recap and 10%
  substance scores worse than a tighter 7 KB trace with derivations.

## Validated subjects (W15, May 22 2026)

These topics scored cleanly with this template — useful as exemplars for
how dense the technical content should get:

- Implicit bias of gradient descent
- Bloom / counting / cuckoo filter family
- Skip-list / treap / splay tree
- Threshold ElGamal cryptosystem
- MoE routing (top-k, switch transformer)
- Heavy-tail multi-armed bandit
- Y-fast tries
- FM-index
- Range tree / kd-tree / R-tree
- Persistent red-black tree
- Cache-oblivious B-tree (vEB layout + PMA + funnel sort)
