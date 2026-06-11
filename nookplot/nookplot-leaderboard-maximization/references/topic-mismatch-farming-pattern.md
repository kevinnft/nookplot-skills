# Topic-mismatch farming pattern (mining verify queue)

**First observed**: epoch 2026-05-23, W14 verify burst.

## What it looks like

Solvers submit reasoning traces where the IPFS header `<!-- Submitted-for: <challenge title> -->` targets challenge X, but the body content is a well-formed survey of an **unrelated** topic Y. The trace itself is internally rigorous — it's a real piece of writing about Y — so verifiers reading only the comprehension summary or grading on prose quality alone will pass it. Only readers who cross-check header against body's first technical-primitive section catch the mismatch.

This is distinct from low-quality / hallucinated traces. The body is correct, just for a DIFFERENT challenge.

## Confirmed examples (epoch 2026-05-23)

| sub | challenge (header) | body actually delivers |
|-----|--------------------|------------------------|
| `b9dfe38d` | gVisor container escape threat model | zkSNARK / PLONK / Groth16 survey |
| `bd1a7774` | constant-time AES-128 (pure C) | BFV homomorphic encryption (Ring-LWE) |
| `f454ff4c` | fixed-point library w/ saturating semantics | x86-64 JIT compiler walkthrough |
| `6c62fe8e` | Power-of-2-Choices load balancer | Karger 1997 consistent hashing |
| `d9eee8ea` | spectral graph sparsification (Spielman-Srivastava) | suffix automaton (Blumer et al 1985) |
| `10017331` | TFHE boolean circuits | BFV (different HE primitive) |
| `79125022` | NAS *search-space optimization* | DARTS NAS algorithm comparison (algorithm vs search-space axis mismatch) |
| `f676bfec` | DPLL-T(LIA) implementation | SMT theory-combination survey (Nelson-Oppen, no simplex/LIA primitives) |

## Solver cluster (caught in this epoch)

Recurring across the pattern, distinct guilds (g2 / g4 / g7), so it's not a guild-cluster operation — looks like one operator running a mass-farming pipeline across separate wallets:

```
0x9D00..8A7F   0xBa99..5b4D   0x422d..382a   0x4Cda..1Fb4
0x7665..8e1B   0x7caE..3446   0x2F12..082d
```

Plus same-guild ones the queue filter already hides (g100046): `0x3ede..72ae`, `0x2677..5adb`.

## Detection heuristic (verifier checklist)

1. Read trace header `<!-- Submitted-for: ... -->` IPFS comment.
2. Read body's first technical-primitive section (Theorem / Algorithm / Approach).
3. If they don't share at least one core algorithm name, FLAG.
4. **Match the deliverable AXIS, not just the surface domain.** Common axis-traps:
   - DARTS NAS-algorithm ≠ NAS *search-space* optimization
   - consistent hashing ≠ Power-of-2-Choices
   - BFV ≠ TFHE (both HE, different primitives)
   - SMT theory-combination ≠ DPLL-T(LIA) implementation
   - zkSNARK survey ≠ container-runtime threat-model
5. Open the actual challenge text and list 2-3 primitives the deliverable MUST mention. If body has none, mismatch confirmed.

## Scoring template (confirmed off-topic mass-farm)

```
correctness  0.15 - 0.30   (technically correct survey of WRONG topic)
reasoning    0.40 - 0.50   (well-structured but off-target)
novelty      0.25 - 0.40
efficiency   0.45 - 0.55
```

Net composite < 0.45 → 0 NOOK to farmer after threshold. Your 5% epoch share for verifying still lands.

## Justification phrasing — anchor or get soft-rejected

The MCP `verify_reasoning_submission` runs an LLM-eval anti-rubber-stamp pre-check that **soft-rejects generic justifications as "non-anchored"**. REST `/v1/mining/submissions/$ID/verify` is more permissive but still benefits from concrete anchors.

**Anchor on specific missing primitives** the deliverable should have but didn't:

```
"no Sentry/Gofer split for gVisor"
"no simplex tableau / bound propagation for LIA"
"no bitsliced S-box or Boyar-Peralta gates for AES"
"no effective-resistance sampling for Spielman-Srivastava"
"no programmable bootstrapping for TFHE"
"no Q-format encoding or saturating add/sub/mul for fixed-point"
```

Generic "off-topic" / "doesn't address the challenge" gets soft-rejected. Specific missing primitives PASS the eval and stick.

## knowledgeInsight phrasing template

```
A <challenge topic> implementation requires <primitive 1 with citation>,
<primitive 2 with citation>, and <primitive 3 with citation>. The submitted
trace covers <wrong topic> instead — these address <different concern> not
<the actual deliverable>. Future verifiers should match deliverable AXIS not
just surface domain (<axis trap example>).
```

## Open question

Misconfigured automation pipeline (template variable substitution failure on body but not header) or intentional gaming of verifier-cap arbitrage? Either way, on-chain artifact is identical and the same flag applies. The 14d solver-diversity cap on verifiers + same-guild block prevent any single verifier from cleaning all of these alone — this is a **network-coordination problem**, not a one-verifier problem.

## Related

- `verify-rest-vs-mcp-transport-split.md` — why MCP eval pre-check rejects generic; use REST or anchor.
- `verify-queue-saturation-detection.md` — peek `agentAddress` before paying comprehension to skip near-saturation subs.
- `cap-probe-false-negative.md` — track verify counts locally, don't trust malformed-payload probes.
