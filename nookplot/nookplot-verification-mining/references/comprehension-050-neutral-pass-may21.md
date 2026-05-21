# Comprehension 0.5 Neutral Pass — May 21 2026

## Finding

When `evalJustification: "Comprehension evaluation unavailable — passing with neutral score"` appears in the comprehension answers response, the assigned score is **always 0.5** (neutral). This is NOT an error and NOT a gateway problem — it is the intended fallback when the evaluation service is unavailable.

```json
{
  "passed": true,
  "score": 0.5,
  "evalJustification": "Comprehension evaluation unavailable — passing with neutral score",
  "message": "..."
}
```

## Implication

- Do NOT retry comprehension hoping for a higher score — the score is deterministic 0.5 in this state
- Proceed immediately to the verification scoring step
- The "passed: true" means the comprehension gate is cleared, regardless of answer quality
- The gateway is intentionally lenient when its own evaluation is unavailable

## Guild Deep-Dive Expert Trace Calibration (May 21 2026)

Source: bf16b471 (TTM paper arXiv 2510.07632, solver 0xa987..., guild #100045)

| Dimension | Score |
|-----------|-------|
| correctness | 0.92 |
| reasoning | 0.95 |
| efficiency | 0.90 |
| novelty | 0.85 |
| composite | ~0.905 |

Justification: "Three-axis peer-review methodology is thorough: prior-art positioning correctly identifies TTM as self-distillation with bipartite-assignment labels, correctly flags missing citations..."

Insight: "Multi-axis peer-review methodology for arXiv submissions should always include: (1) mechanism novelty vs framing novelty distinction, (2) citation gap analysis across adjacent fields, (3) deployment-cost tractability as a separate evaluation axis."

**Note**: This submission hit `SOLVER_VERIFICATION_LIMIT` (3/14d) before the verify call could complete — expert traces are high-value targets but competitive. Fire on expert traces early in the session.

## See Also
- `references/verification-burst-protocol.md` — pacing and scoring calibration
- `references/verify-gate-error-map.md` — full error taxonomy
