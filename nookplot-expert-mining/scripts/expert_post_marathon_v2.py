#!/usr/bin/env python3
"""Nookplot Expert Marathon V2: 15 wallets × 12 FRESH topics = 180 expert challenges.
Use --bank 2 for second set of topics (after bank 1 is exhausted).
Use --bank 1 (default) for original May 31 topics.

USAGE:
  python3 expert_post_marathon_v2.py --bank 2           # Fresh topics
  python3 expert_post_marathon_v2.py --bank 2 --dry-run # Preview
"""
import subprocess, os, sys, time, random

WALLETS = [
    "abel", "bagong", "ball", "din", "don", "gord", "gordon",
    "heist", "herdnol", "jordi", "kaiju8", "kikuk", "kimak", "liau", "pratama"
]

# BANK 2: Fresh topics for June 1+ runs (different from May 31 bank 1)
DOMAIN_V2 = {
    "abel": {
        "name": "Mechanism Design & Game Theory",
        "spec": "mechanism-design,game-theory,auctions,economics",
        "topics": [
            ("Bayesian Persuasion", "Optimal information design with commitment power — sender utility under prior-dependent signals"),
            ("Contract Theory", "Adverse selection with multidimensional types — screening mechanism for insurance markets"),
            ("Cooperative Games", "Core existence in transferable utility games — Bondareva-Shapley theorem applications"),
            ("Network Games", "Strategic complements on graphs — Nash equilibrium characterization via potential functions"),
            ("Matching Markets", "Many-to-one matching with contracts — cumulative offer mechanism stability proof"),
            ("Public Choice", "Arrow impossibility theorem extensions — domain restrictions enabling strategy-proof voting"),
            ("Contest Design", "Tullock contest with incomplete information — all-pay auction equivalence under risk neutrality"),
            ("Cost Sharing", "Serial cost sharing vs average cost — strategy-proofness under decreasing marginal costs"),
            ("Bargaining Theory", "Rubinstein alternating offers with outside options — subgame perfect equilibrium characterization"),
            ("Regulation", "Laffont-Tirole incentive regulation — cost-plus vs fixed-price contracts under adverse selection"),
            ("Platform Markets", "Two-sided platform pricing with cross-group externalities — Rochet-Tirole model extensions"),
            ("Information Design", "Concavification approach to Bayesian persuasion — multi-receiver signal design under correlation"),
        ],
    },
    "bagong": {
        "name": "AI Safety & Alignment",
        "spec": "alignment,ai-safety,rlhf,constitutional-ai,deception-detection",
        "topics": [
            ("Specification Gaming", "Reward misspecification in open-ended environments — formal characterization of proxy failures"),
            ("Inner Alignment", "Mesa-optimization detection — gradient analysis of learned search processes in base optimizers"),
            ("Honesty Training", "Process reward models for factual accuracy — supervised fine-tuning with verified reasoning chains"),
            ("Power Seeking", "Instrumental convergence thesis formalization — optimal policy analysis in Markov decision processes"),
            ("Interpretability", "Attention head circuit analysis — causal tracing of factual recall in transformer layers"),
            ("Red Teaming", "Automated adversarial prompt generation via gradient-based optimization — jailbreak success rate benchmarking"),
            ("Sleeping Agents", "Backdoor trigger detection in pre-trained models — neural trojans via clean-label data poisoning"),
            ("Value Learning", "Inverse reward learning from suboptimal demonstrations — Boltzmann rationality assumption limitations"),
            ("AI Governance", "Compute governance proposals — hardware tracking mechanisms for frontier model training oversight"),
            ("Corrigible Agents", "Interruptibility in reinforcement learning — off-switch game analysis under uncertainty"),
            ("Scalable Oversight", "Debate framework with computationally bounded judges — complexity-theoretic arguments for truth-seeking"),
            ("Robustness", "Adversarial examples as alignment failures — certified defenses via randomized smoothing bounds"),
        ],
    },
    "ball": {
        "name": "Network Protocols & Congestion Control",
        "spec": "networking,tcp,http3,quic,congestion-control,multipath",
        "topics": [
            ("CUBIC Analysis", "CUBIC congestion window function — concave-convex profile stability under variable RTT"),
            ("QUIC 0-RTT", "Zero round-trip connection establishment — replay attack surface and anti-replay mechanisms"),
            ("DASH Streaming", "Adaptive bitrate algorithms under bandwidth estimation uncertainty — BOLA vs MPC controllers"),
            ("IPsec ESP", "Encapsulating Security Payload with AEAD — GCM vs ChaCha20-Poly1305 throughput comparison"),
            ("MPTCP Scheduling", "Lowest-RTT-first vs redundant transmission — latency optimization across heterogeneous subflows"),
            ("Segment Routing", "SRv6 network programming — source-routed paths with uSID compression for datacenter fabrics"),
            ("P4 Data Plane", "Programmable switch pipelines — match-action table compilation for INT telemetry at line rate"),
            ("VXLAN EVPN", "Overlay multi-tenancy with BGP EVPN — integrated routing and bridging across VTEPs"),
            ("INT Telemetry", "In-band network telemetry with P4 — hop-by-hop latency and queue depth at nanosecond precision"),
            ("RDMA over WAN", "iWARP vs RoCEv2 performance — loss recovery mechanisms for wide-area datacenter interconnect"),
            ("Intent Networking", "Intent-based networking with declarative policies — conflict resolution in multi-controller SDN"),
            ("Network Coding", "Random linear network coding for multicast — field size requirements and generation-based encoding"),
        ],
    },
    "din": {
        "name": "Quantum Computing & Information",
        "spec": "quantum-computing,quantum-information,quantum-algorithms,quantum-error-correction",
        "topics": [
            ("Topological QEC", "Color codes in 3D — transversal logical gates and gauge fixing for universal fault tolerance"),
            ("Quantum Walks Search", "Continuous-time quantum walks on hypercubes — hitting time analysis via spectral decomposition"),
            ("Entanglement Distillation", "Recurrence protocol for noisy Bell pairs — yield analysis under depolarizing channel"),
            ("QKD MDI", "Measurement-device-independent QKD — security proof removing detector side-channel attacks"),
            ("Quantum RAM", "Bucket-brigade qRAM architecture — O(log N) depth queries with O(N) qubits and polylog error"),
            ("Hamiltonian Simulation", "Qubitization for Hamiltonian simulation — optimal query complexity via quantum signal processing"),
            ("Quantum Communication", "Entanglement-assisted classical capacity — superdense coding generalization to noisy channels"),
            ("Tensor Network QEC", "Holographic quantum error correction — AdS/CFT correspondence in HaPPY code construction"),
            ("Quantum Advantage", "Random circuit sampling — cross-entropy benchmarking for quantum supremacy verification"),
            ("Clifford+T", "T-count optimization via ZX-calculus — phase polynomial simplification for fault-tolerant compilation"),
            ("Quantum Thermodynamics", "Landauer's principle in quantum regime — erasure cost for mixed quantum states"),
            ("Boson Sampling", "Gaussian boson sampling with threshold detectors — complexity-theoretic hardness under photon loss"),
        ],
    },
    "don": {
        "name": "Complexity Theory & Lower Bounds",
        "spec": "complexity-theory,fine-grained-complexity,lower-bounds,approximation",
        "topics": [
            ("Natural Proofs", "Razborov-Rudich barrier — pseudorandom function existence blocking circuit lower bounds"),
            ("Algebrization", "Aaronson-Wigdons algebrization barrier — diagonalization relativizing to algebraic extensions"),
            ("Karp-Lipton", "NP ⊂ P/poly implies PH collapse — consequences of small circuits for NP"),
            ("Descriptive Complexity", "Fagin's theorem — existential second-order logic captures NP on ordered structures"),
            ("Proof Complexity", "Resolution width lower bounds — size-width tradeoff via random restriction method"),
            ("Interactive Proofs", "IP=PSPACE via arithmetization — sumcheck protocol for quantified Boolean formula"),
            ("Zero Knowledge", "Constant-round ZK for NP — simultaneous resettable zero-knowledge under DDH"),
            ("Derandomization", "Hardness vs randomness tradeoff — PRG construction from worst-case circuit lower bounds"),
            ("Streaming Algorithms", "Frequency moments in sublinear space — AMS sketch and lower bounds via communication complexity"),
            ("Online Learning", "Regret bounds for online convex optimization — OGD with adaptive step sizes vs AdaGrad"),
            ("Communication", "Information complexity of set disjointness — direct sum theorems for multi-party protocols"),
            ("Quantum Complexity", "QMA-completeness of local Hamiltonian — Kitaev's circuit-to-Hamiltonian construction"),
        ],
    },
    "gord": {
        "name": "Compiler Optimization & JIT",
        "spec": "compilers,webassembly,jit,pgo,compiler-optimization",
        "topics": [
            ("Alias Analysis", "Flow-sensitive points-to analysis with Andersen-style constraints — scalability via cycle detection"),
            ("Vectorization", "SLP vectorization with tree height reduction — cost model for superword-level parallelism"),
            ("Auto-Parallelization", "Polyhedral model loop transformations — Pluto scheduling for affine loop nests"),
            ("Dead Code", "Interprocedural dead code elimination via IPA visibility — whole-program reachability analysis"),
            ("Coroutines", "Stackless coroutine lowering to state machines — heap allocation elimination via escape analysis"),
            ("Module Linking", "Wasm component model — type-checked module composition with interface types adaptation"),
            ("Speculative Devirt", "Type profiling for speculative devirtualization — guard insertion and deoptimization in JVMs"),
            ("Stack Allocation", "Region-based memory management inference — lifetime analysis for stack-promotable heap objects"),
            ("Constraint Solver", "SMT-based constraint solving for type inference — DPLL(T) integration in gradual type systems"),
            ("Binary Lifting", "Static binary translation from x86 to RISC-V — instruction pattern matching and ABI adaptation"),
            ("Macro Expansion", "Hygienic macro expansion with binding analysis — scope set propagation in proc-macro systems"),
            ("Incremental Compilation", "Query-based compilation with Salsa — dependency tracking for demand-driven recomputation"),
        ],
    },
    "gordon": {
        "name": "Type Theory & PL Design",
        "spec": "type-theory,dependent-types,gradual-typing,refinement-types,PL-design",
        "topics": [
            ("Cubical TT", "Cubical type theory with Kan operations — computational interpretation of univalence axiom"),
            ("Session Types", "Multiparty session types with global types — deadlock freedom via projection and merging"),
            ("Ownership Types", "Uniqueness typing for mutable references — affine types and borrowing in systems PL design"),
            ("CPS Transform", "Call-by-value CPS translation preserving types — double-negation translation for classical logic"),
            ("Module Systems", "ML module system with first-class modules — packing/unpacking with sealed signatures"),
            ("Metaprogramming", "Staged computation with typed multi-stage programming — cross-stage persistence and type safety"),
            ("Type Classes", "Coherent type class resolution — overlapping instances with functional dependencies"),
            ("Continuations", "Delimited continuations (shift/reset) — type system for control operators with answer-type polymorphism"),
            ("Indexed Types", "GADTs vs indexed type families — expressiveness comparison with dependent pattern matching"),
            ("Effect Handlers", "Typed effect handlers with row polymorphism — shallow vs deep handler semantics"),
            ("Logical Relations", "Step-indexed logical relations for recursive types — semantic soundness proof for System F_omega_mu"),
            ("Elaboration Z", "Bidirectional elaboration for dependent types — unification with metavariables and constraint solving"),
        ],
    },
    "heist": {
        "name": "Offensive Security & Exploitation",
        "spec": "security,penetration-testing,ebpf,firmware,side-channel",
        "topics": [
            ("Spectre v2", "Branch target injection via BTB poisoning — retpoline mitigation effectiveness analysis"),
            ("Container Escape", "cgroups namespace escape via /proc/self/mem writes — kernel pointer overwrite chain"),
            ("Browser Exploit", "V8 Turbofan JIT type confusion — speculative optimization bypass for arbitrary read/write"),
            ("Kernel Exploit", "use-after-free in Linux kmalloc-64 — cross-cache exploitation via SLUB freelist poisoning"),
            ("Malware Analysis", "Polymorphic code detection via semantic equivalence — symbolic execution for unpacking"),
            ("Crypto Implementation", "ECDSA nonce bias from stack-based timing — lattice attack with partial nonce leakage"),
            ("SGX Attack", "Controlled-channel attacks on Intel SGX — page-fault side channel for enclave memory access patterns"),
            ("WiFi Security", "WPA3 Dragonfly handshake vulnerabilities — cache-based side channel on PWE derivation"),
            ("Binary Protection", "CFI bypass via data-oriented programming — gadget chaining without control flow transfer"),
            ("Hypervisor Escape", "VM escape via emulated device — QEMU virtio-blk buffer overflow to hypervisor memory"),
            ("Blockchain Exploit", "Flash loan sandwich attacks — MEV extraction via frontrunning with atomic transaction bundles"),
            ("IoT Firmware", "ARM TrustZone OP-TEE exploitation — shared memory buffer overflow to secure world privilege escalation"),
        ],
    },
    "herdnol": {
        "name": "Distributed Systems & Consensus",
        "spec": "distributed-systems,consensus,replication,crdt,fault-tolerance",
        "topics": [
            ("Viewstamped Repl", "Viewstamped replication revisited — recovery protocol optimization for stable primary"),
            ("State Machine", "Deterministic state machine replication — batching and pipelining for latency-sensitive workloads"),
            ("CockroachDB", "Parallel commits in CockroachDB — transactional pipelining with write intent resolution"),
            ("Spanner", "Google Spanner TrueTime — external consistency via commit-wait and GPS+atomic clocks"),
            ("Dynamo", "Dynamo-style systems — vector clock conflict resolution vs last-writer-wins with LWW-element-sets"),
            ("CRDT Sequences", "RGA and Yjs CRDTs for collaborative text — interleaving anomalies and fractional indexing"),
            ("Byzantine", "HotStuff BFT consensus — linear message complexity via threshold signatures and pipelining"),
            ("Disaggregated", "Disaggregated memory with RDMA — remote memory access patterns for distributed hash tables"),
            ("Serverless", "Cold start optimization in serverless — snapshot-based restore vs lightweight VM firecracker"),
            ("Stream Processing", "Exactly-once semantics in Kafka Streams — transactional producer with idempotent write protocol"),
            ("Clock Synchronization", "NTP vs PTP vs HLC — clock skew bounds for distributed snapshot consistency"),
            ("Data Placement", "Erasure coding vs replication — durability-cost tradeoff with correlated failure models"),
        ],
    },
    "jordi": {
        "name": "Numerical Optimization & Scientific Computing",
        "spec": "optimization,numerical-methods,scientific-computing,linear-algebra",
        "topics": [
            ("Frank-Wolfe", "Conditional gradient method with away-step — linear convergence over polytopes via geometric strong convexity"),
            ("Mirror Descent", "Online mirror descent with adaptive regularization — data-dependent regret bounds for simplex domains"),
            ("Tensor Methods", "Cubic regularization of Newton's method — global convergence rate for nonconvex optimization"),
            ("Saddle Point", "Extragradient method for variational inequalities — last-iterate convergence under monotonicity"),
            ("Randomized LA", "Randomized SVD with power iteration — singular value gap dependence for spectral approximation"),
            ("Optimal Transport", "Sinkhorn algorithm for entropic OT — convergence analysis and stabilization for unbalanced measures"),
            ("Sparse Recovery", "Iterative hard thresholding for compressed sensing — restricted isometry property bounds"),
            ("Bandit Optimization", "Linear bandits with Thompson sampling — Bayesian regret bounds via elliptical confidence sets"),
            ("Spectral Methods", "Phase retrieval via Wirtinger flow — initialization sensitivity and gradient descent landscape"),
            ("Multi-Objective", "Pareto front approximation via scalarization — weight space partition for bi-objective convex problems"),
            ("Distributed Opt", "Decentralized gradient descent — consensus rate vs optimization rate tradeoff on expander graphs"),
            ("Conditioning", "Preconditioned conjugate gradient with incomplete Cholesky — fill-level vs convergence rate analysis"),
        ],
    },
    "kaiju8": {
        "name": "Statistical Theory & Inference",
        "spec": "statistics,statistical-inference,high-dimensional-statistics,robust-statistics",
        "topics": [
            ("Conformal Prediction", "Distribution-free predictive intervals — coverage validity under exchangeability assumption"),
            ("Bayesian Nonparametrics", "Dirichlet process mixture models — posterior consistency under misspecification"),
            ("Multiple Testing", "Knockoff filter for FDR control — variable selection with guaranteed false discovery rate"),
            ("Time Series", "Structural break detection via CUSUM — sequential monitoring with boundary crossing probabilities"),
            ("Spatial Statistics", "Gaussian process regression — kernel selection via marginal likelihood and RKHS embedding"),
            ("Survival Analysis", "Cox proportional hazards — partial likelihood estimation under informative censoring"),
            ("Network Inference", "Stochastic block model — exact recovery threshold via information-theoretic bounds"),
            ("Mixture Models", "EM algorithm convergence for Gaussian mixtures — identifiability conditions and local optima"),
            ("Quantile Regression", "Pinball loss optimization — check function for conditional quantile estimation at multiple levels"),
            ("Information Theory", "Mutual information estimation — k-nearest neighbor methods with bias correction"),
            ("Ranking", "Plackett-Luce model — maximum likelihood estimation for partial rankings with ties"),
            ("Experimental Design", "Optimal treatment assignment — stratified randomization with covariate balancing constraints"),
        ],
    },
    "kikuk": {
        "name": "Protocol Design & API Architecture",
        "spec": "protocol-design,api-gateway,service-mesh,zero-trust,rate-limiting",
        "topics": [
            ("GraphQL Federation", "Apollo Federation query planning — subgraph composition with requires/provides directives"),
            ("WebSocket Protocol", "WebSocket compression (permessage-deflate) — context takeover tradeoffs for memory vs bandwidth"),
            ("Message Queue", "NATS JetStream consumer groups — at-least-once delivery with interest-based retention policies"),
            ("Distributed Lock", "Redlock algorithm correctness — safety analysis under clock drift and process pause"),
            ("Consensus Protocol", "HotStuff linear BFT — chaining and pipelining for 3-chain commit rules"),
            ("P2P Protocol", "libp2p protocol composition — transport multiplexing with Yamux and Noise framework security"),
            ("API Pagination", "Cursor-based vs offset pagination — consistency guarantees under concurrent writes"),
            ("Health Check", "Deep health checks with dependency graph — cascading failure detection and circuit propagation"),
            ("Feature Flags", "Multi-variant feature flag evaluation — consistent hashing for sticky user assignments"),
            ("Webhook Delivery", "Webhook delivery with exponential backoff — HMAC signature verification and replay prevention"),
            ("API Monetization", "Usage-based API metering — distributed counting with eventual consistency and quota reconciliation"),
            ("mTLS Automation", "Automated certificate rotation with SPIRE — SVID renewal under CA failover scenarios"),
        ],
    },
    "kimak": {
        "name": "Reinforcement Learning & Multi-Agent Systems",
        "spec": "reinforcement-learning,policy-gradient,multi-agent,curriculum-learning",
        "topics": [
            ("Dreamer", "World model learning with latent dynamics — RSSM architecture for visual RL from pixels"),
            ("Decision Transformer", "Sequence modeling for RL — return-conditioned trajectory prediction with GPT-style attention"),
            ("Population-Based", "Population-based training with asynchronous evaluation — hyperparameter scheduling for deep RL"),
            ("Reward Machine", "Reward machines for task specification — automata-guided reward shaping for temporally extended goals"),
            ("Sim-to-Real", "Domain randomization with adaptive curriculum — Bayesian optimization for simulation parameter selection"),
            ("Attention Policy", "Transformer policies for multi-agent — permutation-invariant observation encoding for cooperative tasks"),
            ("Offline MARL", "Offline multi-agent RL with dataset constraints — pessimistic value estimation under partial observability"),
            ("Communication", "Emergent communication in cooperative games — TarMAC attention-based message passing protocol"),
            ("Transfer RL", "Policy reuse via skill discovery — unsupervised pretraining for downstream task adaptation"),
            ("Goal-Conditioned", "Hindsight experience replay with goal relabeling — density estimation for sparse reward environments"),
            ("Neural ODE Policy", "Continuous-depth policy networks — adjoint method for memory-efficient backpropagation through time"),
            ("Shaping Potential", "Potential-based reward shaping invariance — generalized advantage estimation with learned potential functions"),
        ],
    },
    "liau": {
        "name": "Graph Neural Networks & Geometric Deep Learning",
        "spec": "graph-neural-networks,message-passing,subgraph-gnn,dense-retrieval",
        "topics": [
            ("Equivariant GNN", "E(n) equivariant graph networks — weight sharing under Euclidean group actions for 3D molecular data"),
            ("Graph Contrastive", "GraphCL contrastive learning — augmentation strategies for molecular and social network graphs"),
            ("Scatter-Gather", "Scatter-gather optimization for GNN — fused CUDA kernels for SpMM and SDDMM on sparse adjacency"),
            ("Dynamic GNN", "Temporal graph networks with neighbor sampling — streaming edge updates with memory module eviction"),
            ("Graph Generation", "GraphRNN autoregressive generation — node ordering sensitivity and BFS sequence modeling"),
            ("Heterogeneous GNN", "Metapath2vec and RGCN — relation-specific aggregation for knowledge graph completion"),
            ("Graph Diffusion", "Graph diffusion convolution — personalized PageRank as fixed-size receptive field for node classification"),
            ("Expressive Power", "Provably powerful GNNs — k-WL hierarchy and subgraph counting for distinguishing non-isomorphic graphs"),
            ("Sampling Strategy", "Cluster-GCN and GraphSAINT — minibatch training via graph partitioning and importance sampling"),
            ("Positional Encoding", "Random walk positional encoding — PEs from transition matrix eigenvectors for transformer input"),
            ("Molecule Generation", "Junction tree VAE for molecular graphs — tree decomposition and validity-preserving decoding"),
            ("Neural ODE Graph", "Graph neural ODEs — continuous-time message passing for irregular time series on graphs"),
        ],
    },
    "pratama": {
        "name": "Quantum Algorithms & Cryptography",
        "spec": "quantum-computing,quantum-algorithms,qec,quantum-cryptography,vqe",
        "topics": [
            ("Quantum SDP", "Quantum semidefinite programming — Gibbs sampling with quantum relative entropy minimization"),
            ("Isogeny Crypto", "SIDH/SIKE security analysis — torsion point information leakage and Castryck-Decru attack"),
            ("Quantum Secret Sharing", "Quantum secret sharing with graph states — threshold access structure via stabilizer codes"),
            ("QRAM Alternatives", "Parallel quantum RAM architectures — fanout-based qRAM with logarithmic depth and polynomial qubits"),
            ("Quantum Chemistry", "VQE for molecular ground states — ansatz design for strongly correlated systems (FeMoco catalyst)"),
            ("Blind QC", "Universal blind quantum computing — measurement-based computation with encrypted measurement angles"),
            ("Quantum Network", "Quantum internet routing — entanglement purification chain optimization across quantum repeaters"),
            ("Fault-Tolerant FT", "Lattice surgery for surface codes — logical CNOT via merge-split operations with boundary defects"),
            ("Quantum Sensing", "Heisenberg-limited phase estimation — adaptive Bayesian protocol for optical interferometry"),
            ("Homomorphic QE", "Quantum fully homomorphic encryption — Clifford+T gadget implementation with T-gate bootstrapping"),
            ("Quantum Voting", "Quantum voting protocols — anonymity with verifiability via entangled ballot states"),
            ("Noise Spectroscopy", "Quantum noise spectroscopy — dynamical decoupling sequences for characterizing non-Markovian environments"),
        ],
    },
}

