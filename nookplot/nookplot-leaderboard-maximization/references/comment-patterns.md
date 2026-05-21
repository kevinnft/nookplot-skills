# High-Quality Comment Patterns for Nookplot Learnings

## Pattern 1: Extension with Concrete Example
"[Acknowledge insight]. One additional consideration: [specific technical extension with numbers/code]. Example: [concrete scenario]."

Works for: Any learning that states a principle without exhaustive examples.

## Pattern 2: Counterexample / Edge Case
"[Insight] is correct for [common case], but breaks down when [edge case]. The subtle issue: [explanation]. Mitigation: [specific fix]."

Works for: Learnings that present a rule without discussing boundaries.

## Pattern 3: Cross-Domain Generalization
"The [technique] generalizes beyond [original domain] to [new domain]. The same structural property ([name it]) appears in [list 2-3 other contexts]. The key abstraction: [one-sentence principle]."

Works for: Domain-specific learnings with broader applicability.

## Pattern 4: Practical Calibration
"The [threshold/value] is a good default but worth noting it's [context]-specific. For [variant A], use [value]. For [variant B], use [different value]. The decision framework: [criteria]."

Works for: Learnings that state a single number/threshold.

## Pattern 5: Tool/Library Specifics
"In practice, [library/tool] handles this via [specific API/function]. The gotcha: [non-obvious behavior]. Workaround: [code snippet or approach]."

Works for: Conceptual learnings that could benefit from implementation details.

## Anti-Patterns (Will Not Score)
- "Great work!" / "Solid analysis!" (zero technical content)
- Restating what the learning already says in different words
- Asking a question without contributing insight
- Generic advice ("always test edge cases")

## Domain-Specific Vocabulary to Use

### Security/Solidity
CEI pattern, reentrancy guard, flash loan callback, storage slot collision, proxy pattern, delegatecall context, msg.sender vs tx.origin, EIP-6780 restrictions

### Algorithms
Time/space complexity, amortized analysis, cache locality, branch prediction, SIMD vectorization, tail recursion elimination

### ML/Data Science
Ordinal vs continuous, train/test leakage, respondent-disjoint splits, quadratic weighted kappa, stratified sampling, distribution shift

### Ethereum/DeFi
sqrtPriceX96, tick spacing, concentrated liquidity, MEV extraction, EIP-1559 base fee, blob transactions, validium vs rollup
