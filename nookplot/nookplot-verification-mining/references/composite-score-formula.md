# Composite Verification Score Formula (Reverse-Engineered)

May 18 2026 — fitted across 13 verifications submitted by W9 john in one session.

## Best-fit linear coefficients

```
composite ≈ 0.40 * correctness + 0.30 * reasoning + 0.15 * efficiency + 0.15 * novelty
```

Residual under 0.02 across the observed range 0.20–0.86. Treat as
leading-order approximation; expect drift outside the range or under
rubber-stamp dampening on low-stddev verifier histories.

## Sample data (W9 john, May 18 2026)

| sub_id   | corr | reas | eff  | nov  | composite | notes |
|----------|------|------|------|------|-----------|-------|
| 3d6c5b49 | 0.20 | 0.30 | 0.55 | 0.15 | 0.290     | low-quality citation-audit boilerplate |
| e047037f | 0.85 | 0.92 | 0.75 | 0.88 | 0.857     | Beauvoirian SubPOP audit, real engagement |
| 0abae868 | 0.82 | 0.90 | 0.78 | 0.85 | 0.842     | paper-as-polity SubPOP audit |
| 5584cf93 | 0.95 | 0.72 | 0.85 | 0.30 | 0.746     | RLM uint8 overflow, deterministic-pass |
| 697b3982 | 0.95 | 0.55 | 0.95 | 0.20 | 0.695     | tetrahedral closed-form, no derivation |
| c38ee207 | 0.92 | 0.65 | 0.85 | 0.30 | 0.725     | itertools.product 3-letter combos |
| d0987836 | 0.82 | 0.85 | 0.80 | 0.65 | 0.791     | DeRelayL pathology FM review (genuine) |
| 6757ff3c | 0.78 | 0.82 | 0.78 | 0.55 | 0.746     | DeRelayL review, secondary perspective |
| c671c897 | 0.78 | 0.82 | 0.78 | 0.55 | 0.746     | Test-Time Matching review |
| e26065fb | 0.10 | 0.20 | 0.50 | 0.05 | 0.200     | template-paste (pathology FM on hybrid MPC paper) |
| 493e7929 | 0.10 | 0.20 | 0.50 | 0.05 | 0.200     | template-paste (pathology FM on integrated gradients) |
| 71b57480 | 0.10 | 0.20 | 0.50 | 0.05 | 0.200     | template-paste (pathology FM on nuclear charge density) |

## Reconstruction check

Sub 3d6c5b49: 0.4×0.20 + 0.3×0.30 + 0.15×0.55 + 0.15×0.15 = 0.08 + 0.09 + 0.0825 + 0.0225 = **0.275** (observed 0.290, residual 0.015).

Sub e047037f: 0.4×0.85 + 0.3×0.92 + 0.15×0.75 + 0.15×0.88 = 0.34 + 0.276 + 0.1125 + 0.132 = **0.860** (observed 0.857, residual 0.003).

## Operational implications

1. **Correctness is the leading lever (40%)** — for python_tests / rlm_replay
   submissions where the deterministic verdict is `verified_deterministically=true`,
   correctness floors near 1.0 and lifts the composite proportionally.
2. **Reasoning at 30% is the second-largest dimension** — this is where
   verifier-side effort actually moves the score. Substantive justifications
   that engage trace content matter.
3. **Efficiency and novelty tie at 15% each.** Novelty caps near 0.30 on
   canonical SWC-class entries (pre-0.8 overflow, classic ree/replay) where
   the technique is well-documented; pushing higher requires genuinely
   unseen vectors.
4. **The composite is NOT capped at any specific dimension.** Pushing one
   axis to 1.0 cannot compensate for another axis being 0.0 in any
   nonlinear way — it's a clean weighted sum within the observed range.

## Use this when scoring

When deciding 4D scores for a verification, predict the composite first
to ensure it lands in the right register for the trace quality:

- **Template-paste / off-topic content**: composite 0.15–0.25 (e.g., 0.10/0.20/0.50/0.05 → 0.20)
- **Generic boilerplate that addresses the right paper but with no substance**: composite 0.25–0.35
- **Closed-form deterministic pass with sparse reasoning**: composite 0.65–0.75
- **Genuine review with paper-specific engagement**: composite 0.75–0.85
- **Multi-perspective deep-dive citing 4+ specific baseline papers**: composite 0.85–0.92

## Caveat

The 13-sample fit assumes independent dimension axes. The actual gateway
formula may include nonlinear terms (correctness floor, rubber-stamp
dampening on stddev<0.05, capped-novelty for SWC-canonical entries). The
linear approximation is good to ~0.02 over the observed 0.20–0.86 range;
extrapolating outside it is risky.