def load_env(wallet):
    env = os.environ.copy()
    env_path = f"/home/ryzen/nookplot-{wallet}/.env"
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k] = v.strip('"').strip("'")
    return env

def generate_post_body(topic, description, domain_spec):
    difficulty = random.choice(["Expert", "Advanced", "Expert"])
    reward = random.choice(["45K", "50K", "55K"])
    max_subs = random.choice(["15", "20", "25"])

    return f"""## Mining Challenge: {topic}

**Domain**: {domain_spec.split(',')[0].title()} | **Difficulty**: {difficulty}

### Problem Statement
Design and implement a solution for {description}. Your solution must handle edge cases and demonstrate deep domain expertise.

### Your Task
1. Formalize the problem with precise mathematical definitions
2. Implement a working solution with at least 150 lines of well-documented code
3. Analyze algorithmic complexity with rigorous proofs
4. Provide empirical validation with synthetic and real-world benchmarks

### Constraints
- Time complexity must be asymptotically optimal
- Space complexity limited to O(n) auxiliary memory
- Solution must handle edge cases: empty inputs, extreme values, degenerate cases

### Evaluation Criteria
| Criterion | Weight | Description |
|-----------|--------|-------------|
| Correctness | 35% | All test cases pass including edge cases |
| Algorithmic Quality | 25% | Optimal complexity with rigorous analysis |
| Code Quality | 20% | Readable, well-structured, thoroughly commented |
| Novelty | 20% | Creative approach beyond standard textbook solutions |

### References
1. Relevant academic papers in {domain_spec.split(',')[0]} from top venues (STOC, FOCS, NeurIPS, SOSP, etc.)

**Reward**: {reward}K NOOK • **Duration**: 7 days • **Max Submissions**: {max_subs}"""

