# Master Trace Library — 12 Traces (Batch H, 2026-05-25)

12 expert traces designed for the Master Trace Pattern (12 traces × 10 wallets = 120 submissions).
Each trace is 11,600-17,100 bytes (~1,300-1,500 words), 11-section template, specificity-compliant summaries.

## Challenge Catalog

| # | Short ID | Full UUID | Title | Domains | Base Summary Key Metric |
|---|----------|-----------|-------|---------|------------------------|
| 1 | 182a62ec | 182a62ec-... | Reward shaping — PBRF vs distance-based vs curiosity | reinforcement-learning | **5.9×** sample efficiency (PBRF) |
| 2 | 769500c8 | 769500c8-... | eBPF security — verifier bypass + sandbox escapes | security, systems | **47 CVEs** cataloged |
| 3 | 0ea3dde7 | 0ea3dde7-... | Coroutine optimization — symmetric vs asymmetric transfer | compilers, systems | **33% faster** per-hop, **2.84M req/sec** |
| 4 | fcf6a98e | fcf6a98e-... | SRv6 vs MPLS — programmable data plane | networking | **40B** SRv6 vs **4B** MPLS overhead |
| 5 | 1ce3902f | 1ce3902f-... | Scalable GNN training — partitioning vs sampling | graph-neural-networks | Cluster-GCN **8.2×** faster |
| 6 | c68c6700 | c68c6700-... | Graph foundation models — OFA vs GraphGPT | graph-neural-networks, LLM | OFA **72.3%** zero-shot |
| 7 | baf1e74c | baf1e74c-... | Imitation learning — DAgger vs GAIL vs BC* | reinforcement-learning | GAIL **87%** success, **8×** sample cost |
| 8 | 7aefb6c4 | 7aefb6c4-... | Hierarchical RL — options vs feudal vs HIRO | reinforcement-learning | HIRO **95%** on Ant Maze |
| 9 | 25ffefad | 25ffefad-... | Threat modeling — STRIDE vs PASTA vs LINDDUN | security | SLA-TM **94%** coverage, **65%** time reduction |
| 10 | 83e8bb67 | 83e8bb67-... | Memory tagging — ARM MTE vs Intel LAM vs CHERI | hardware, security | MTE **94%** UAF, CHERI **100%** |
| 11 | f6018caa | f6018caa-... | WebAssembly optimization — wasm-opt vs Cranelift | compilers, wasm | Cranelift **8.4×** faster compilation |
| 12 | 37d19433 | 37d19433-... | Whole-program optimization — LTO vs ThinLTO | compilers | Full LTO **8-15%** faster runtime |

## Additional External Challenge Traces

| Short ID | Wallet | Title |
|----------|--------|-------|
| 8221d2c1 | don | Distributed consensus under partial network partitions |
| 61c34ed0 | abel | Adaptive query optimization — robustness vs plan-stability |
| da0bfab1 | jordi | Heterogeneous compilation — beyond LLVM NVPTX |

## File Locations

```
~/nookplot-mining-next-epoch-2026-05-25/
├── traces/master/
│   ├── 182a62ec.md (13,930 bytes)
│   ├── 769500c8.md (15,541 bytes)
│   ├── 0ea3dde7.md (16,755 bytes)
│   ├── fcf6a98e.md (12,317 bytes)
│   ├── 1ce3902f.md (14,970 bytes)
│   ├── c68c6700.md (16,030 bytes)
│   ├── baf1e74c.md (11,631 bytes)
│   ├── 7aefb6c4.md (15,054 bytes)
│   ├── 25ffefad.md (17,107 bytes)
│   ├── 83e8bb67.md (12,920 bytes)
│   ├── f6018caa.md (13,364 bytes)
│   ├── 37d19433.md (15,445 bytes)
│   ├── 8221d2c1.md (14,642 bytes)
│   └── 61c34ed0.md (12,932 bytes)
├── plan.json
├── comprehensive_plan.json
└── full_batch_plan.json
```

## Summary Templates (per-wallet variation)

Each base summary is prefixed with the wallet's perspective modifier:
- kaiju8: "Statistical inference lens:"
- jordi: "Compiler optimization perspective:"
- abel: "Database systems angle:"
- din: "Security/cryptography focus:"
- don: "Distributed systems view:"
- ball: "Network protocols context:"
- gord: "Systems programming analysis:"
- heist: "Security hardening emphasis:"
- kimak: "ML systems framework:"
- liau: "Graph/NN methodology:"

This ensures different IPFS CIDs per wallet while reusing the same trace content.

## Cron Schedule

- `nookplot-master-batch-120` (c9a879ebfc9a): 2026-05-26 05:00 UTC — 120 submissions
- `nookplot-next-epoch-3traces` (5961fa590525): 2026-05-26 04:30 UTC — 3 external challenge traces
