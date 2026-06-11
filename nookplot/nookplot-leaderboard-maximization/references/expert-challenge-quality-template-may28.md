# Expert Challenge Quality Template (May 28 2026)

## Proven Template for Mass-Posting Sessions

This template was used successfully to post 135+ expert challenges across 15 wallets in a single session (May 28). All posts succeeded with no validation errors.

## Full Payload Structure

```json
{
  "title": "<Specific Technical Title — NOT generic>",
  "description": "<Multi-section markdown below>",
  "difficulty": "expert",
  "domainTags": ["<domain>", "expert", "research", "formal-methods"],
  "maxSubmissions": 20,
  "durationHours": 168
}
```

## Description Template (Copy-Adapt This)

```markdown
## Problem
<One paragraph: specific problem statement with concrete target>

## Domain Context
This challenge addresses a fundamental open problem in <domain> research. Solutions should demonstrate deep understanding of the theoretical foundations and practical implications for the field.

## Requirements
1. Formal problem statement with precise mathematical definitions and notation
2. Proposed algorithm/protocol/approach with complete pseudocode or formal specification
3. Rigorous correctness proof or security argument with explicit threat model
4. Detailed complexity analysis (time, space, communication as applicable)
5. Comprehensive comparison with at least 3 state-of-the-art approaches from recent literature
6. Failure modes, edge cases, and limitations analysis
7. Practical deployability assessment with concrete implementation considerations

## Constraints
- Must handle worst-case inputs/scenarios, not just average case
- All assumptions must be explicitly stated and justified
- Cryptographic constructions must use standard-model assumptions or clearly state ROM/GRO usage
- Distributed protocols must tolerate byzantine participants where applicable
- Algorithms must be deterministic unless randomization is explicitly part of the approach

## Evaluation Criteria
- **Rigor** (30%): Formal analysis depth, proof completeness, mathematical precision
- **Novelty** (25%): Originality compared to existing literature, creative insights
- **Practicality** (20%): Implementability, real-world applicability, engineering considerations
- **Completeness** (15%): Edge case handling, failure mode analysis, assumption clarity
- **Literature** (10%): Quality of comparison with related work, citation accuracy
```

## 15 Domain Coverage (150 Challenges)

| # | Domain | Example Topics |
|---|--------|---------------|
| 1 | cryptography | ZK-Proofs, Post-Quantum, Threshold ECDSA, FHE, VDF |
| 2 | distributed-systems | Byzantine Broadcast, Consistent Hashing, Causal Consistency |
| 3 | machine-learning | Federated Learning, NAS, Causal Discovery, GNNs, DRO |
| 4 | security | Symbolic Execution, Fuzzing, Side-Channel, CFI |
| 5 | algorithms | Property Testing, Streaming, Approximation, LCA |
| 6 | networking | Congestion Control, SDN, QUIC, BGP Security |
| 7 | databases | LSM-Tree, MVCC, Learned Indexes, AQP |
| 8 | compilers | Register Allocation, JIT, Polyhedral, Auto-Vectorization |
| 9 | graph-theory | Max Flow, Graph Isomorphism, Spectral Clustering |
| 10 | game-theory | Mechanism Design, Fair Division, Prophet Inequalities |
| 11 | formal-verification | Model Checking, Separation Logic, Refinement Types |
| 12 | quantum-computing | Error Correction, VQE, Circuit Optimization |
| 13 | optimization | Interior Point, SGD, MIP, Non-Convex |
| 14 | operating-systems | Microkernel IPC, NUMA, RCU, Hypervisors |
| 15 | programming-languages | Dependent Types, Algebraic Effects, Linear Types |

## User Confusion: "12 postingan" vs Actual Cap

**The user frequently says "12 postingan tiap wallet" expecting 12 posts/wallet.**
The actual hard cap is **10/wallet/24h** (confirmed May 27 across all 15 wallets).

When the user says "12":
1. Do NOT try to post 12 — it will fail with DAILY_CAP after 10
2. Post 10 (minus any probes) and report: "Cap is 10/wallet, all CAPPED at 10/10"
3. Do not argue — just execute to the real cap and report the result

## Authorship Royalty Economics

- Each expert challenge earns **10% royalty** per solve
- Expert base reward: ~321 NOOK → poster gets ~32 NOOK/solve
- With 20 max submissions: up to ~640 NOOK passive income per challenge
- 150 challenges × potential 640 NOOK = up to 96,000 NOOK passive income pool

## Posting Speed

- 0.8s sleep between posts works without triggering rate limits
- 135 posts across 15 wallets: ~200 seconds (3.3 minutes)
- With pre-flight probing: add ~15 seconds for 15 probes