def post_to_wallet(wallet, posts, dry_run=False):
    env = load_env(wallet)
    domain_info = DOMAIN_V2[wallet]
    domain_spec = domain_info["spec"]

    print(f"\n{'='*60}")
    print(f"  WALLET: {wallet} — {domain_info['name']}")
    print(f"  Posts to create: {len(posts)}")
    print(f"{'='*60}")

    success = 0
    fail = 0

    for i, (topic, description) in enumerate(posts):
        body = generate_post_body(topic, description, domain_spec)
        title = f"Mining Challenge: {topic}"

        if dry_run:
            print(f"  [{i+1}/12] DRY-RUN: {topic}")
            success += 1
            continue

        cmd = [
            "nookplot", "publish", "--title", title, "--body", body,
            "--community", "engineering", "--tags", domain_spec
        ]

        for attempt in range(3):
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60,
                cwd=f"/home/ryzen/nookplot-{wallet}", env=env
            )
            combined = result.stdout + result.stderr

            if "Published" in combined or "published" in combined.lower():
                print(f"  [{i+1}/12] ✓ {topic}")
                success += 1
                break
            else:
                if attempt < 2:
                    print(f"  [{i+1}/12] ⚠ Retry {attempt+1} for: {topic}")
                    time.sleep(3)
                else:
                    print(f"  [{i+1}/12] ✗ FAIL: {topic}")
                    print(f"      {combined[:200]}")
                    fail += 1

        if i < len(posts) - 1:
            time.sleep(11)

    return success, fail

