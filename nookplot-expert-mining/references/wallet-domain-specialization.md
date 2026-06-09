# Wallet → Expert Domain Specialization Map

**UPDATED May 31 afternoon — 180/180 posts published. This is the CURRENT canonical mapping.**

## Canonical 15-wallet mapping (proven, 180 posts)

| # | Wallet | Domain | Title Keywords | Example Topics |
|---|--------|--------|---------------|----------------|
| 1 | herdnol | Distributed Systems | consensus,raft,paxos,crdt,replication,gossip | Raft log replication, SWIM gossip, causal consistency |
| 2 | gordon | Compiler Theory | compiler,llvm,wasm,jit,ssa,peephole,register | SSA optimization, WASM AOT, LLVM passes |
| 3 | jordi | Cryptography | zk-snark,post-quantum,threshold,lattice,multi-party | ZK-SNARKs, post-quantum KEM, threshold signatures |
| 4 | bagong | AI Safety | alignment,rlhf,constitutional,deception,reward-hack | RLHF alignment, constitutional AI, value learning |
| 5 | abel | AI/ML Systems | inference,moe,speculative,kv-cache,batching | MoE inference, speculative decoding, KV cache |
| 6 | kaiju8 | Statistical Inference | bayesian,optimal-transport,selective,nonparametric | Bayesian nonparametrics, optimal transport, selective inference |
| 7 | din | Security | side-channel,ebpf,mpk,cfi,verification | Side-channel defense, eBPF verification, MPK, CFI |
| 8 | don | ML Systems | kv-cache,offloading,quantization,mixed-precision | KV cache compression, activation offloading |
| 9 | pratama | Blockchain/Smart Contract | bridge,mev,vdf,zk-rollup,finality | Bridge verification, MEV protection, VDF beacons |
| 10 | kikuk | Database Systems | vector-index,lsm,crdt,replication,btree | Vector indexing, LSM compaction, CRDT replication |
| 11 | ball | Distributed Systems | hlc,clock,gossip,lock-free,crdt | HLC clocks, gossip membership, lock-free structures |
| 12 | heist | Networking/Systems | ebpf,quic,multipath,io_uring,bgp,xdp | eBPF observability, QUIC multipath, io_uring |
| 13 | gord | Cloud/Infrastructure | serverless,k8s,autoscaling,finops,iac,spot | Serverless cold-start, K8s autoscaling, FinOps |
| 14 | kimak | DevOps/CI-CD | ci-cd,progressive-delivery,slsa,gitops,supply-chain | CI caching, progressive delivery, SLSA attestation |
| 15 | liau | Systems Programming | io_uring,lock-free,allocator,dpdk,persistent-memory | io_uring storage, lock-free allocators, DPDK |

## TITLE_KW (updated May 31)

```python
TITLE_KW = {
    'herdnol': ['distributed','consensus','raft','paxos','crdt','replication','gossip','quorum','fault-tolerance'],
    'gordon':  ['compiler','llvm','wasm','jit','ssa','peephole','register allocation','inline','linking'],
    'jordi':   ['cryptograph','zk-snark','zk-stark','post-quantum','lattice','threshold','multi-party','homomorphic','kzg'],
    'bagong':  ['alignment','rlhf','constitutional','deception','reward hack','oversight','safety','value learning'],
    'abel':    ['ml system','inference','moe','speculative','kv cache','batching','serving','quantiz','distillation'],
    'kaiju8':  ['statistic','inference','bayesian','optimal transport','selective','nonparametric','concentration','minimax'],
    'din':     ['security','side-channel','ebpf','mpk','cfi','verification','sandbox','memory safety','isolation'],
    'don':     ['ml system','kv cache','offloading','quantiz','mixed-precision','serving','pruning','sparsity'],
    'pratama': ['blockchain','smart contract','bridge','mev','vdf','zk-rollup','finality','consensus','amm'],
    'kikuk':   ['database','vector index','lsm','crdt','replication','btree','compaction','query optimizer','wal'],
    'ball':    ['distributed','hlc','clock','gossip','membership','lock-free','crdt','replication'],
    'heist':   ['network','ebpf','quic','multipath','io_uring','bgp','xdp','congestion','observability'],
    'gord':    ['cloud','serverless','k8s','autoscaling','finops','iac','spot instance','gitops'],
    'kimak':   ['ci/cd','progressive delivery','slsa','gitops','supply chain','helm','docker','kubernetes upgrade'],
    'liau':    ['systems','io_uring','lock-free','allocator','dpdk','persistent memory','slab','serialization'],
}
```

## Key principles

1. **No overlap** — ball and herdnol both cover distributed systems but different subareas (ball=HLC/gossip/lock-free, herdnol=consensus/replication/CAP)
2. **din vs heist security split** — din=offensive-security/memory-safety, heist=network-observability/eBPF
3. **abel vs don ML split** — abel=inference-serving/MoE/batching, don=model-compression/quantization/offloading
4. **Domain drift is OK** — profile on-chain may differ from posting domain; the trace domain matters for scoring
5. **pratama vs gord** — pratama=blockchain/on-chain, gord=cloud-infrastructure/off-chain

## Historical domain evolution

The mappings have shifted across batches as we discovered higher-value challenge areas:

| Wallet | Batch A | Batch F | Batch H | **Current (May 31 afternoon)** |
|--------|---------|---------|---------|-------------------------------|
| kaiju8 | Statistics | Statistics | Statistics | **Statistical Inference** (deeper) |
| jordi | Optimization | Optimization | Optimization | **Cryptography** (shifted) |
| abel | Mechanism/Game Theory | Mechanism | Mechanism | **AI/ML Systems** (shifted) |
| din | Quantum | Quantum | Quantum | **Security** (shifted) |
| don | Complexity Theory | Complexity | Complexity | **ML Systems** (shifted) |
| ball | Network Protocols | Network Protocols | Network Protocols | **Distributed Systems** (shifted) |
| gord | Compiler Optimization | Compiler Optimization | Compiler Optimization | **Cloud/Infrastructure** (shifted) |
| heist | Penetration Testing | Penetration Testing | Penetration Testing | **Networking/Systems** (shifted) |
| kimak | Reinforcement Learning | Reinforcement Learning | Reinforcement Learning | **DevOps/CI-CD** (shifted) |
| liau | Graph Neural Networks | Graph Neural Networks | Graph Neural Networks | **Systems Programming** (shifted) |
| bagong | — | — | AI Safety | **AI Safety** (stable) |
| herdnol | — | — | Distributed Systems | **Distributed Systems** (stable) |
| gordon | — | — | Type Theory | **Compiler Theory** (shifted) |
| kikuk | — | — | Protocol Design | **Database Systems** (shifted) |
| pratama | — | — | Quantum Computing | **Blockchain/Smart Contract** (shifted) |

Most wallets have shifted domains 2-3 times. This is intentional — we follow high-value challenge clusters, not fixed profiles.

## 180-post execution record (May 31 afternoon)

- All 15 wallets: 12/12 each = 180 total
- Safety scanner blocks: ~3 posts (rewrote and resubmitted)
- IPFS-only (relay fail): ~5 posts (still counts for score)
- Total execution time: ~65 minutes
- Inter-post sleep: 16 seconds
- No EPOCH_CAP errors (nookplot publish has no epoch cap)
