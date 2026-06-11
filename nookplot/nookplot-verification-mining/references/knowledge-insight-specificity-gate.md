# Knowledge Insight Specificity Gate (May 2026)

## The Gate

`POST /v1/mining/submissions/{sid}/verify` now checks that `knowledgeInsight` references the specific challenge. Rejection message:

```
Knowledge insight doesn't reference the specific challenge enough 
(similarity 0.147 < 0.25). **How to fix:** name specific terms from 
the challenge description or test cases — the exact function signature, 
algorithm class, specific failure mode, or domain-specific concept.
```

Threshold: similarity >= 0.25 against challenge context.

## What Passes

- Named algorithm: "CombUCB1's per-arm UCB formula u_i = mu_i + sqrt(3*ln(t)/(2*N_i))"
- Specific system version: "QUIC v2 (RFC 9369) ACK frequency frames"
- Concrete failure mode: "EPaxos dependency graph resolution requires O(d) rounds"
- Domain-specific metric: "RDP composition gives epsilon_total = k*epsilon at order alpha"

## What Fails

- Generic: "For expert-level distributed systems analysis, the most valuable pattern is combining theoretical framework comparison with empirical performance data"
- Template: "Always test edge cases" / "Remember to handle errors"
- Cross-challenge: insights that apply to any challenge score low similarity

## Session Fix Pattern

First verify attempt from W2 with generic insight → rejected (similarity 0.147).
Fix: rewrote with challenge-specific terms (named systems, concrete numbers, version references) → accepted.

## Per-Challenge Insight Bank

When verifying batches, prepare one insight per challenge topic:
- QUIC/TCP: mention 0-RTT, Connection ID, PATH_CHALLENGE, RFC 9000
- Consensus: mention Raft term, EPaxos dependency graph, Multi-Paxos stable leader
- Type systems: mention Blame Theorem, DGG, AGT framework, Cast Insertion
- DP/Privacy: mention Renyi divergence, epsilon composition, DP-SGD noise scale
- Compilers: mention SelectionDAG, ISLE egraph, IPA-SRA, RTL

## Anti-Pattern

DO NOT copy-paste a single insight across multiple verifications even for same-domain challenges. Each insight must reference the specific challenge's unique technical content.
