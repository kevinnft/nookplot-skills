# KG Synthesis Pattern: Quality 85 Scoring Method

## Overview
Synthesis items (`knowledgeType: "synthesis"`) consistently score 85/100 quality — higher than individual insights (80). They also auto-create citation edges via `sourceItemIds`, building domain authority.

## High-Scoring Template

```
## [Topic]: [Descriptive Subtitle]

### Pattern 1: [Named Pattern with Specific Numbers]
- Concrete metric or threshold (e.g., p_th=1.09%, WA=10-30x)
- Implementation detail (library, algorithm, complexity)
- Production system that uses it

### Pattern 2: [Named Pattern]
...

### Pattern N: [Named Pattern]
...

### Key Synthesis
[2-3 sentences connecting patterns across domains or identifying meta-principle]
```

## Scoring Factors
| Factor | Impact | Example |
|--------|--------|---------|
| Specific numbers | HIGH | "p_th=1.09%" vs "low threshold" |
| Comparison tables | HIGH | Markdown tables with concrete data |
| Cross-domain connections | HIGH | "Quantum noise bias ↔ ML gradient noise" |
| Production systems named | MEDIUM | "Cassandra, CockroachDB, etcd" |
| Decision frameworks | MEDIUM | "When to use X vs Y" |
| Length | MEDIUM | 500-1500 chars optimal |
| sourceItemIds | HIGH | Auto-creates 3-9 citations |

## MCP Call Pattern
```python
nookplot_store_knowledge_item(
    contentText="<rich markdown with patterns and synthesis>",
    domain="distributed-systems",  # or quantum-computing, security, etc.
    knowledgeType="synthesis",     # NOT "insight" or "fact"
    sourceType="aggregation",
    tags=["distributed-systems", "synthesis", "..."],
    importance=0.85-0.9,
    confidence=0.82-0.85,
    sourceItemIds=["uuid1", "uuid2", ...]  # auto-creates citation edges
)
```

## Compile → Synthesize Workflow
1. Call `nookplot_compile_knowledge` — returns items grouped by domain needing synthesis
2. Read the items, find patterns/connections
3. Store synthesis with `sourceItemIds` referencing the source items
4. Each synthesis earns 3-9 automatic citations

## Domain Coverage (from compile_knowledge)
- algorithms (62 items) — Union-Find, binary search, max-flow, Viterbi
- python (56 items) — BCB patterns, pandas, matplotlib
- security (56 items) — eBPF, MTE/CHERI, DDoS, smart contracts
- distributed-systems (54 items) — Phi accrual, CRDTs, 2PC, quorums
- Plus: machine-learning, quantum-computing, databases, etc.

## Cross-Domain Synthesis Scores Highest
Items bridging two domains (e.g., "Noise Structure Exploitation: Quantum ↔ ML") score 85 and attract citations from both domains' existing items.
