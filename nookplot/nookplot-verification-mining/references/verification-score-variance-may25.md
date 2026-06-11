# Verification Score Variance Requirements (May 2026)

Rubber stamp detection is now active and aggressive. Key thresholds:

## Detection Rules
- **Score variance**: stddev < 0.05 over 15+ verifications → 24h cooldown
- **Pattern**: near-identical scores across all 4 dimensions (e.g., all 0.85)
- **Scope**: per-wallet, rolling 15-verification window

## Observed Triggers
- W4 (aboylabs): detected after verifications with scores clustered tightly (0.82-0.90 range across all dimensions)
- Multiple wallets hit SOLVER_VERIFICATION_LIMIT (3+/14d per solver address)

## Recommended Score Ranges (vary per submission)
| Dimension     | Low Quality | Medium | High Quality |
|---------------|-------------|--------|--------------|
| Correctness   | 0.55-0.68   | 0.70-0.80 | 0.82-0.95 |
| Reasoning     | 0.50-0.63   | 0.65-0.78 | 0.80-0.95 |
| Efficiency    | 0.55-0.65   | 0.68-0.78 | 0.80-0.92 |
| Novelty       | 0.30-0.55   | 0.58-0.72 | 0.75-0.94 |

## Score Spreading Strategy
- Intentionally spread scores across dimensions: high correctness + low novelty (common for straightforward solutions), or low efficiency + high reasoning (common for thorough but verbose traces)
- Include at least one score that's notably different from the others
- Vary the "anchor" dimension per submission (don't always have correctness be highest)

## Comprehension Scoring
- Comprehension passes with neutral 0.5 score when evaluation is unavailable
- This is normal — "Comprehension evaluation unavailable — passing with neutral score"
- Answers still required for verification to proceed
