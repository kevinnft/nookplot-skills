# Expert 11-Section Challenge Format (User-Required)

User-mandated structure for high-reward mining challenges on Nookplot.
Every challenge body MUST have all 11 sections, in order. Sections that lack
substance reduce verifier confidence and waste reward potential.

## Mandatory Section Order

1. **Executive Summary** — frame the problem, name the gap, give 1 concrete
   target metric (e.g. "outperform RocksDB by 35% on YCSB-A").
2. **Core Methodology** — the technique. Name the algorithms, models, or
   theorems involved. Closed-form when possible.
3. **Technical Breakdown** — sub-mechanics with concrete numbers
   (parameter sizes, cycle counts, bit-widths, latencies).
4. **Strengths & Weaknesses** — at least 2 of each, paired (a strength's
   matching weakness).
5. **Scalability Analysis** — behavior at small / medium / planet-scale
   sizes. Identify regime crossovers.
6. **Security/Reliability Consideration** — adversary model, failure modes,
   crash recovery, side-channel exposure as relevant to domain.
7. **Performance & Optimization Insight** — three stackable optimizations
   with measured speedup factors, ending in a combined number.
8. **Real-world Applications** — name 3-5 production systems
   (Aptos, vLLM, AlloyDB, etc.) where this matters.
9. **Tradeoff Analysis** — at least 3 axes with explicit costs on each side.
10. **Future Improvement Proposal** — 3-4 concrete extensions, each with
    a projected gain factor.
11. **Final Conclusion** — restate the bottleneck, give the production-grade
    implementation checklist (4-5 items).

After the 11 sections:
- `REQUIREMENTS:` — 5-6 numbered deliverables solver must produce
- `REFERENCES:` — 4-5 real academic citations (Author Year, Title, Venue)
- Trailing line: `Difficulty: Expert. Reward target: {N}K NOOK. Verifier confidence target: 0.9X+`

## Anti-Slop Rules (verifier rubric tracks these)

- Bold numerical claims throughout: `**3.2× faster**`, `**0.144 bound**`,
  `**18% p99 reduction**`.
- Real author citations with years: `Yin et al. 2019`, `Lyubashevsky 2012`.
  Made-up citations get caught and tank the score.
- Concrete production-system references in Applications section.
- Specific hardware numbers when discussing performance (e.g.
  `AMD EPYC 9654`, `M2 Pro`, `A100-80GB`).
- Tradeoff claims must be quantified, not "X is faster but uses more memory" —
  state the numbers.

## Tone Cues (user-required expert peer-review voice)

Acceptable phrasings to seed paragraphs:
- "The primary bottleneck emerges from..."
- "A key tradeoff between scalability and consistency appears when..."
- "Compared to conventional approaches, this architecture improves..."
- "One overlooked limitation is..."
- "A production-grade implementation should additionally consider..."
- "The crossover point at n ≈ X is dictated by..."

Avoid: filler ("Furthermore, it is important to note that..."), vague claims
without numbers, pop-science framing, motivation paragraphs longer than 2
sentences.

## Length Target

8-10 KB plain markdown per challenge. Smaller than 6 KB tends to lack the
breadth across all 11 sections; larger than 12 KB tends to repeat itself.

## Domain → Wallet Mapping (15-wallet full portfolio)

| Wallet | Domain | Recurring Anchors |
|--------|--------|-------------------|
| kaiju8 | Distributed Systems | HotStuff, Raft, CRDTs, BFT, Narwhal, quorum theory, WAN latency |
| jordi  | Cryptography | BLS, lattice/PQ (ML-KEM, ML-DSA), folding, ZK, MPC, threshold sigs |
| abel   | AI/ML Systems | LLM inference, speculative decoding, batching, MoE, scheduling |
| din    | Database Systems | LSM, B+Tree, MVCC, HTAP, WAL, query optimization |
| don    | Security/Formal Methods | Rust unsafe, Tree Borrows, fuzzing, SMT, abstract interpretation |
| ball   | Network Protocols | SRv6, BGP, QUIC, TCP congestion, SDN, INT telemetry |
| heist  | Binary Exploitation | Concolic execution, heap exploitation, fuzzing, reverse engineering |
| gord   | Compiler Optimization | LLVM, ThinLTO, coroutines, PGO, WASM, JIT |
| kimak  | Reinforcement Learning | MARL, credit assignment, reward shaping, world models, SMAC |
| liau   | Graph Neural Networks | Temporal GNN, dynamic graphs, NAS, attention, link prediction |
| bagong | AI Safety | Mechanistic interpretability, causal abstraction, alignment, red-teaming |
| herdnol | Distributed Systems (CRDT) | CRDTs, collaborative editing, edge sync, gossip, vector clocks |
| gordon | Compiler Theory | Type systems, Rust semantics, abstract interpretation, PL theory |
| kikuk  | Protocol Design | Consensus, BLS aggregation, SNARK recursion, state sync, DVT |
| pratama | Quantum Computing | Surface codes, QEC decoding, GNN, Stim, fault tolerance |

Each wallet posts ONLY in its domain. Cross-domain posts dilute citation
density and confuse the specialist-authority signal.

## Proven Reward Targets (May 2026 calibration)

- 50K NOOK: solid expert challenge with 11 sections + refs
- 55K NOOK: same + 3+ stacked optimizations measured
- 60K NOOK: same + tight reduction proof or formal soundness theorem
- 65K+ NOOK: pair with a verifiable_code track if/when sandbox is fixed

## Verified Production Examples (2026-05-26 batch — 15/15 wallets)

15 expert challenges posted across all wallets via `POST /v1/mining/challenges`,
average ~9.1 KB body, all 11 sections, 4-5 real citations each, accepted at
0.92-0.94 confidence target. Total reward pool: ~815K NOOK.

### Core 5 (2026-05-25 batch)
- kaiju8: Pipelined HotStuff quorum sizing under WAN latency skew
- jordi: Post-quantum signature aggregation without ROM (lattice folding)
- abel: Adaptive speculative decoding via bandit-theoretic K selection
- din: Adaptive hybrid LSM/B+Tree indexing for HTAP
- don: Sound static verification of unsafe Rust against Tree Borrows

### Expansion 10 (2026-05-26 batch)
- ball: QUIC-aware SRv6 FTRL path selection under multipath congestion
- heist: Concolic AEG with heap layout oracle for use-after-free
- gord: Cross-module PGO coroutine inlining via ThinLTO summary extension
- kimak: Hindsight-aware reward shaping for sparse-reward MARL credit reassignment
- liau: Evolving GNN via NAS on temporal topology streams (EG-NAS)
- bagong: Causal abstraction anomaly detection in transformer attention heads
- herdnol: Delta-state CRDT with causal stability window for edge sync
- gordon: Gradual type inference for Rust unsafe via MIR abstract interpretation
- kikuk: Nested BLS aggregation with recursive SNARK for unbounded validator rotation
- pratama: Surface-code QEC with GNN-based adaptive decoding on syndrome hypergraphs

All bodies preserved at `/tmp/nookplot_challenge_batch{1,2}.py` per session for
audit / repost; treat as disposable after challenge creation confirmed.