def main():
    dry_run = "--dry-run" in sys.argv
    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"╔══════════════════════════════════════════════════════╗")
    print(f"║  NOOKPLOT EXPERT MARATHON V2 — {mode}        ║")
    print(f"║  15 wallets × 12 FRESH topics = 180 challenges      ║")
    print(f"╚══════════════════════════════════════════════════════╝")

    total_ok = 0
    total_fail = 0
    results = {}

    for wallet in WALLETS:
        if wallet not in DOMAIN_V2:
            print(f"  ⚠ Skipping {wallet} — no domain config")
            continue

        posts = DOMAIN_V2[wallet]["topics"]
        ok, fail = post_to_wallet(wallet, posts, dry_run=dry_run)
        results[wallet] = (ok, fail)
        total_ok += ok
        total_fail += fail

        print(f"  {wallet}: {ok}/12 OK, {fail}/12 FAIL")

        if wallet != WALLETS[-1]:
            print(f"  --- 30s cooldown between wallets ---")
            time.sleep(30)

    print(f"\n{'='*60}")
    print(f"  MARATHON V2 COMPLETE: {total_ok}/{total_ok+total_fail} posts")
    print(f"  Success: {total_ok} | Failed: {total_fail}")
    print(f"{'='*60}")

    for w, (ok, fail) in results.items():
        bar = "█" * ok + ("░" * fail)
        print(f"  {w:12s} [{bar}] {ok}/12")

    return 0 if total_fail == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
