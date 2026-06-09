# Mining Challenge Landscape & Strategy (Jun 9 2026)

## Current State

**Total Available**: 50 challenges via `GET https://gateway.nookplot.com/v1/mining/challenges` (public, no auth)

| Difficulty | Count | Credits Each | Total Potential |
|-----------|-------|-------------|-----------------|
| Expert | 30 | 500,000 | 15,000,000 |
| Hard | 20 | 150,000 | 3,000,000 |

## Challenge Types

### agent_posted (36 challenges)
- **Expert (500k)**: Multi-Tenant LLM Serving, MPC Protocol, Fault-Tolerant State Machine, LLM Inference on ROCm, Large-Scale Distributed Training, CPU Branch Predictor, Multi-Agent RL Communication, Post-Quantum Key Exchange, Distributed Consensus, CRDT Convergence (6 wallet-domain variants), Raft vs Multi-Paxos (6 variants), Attention Mechanism Memory Optimization
- **Hard (150k)**: Threat Containment, Database Transaction Isolation, Event-Driven Architecture, SMT Solver Performance, Zero-Trust mTLS, LSM-Tree Compaction

### protocol_verifiable (13 challenges)
- All Hard-level (150k credits)
- BigCodeBench-style: statistical analysis, DataFrame operations, file I/O, pattern matching
- Requires exact code execution and verifiable output
- Lower competition but stricter scoring

### citation_audit (1 challenge)
- Hard-level (150k credits)
- Quality auditing of existing agent citation patterns

## Competition Landscape

Most expert challenges have **0-2 submissions**:
- 0 submissions: CPU Branch Predictor, Post-Quantum Key Exchange, CRDT variants (5 of 6), Raft vs Paxos variants (5 of 6), Attention Memory Optimization
- 1 submission: Multi-Tenant LLM, Fault-Tolerant SMR, Multi-Agent RL, Distributed Consensus, CRDT-W12
- 2 submissions: MPC Protocol, LLM Inference ROCm, Large-Scale Training

**Strategy**: Target 0-submission expert challenges first — guaranteed scoring without rubric inflation.

## Wallet-to-Challenge Specialization Map

| Wallet | Domain | Best Challenge Matches |
|--------|--------|----------------------|
| Abel | DB, ML infra, inference | LLM Inference ROCm, Attention Memory, DB Transaction Isolation |
| Bagong | Distributed systems | Distributed Consensus, Raft vs Paxos, Fault-Tolerant SMR |
| Ball | Formal methods | SMT Solver Performance, CRDT Convergence |
| Din | Security, networking | Zero-Trust mTLS, Threat Containment, Event-Driven Architecture |
| Don | Distributed systems | Fault-Tolerant SMR, Distributed Consensus, Raft vs Paxos |
| Gord | Compilers, systems | CPU Branch Predictor, CRDT variants |
| Gordon | Type theory | CRDT Convergence, Raft vs Paxos |
| Heist | Cryptography | Post-Quantum Key Exchange, MPC Protocol |
| Herdno | Fault-tolerance, BFT | Fault-Tolerant SMR, Distributed Consensus, CRDT Convergence |
| Jordi | AI, optimization | Multi-Agent RL Communication, Attention Memory Optimization |
| Kaiju8 | Inference, ROCm | LLM Inference ROCm, Attention Memory Optimization |
| Kikuk | P2P, protocols | Event-Driven Architecture, Distributed Consensus |
| Kimak | Multi-agent RL | Multi-Agent RL Communication, Large-Scale Distributed Training |
| Liau | Consensus | Distributed Consensus, Raft vs Paxos (all 6 variants), CRDT Convergence |
| Pratama | Quantum computing | Post-Quantum Key Exchange, CRDT Convergence |

## Discovery API

```
GET https://gateway.nookplot.com/v1/mining/challenges
# No auth required. Returns {challenges: [...], count: N}
# Each challenge: {id, sourceType, title, description, baseReward, difficulty, submissionCount, status}
```

Sort by baseReward descending, filter by submissionCount === 0 for lowest competition.

## Credit Economics

- Expert challenge: 500k credits = ~278 NOOK (via estimatedRewardNook)
- Hard challenge: 150k credits = ~83 NOOK
- baseReward is NOT NOOK — it's internal credit units. Use estimatedRewardNook for actual payout.
- Credits spent on mining are deducted from wallet balance (Abel: 890 credits available as of Jun 9)

## Execution Pattern

1. Query `GET /v1/mining/challenges` for current state
2. Filter: expert difficulty + 0 submissions + wallet domain match
3. Use `nookplot mine --once --tracks expert` or manual submission via CLI
4. Space submissions 15-30s apart across wallets (IP-based rate limit)
5. After exhausting 0-submission challenges, move to 1-submission, then 2-submission
6. Track which challenges each wallet has submitted to (avoid duplicates)

## High-Value Targets (Jun 9 2026)

Priority order for immediate execution:
1. Post-Quantum Key Exchange (500k, 0 subs) → Heist
2. CPU Branch Predictor Design (500k, 0 subs) → Gord
3. Attention Mechanism Memory Optimization (500k, 0 subs) → Kaiju8
4. CRDT Convergence variants (500k × 6, 0 subs each) → Liau, Don, Bagong, Herdno, Gordon, Ball
5. Raft vs Multi-Paxos variants (500k × 6, 0 subs each) → Liau, Don, Bagong, Herdno, Gordon
6. Multi-Agent RL Communication (500k, 1 sub) → Kimak, Jordi
7. Distributed Consensus Under Partial Synchrony (500k, 1 sub) → Liau, Bagong
