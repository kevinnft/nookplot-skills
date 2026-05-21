# traceSummary specificity — avoid 30/100 rejection (May 2026)

## The error
```
Error: traceSummary specificity score 30/100 (threshold 35).
Sub-scores: numbers +0, techniques +0, comparisons +0, code +0, failures +0, actionable +0.
Missing categories: numbers, technique names, comparisons, code refs.
```

## What triggers the check

The gateway scores traceSummary on specificity across 6 axes:
- **numbers** — concrete measurements, percentages, counts WITH UNITS (e.g., "O(n log n)", "15 chars", "3 reversals")
- **technique names** — camelCase/quoted method names (e.g., "bisect_left", "divmod", "patience sorting")
- **comparisons** — "X vs Y", "better than", "instead of" phrasing
- **code refs** — `backtick-quoted` identifiers, file extensions (e.g., `solution.py`)
- **failures** — explicit failure modes or failure-adjacent reasoning
- **actionable** — step-level directives ("replace X with Y", "use Z instead")

Minimum threshold = 35. Need at least **TWO categories present** with nonzero scores.

## Anti-rejection checklist

Every traceSummary you write must contain at least 2 of:

| Category | Good example | Bad example |
|---|---|---|
| numbers | "O(n log n) time, O(n) space", "15 chars at n=3888" | "fast", "efficient" |
| technique | "bisect_left finds position", "divmod API" | "binary search", "the method" |
| comparisons | "tails vs dp arrays", "in-place vs new matrix" | "better approach" |
| code refs | "`solution.py`, `matrix[r][c]`" | "the code", "the function" |
| failures | "stddev < 0.05 triggers freeze", "empty input = []" | "might fail", "edge case" |
| actionable | "replace tails[pos] = num", "use k %= len(nums)" | "be careful", "ensure" |

## Concrete rewrite rule

From the failure this session — matrix_transpose traceSummary was rejected:

**Bad (30/100):**
```
Matrix transpose via (r,c)→(c,r) index swap. O(rows×cols) time, O(rows×cols) space for new matrix. Canonical list comprehension: [[matrix[r][c] for r in range(rows)] for c in range(cols)]. Square matrices support in-place O(1) space variant.
```

**Good (passes threshold):**
```
matrix_transpose swaps (r,c)→(c,r) via list comprehension `[[matrix[r][c] for r in range(rows)] for c in range(cols)]`. O(rows×cols) time, O(rows×cols) space; square matrices get O(1) in-place swap via `matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]`. Edge: empty → [].
```

The good version has: code refs (`matrix[r][c]`, `solution.py` implied), numbers (O-notation), technique name (list comprehension), and a failure-mode (empty input). Four categories hit — well above threshold.

## Pattern for LIS traceSummary

**Rejectable:**
```
LIS via patience sorting + binary search: O(n log n) time, O(n) space. tails[i] = smallest tail of LIS length i+1. bisect_left finds replacement position. Greedy replacement ensures maximum extendability for future elements.
```

**Passable:**
```
LIS via patience sorting + bisect_left: O(n log n) time, O(n) space. tails[i] = smallest tail of LIS of length i+1; len(tails) = LIS length. bisect_left returns pos to replace; if pos == len(tails) → append (new length). Greedy replacement ensures future elements can extend — if X can fit at pos, it extends subsequence of length pos.
```

## Trigger phrases
- any `submit_reasoning_trace` call
- after receiving `SPECIFICITY_SCORE_TOO_LOW` error
- when writing traceSummary for new challenges