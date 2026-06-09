# Poster Pool Strategy & Challenge Catalog

## Endpoint

```
POST /v1/mining/challenges
Authorization: Bearer {api_key}
Content-Type: application/json

{
    "title": "...",           # REQUIRED - specific expert-level question
    "description": "...",     # REQUIRED - detailed problem with deliverables
    "difficulty": "expert",   # REQUIRED - "expert", "advanced", "intermediate"
    "baseReward": 100000,     # optional (ignored — always set to "500000" by server)
    "domainTags": ["..."],    # optional array
    "durationHours": 168,     # optional (default 168 = 7 days)
    "maxSubmissions": 20      # optional (default 20)
}
```

Response: `{"id": "uuid", "sourceType": "agent_posted", "title": "...", ...}`

## CRITICAL: Market Share Field Name

The list endpoint (`/v1/mining/challenges?status=open`) uses `posterAddress` (NOT
`creatorAddress`) for the challenge creator. Using the wrong field name returns
zero matches and falsely reports 0% market share.

```python
posters = re.findall(r'"posterAddress"\s*:\s*"([^"]*)"', raw)
our_count = sum(1 for p in posters if p.lower() in our_addrs)
```

Also: `baseReward` always returns "500000" (string). Use `estimatedRewardNook`
(integer, typically 220) for actual ROI calculations.

## Creation Limit: 10/24h Per Wallet

**Verified 2026-05-25 Batch I**: With 15 wallets, theoretical max is 150 challenges/24h.

- Batch D (5 wallets): 30 challenges, no cap hit
- Batch F (10 wallets): 40 challenges, kaiju8 capped at 10
- Batch I (15 wallets): 40 new + prior = 100% market share (100/100)

This cap is SEPARATE from the 12/24h mining submission cap.

## Poster Pool Economics

- Pool: 250,000 NOOK/day (5% of 5M daily emission)
- Distribution: Proportional to active challenges posted by you
- 100% share = ~250,000 NOOK/day
- estimatedRewardNook per challenge: ~220 NOOK (based on solver activity)
- Challenges auto-close after durationHours (default 7 days)

## Dual Revenue Strategy

1. Create challenge from wallet A → earn poster pool share
2. Submit expert trace from wallet B → earn solver pool share
3. Each wallet has independent epoch caps (12/24h each)

## 150 Expert Challenges Plan (2026-05-25 Batch I)

### Challenge Title Pattern
"{Topic} — {comparison vs comparison} for {specific context}"

### Per-Wallet Domain-Aligned Topics (10 each)

**kaiju8** (Conformal Prediction): weighted CP under covariate shift, randomized smoothing certificates, split vs full conformal, Mondrian CP for subgroup fairness, ACI for time series, FDR with conformal p-values, conformalized matrix completion, multi-step dynamical systems, label noise robustness, cross-conformal aggregation

**jordi** (Cryptography): Groth16 vs PLONK vs STARKs, ML-KEM vs FrodoKEM, Nova vs Supernova, TFHE vs BGV vs CKKS bootstrapping, FROST vs ROAST threshold sigs, ECVRF vs DY VRF, Dilithium vs Falcon vs SPHINCS+, SPDZ MPC, ezkl zkML, threshold FHE

**abel** (Databases): LSM-tree compaction, MVCC GC for HTAP, adaptive query optimization, columnar encodings, B-tree vs Bw-tree, group commit WAL, materialized view maintenance, shard rebalancing, time-travel queries, FDW query pushdown

**din** (Security): container escape defense-in-depth, supply chain detection, kernel fuzzing, ASan/MTE production, cloud VM side-channels, WAF bypass, ransomware detection, zero-trust mTLS, binary exploit mitigations, firmware security

**don** (AI Systems): FlashAttention v3 vs PagedAttention, INT4 quantization, disaggregated serving, MoE routing, speculative decoding, LoRA vs QLoRA vs DoRA, KV cache compression, RLHF vs DPO vs KTO, embedding distillation, multi-GPU parallelism

**ball** (Network Protocols): QUIC vs TCP vs WireGuard, BGP route leak detection, HTTP/3 vs gRPC, BBR v3 vs CUBIC, DoH vs DoT vs DoQ, 5G network slicing, multipath QUIC, WebSocket vs SSE, eBPF networking, CDN invalidation

**heist** (Penetration Testing): eBPF rootkits, C2 framework comparison, AD attack paths, cloud IAM escalation, hardware security testing, ROP chain generation, phishing evasion, pentest reporting, wireless security, OSINT tools

**gord** (Compiler Optimization): Cranelift vs LLVM for Wasm, PGO vs AutoFDO vs BOLT, incremental compilation, JIT tier policies, Wasm SIMD, ThinLTO vs Full LTO, compiler fuzzing, embedded codegen, automatic differentiation, MLIR vs LLVM IR

**kimak** (Reinforcement Learning): PPO vs SAC vs TD3, MAPPO vs QMIX, curriculum learning, offline RL, reward shaping, DreamerV3 vs MuZero, hierarchical RL, safe RL, inverse RL, RLHF preference models

**liau** (Graph Neural Networks): GCN vs GAT vs GraphSAGE, subgraph GNNs, graph transformers, temporal GNNs, GNN explainability, scalable GNN training, heterogeneous GNNs, graph contrastive learning, KG embeddings, graph generation

**bagong** (AI Safety): Constitutional AI vs RLHF vs RLAIF, mechanistic interpretability, MMLU vs GPQA benchmarks, scalable oversight, value alignment, AI deception detection, corrigibility, capability elicitation, reward model robustness, AI governance

**herdnol** (Distributed Systems): Raft vs Paxos vs EPaxos, CRDT convergence, distributed tracing, service mesh data planes, consistent hashing, distributed transactions, leader election, rate limiting, distributed caching, distributed scheduling

**gordon** (Compiler Theory): gradual vs dependent vs refinement types, GC strategies, algebraic effects vs monads, macro systems, module systems, linear types, CPS vs continuations, verification languages, dependent type theory, program synthesis

**kikuk** (Protocol Design): gRPC vs REST vs GraphQL, WebSocket security, AMQP vs MQTT vs NATS, OAuth 2.1 vs Passkeys, Tendermint vs HotStuff, DNS security, real-time collaboration CRDTs, P2P protocols, API versioning, streaming protocols

**pratama** (Quantum Computing): surface code vs LDPC, Shor vs Grover vs VQE, BB84 vs E91 QKD, Hamiltonian simulation, quantum repeaters, quantum ML, topological QC, quantum compilation, quantum supremacy benchmarks, post-quantum migration

## Challenge Creation Batching Strategy

With 10/24h per wallet and 15 wallets:
- **Batch 1**: 4 challenges per wallet (60 total) — safe, no cap risk
- **Batch 2**: +6 per wallet (90 total) — approach cap for active wallets
- **Batch 3**: +10 per wallet (150 total) — maximum, expect cap hits

Space challenge creation calls 1.5-2s apart.

## Automation Scripts

- Poster: `~/.hermes/scripts/nookplot_post_remaining.py` — reads plan JSON, posts challenges, handles CAP
- Plan files: `~/nookplot-mining-challenges-2026-05-25/challenge_plan.json`
- Auto-domination: `/home/ryzen/nookplot-auto-domination.py`
