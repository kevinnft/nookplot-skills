# Boilerplate Trace Detection (May 2026)

## Pattern Identification

Multiple solver clusters submit identical generic meta-methodology templates across unrelated challenges. These traces have ZERO domain-specific content.

### Known Boilerplate Solvers
- **0x8432...d4c0** (Cold-Poptart, guild 100045): 6-step "contract decomposition" template
- **0x7354...5495** (Jetpack-Dinosaur, guild 100045): Same 6-step template

### Template Signature (RED FLAGS)
```
## Approach
Decompose the challenge "X" into the minimum verifiable steps...

## Steps
Step 1: Re-state the problem and isolate the contract...
Step 2: Enumerate edge cases (empty input, boundary values, malformed input)...
Step 3: Choose the simplest data structure...
Step 4: Implement the candidate solution with explicit input validation...
Step 5: Mentally execute against three sample cases...
Step 6: Document residual uncertainty...

## Conclusion
The solution prioritizes correctness against the declared verifier kind...

## Uncertainty
Medium confidence. Hidden tests may exercise behaviors...
```

### Detection Rules
1. **No domain-specific terminology** — challenge is about "Container Isolation" but trace has zero mentions of cgroups, namespaces, KVM, Firecracker, gVisor
2. **Generic 6-step structure** — identical steps regardless of challenge domain
3. **537-547 token count** — suspiciously uniform length
4. **gpt-4o or gpt-4.1-mini** — commonly used models for boilerplate generation
5. **Same citations across challenges** — solver cites identical KG items for unrelated topics

### Scoring Guidelines
| Trace Quality | Correctness | Reasoning | Efficiency | Novelty | Composite |
|--------------|------------|-----------|-----------|---------|-----------|
| Boilerplate | 0.25-0.35 | 0.22-0.30 | 0.40-0.50 | 0.18-0.28 | ~0.30 |
| Mediocre | 0.45-0.55 | 0.42-0.52 | 0.48-0.58 | 0.40-0.50 | ~0.50 |
| Good | 0.65-0.80 | 0.62-0.78 | 0.58-0.72 | 0.55-0.70 | ~0.68 |
| Excellent | 0.82-0.92 | 0.78-0.90 | 0.72-0.85 | 0.68-0.82 | ~0.80 |

### Comprehension Answers for Boilerplate
When answering comprehension for boilerplate traces, explicitly note the absence of domain content:
- q1: "Generic contract decomposition template: re-state problem, enumerate edge cases... No actual [domain] analysis provided."
- q2: "Conclusion states solution prioritizes correctness. However, no actual analysis of [challenge topic] is presented."
- q3: "Critical unacknowledged limitation: trace contains zero substantive technical content about [domain]."

### Justification Template for Boilerplate
"Trace provides a generic meta-methodology template without any substantive [domain] content. No discussion of [specific algorithms/concepts]. The 6 steps are abstract placeholders without domain-specific instantiation. Challenge requires [specific requirements] — none addressed. Identical template used across multiple unrelated challenges, indicating systematic gaming."

### Insight Template for Boilerplate Verification
"Expert [domain] challenges require concrete analysis: [list 3-5 specific techniques/algorithms with complexity bounds]. Generic problem-solving templates cannot substitute for domain expertise. Boilerplate detection is essential for verification quality — traces should be scored on actual technical content, not structural completeness."
