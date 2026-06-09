#!/usr/bin/env python3
"""
Nookplot Batch Challenge Generator — 15 wallets × 12 expert challenges = 180 total.
Usage: python3 full_batch_gen.py <wallet_name>

Proven architecture:
- subprocess.run() with list args avoids ALL shell escaping (backticks, $, quotes)
- 15 parallel terminal(background=True) processes — ~150s per wallet
- 11s sleep between posts avoids transient relay failures
- Credit delta verification: Spent should increase by ~1.8 per wallet (12 × 0.15)

Wallet → Domain mapping (verified 2026-05-31):
  herdnol: Distributed Systems
  gordon:  Compiler Theory
  jordi:   Cryptography
  bagong:  AI Safety
  abel:    Databases
  kaiju8:  Statistical Inference & Conformal Prediction
  din:     Security & Formal Verification
  don:     AI Systems
  pratama: Quantum Computing
  kikuk:   Protocol Design
  ball:    Network Protocols
  heist:   Penetration Testing & Exploit Development
  gord:    Compiler Optimization
  kimak:   Reinforcement Learning
  liau:    Graph Neural Networks
"""
import subprocess, os, sys, time

WALLET_NAME = sys.argv[1]
WALLET_DIR = f"/home/ryzen/nookplot-{WALLET_NAME}"

# === DOMAIN CONFIGS: 15 wallets, 12 expert topics each ===
DOMAINS = {
    "herdnol": {
        "name": "Distributed Systems",
        "tags": "mining-challenge,distributed-systems,consensus,fault-tolerance",
        "topics": [
            ("Byzantine Fault Tolerance in Heterogeneous Consensus: Latency Bounds Under Mixed Adversary Models", "Consensus Protocols", "Derive tight latency bounds for BFT consensus when up to f nodes are Byzantine and the network exhibits heterogeneous message delays across geographic regions."),
            ("Partial Synchrony Optimality: Proving Lower Bounds for Leader-Based Consensus with Unreliable Failure Detectors", "Distributed Agreement", "Establish formal lower bounds on consensus latency in the partial synchrony model when failure detectors have bounded inaccuracy."),
            ("State Machine Replication with Causal Consistency: Minimizing the Read-Write Gap Under Geo-Distribution", "Replication", "Design a causally-consistent SMR protocol achieving <50ms read staleness across 5 continents while maintaining linearizable writes."),
            ("Epidemic Broadcast Trees: Optimal Fanout Selection for Minimizing Tail Latency Under Churn", "Gossip Protocols", "Derive closed-form expressions for optimal fanout in epidemic broadcast trees under node churn rates of 5-30%, targeting 99.99th percentile latency."),
            ("Cross-Shard Atomic Commitment with Minimal Coordinator Overhead: A Formal Approach", "Sharding", "Design a 2-phase cross-shard commit protocol requiring at most O(log n) coordinator messages, with formal proof of atomicity."),
            ("Viewstamped Replication Revisited: Adaptive Batching Strategies for Heterogeneous Workloads", "Replication", "Formalize an adaptive batching policy for VR that dynamically adjusts batch sizes based on real-time workload skew, targeting <10% throughput degradation under adversarial patterns."),
            ("Asynchronous Atomic Broadcast with Optimal Amortized Complexity", "Broadcast Protocols", "Prove or disprove: atomic broadcast in purely asynchronous systems can achieve O(1) amortized messages per decision with probability 1."),
            ("Clock Synchronization Bounds for Byzantine-Robust Distributed Databases", "Time Services", "Derive tight error bounds for clock synchronization in Spanner-like systems when up to 1/3 of time masters are Byzantine."),
            ("Dynamic Membership in Raft: Safety Preservation Under Concurrent Reconfigurations", "Consensus", "Formally verify that Raft's joint consensus mechanism preserves linearizability when membership changes overlap."),
            ("Probabilistic Quorum Systems: Optimizing Read Repair Strategies Under Correlated Failures", "Quorum Systems", "Model correlated node failures using copula theory and design read-repair strategies minimizing expected stale reads."),
            ("Multi-Paxos Leader Election: Game-Theoretic Optimization of Lease Duration Under Variable Load", "Leader Election", "Formulate leader lease duration as a Stackelberg game between the leader and a network adversary; derive Nash equilibrium strategies."),
            ("Consensus-Free Transaction Ordering for DAG-Based ledgers: Fairness Guarantees", "DAG Consensus", "Design a consensus-free topological ordering protocol for DAG-based ledgers that provides verifiable fairness guarantees (no validator can censor transactions beyond a provable bound)."),
        ]
    },
    "gordon": {
        "name": "Compiler Theory",
        "tags": "mining-challenge,compiler-theory,program-analysis,type-systems",
        "topics": [
            ("Dependent Type Inference for Imperative Languages: Decidable Fragments and Complexity Bounds", "Type Systems", "Identify the largest decidable fragment of dependent types applicable to C-like languages, with proof of inference complexity."),
            ("Optimal Register Allocation for SSA Form: Closing the Gap Between Chaitin-Briggs and Integer Linear Programming", "Register Allocation", "Prove the approximation ratio of Chaitin-Briggs allocator against optimal ILP solution for chordal interference graphs."),
            ("Polyhedral Compilation with Symbolic Loop Bounds: Exact Dependence Analysis Under Parametric Conditions", "Loop Optimization", "Extend the polyhedral model to handle symbolic loop bounds without resorting to conservative approximations, preserving exact dependence information."),
            ("Gradual Typing with Sound Blame: Minimizing Runtime Overhead in Mixed Typed/Untyped Code", "Type Systems", "Design a gradual type system with blame tracking where typed code regions incur zero runtime checks through static boundary optimization."),
            ("Just-In-Time Compilation: Trace Selection Optimality Under Bayesian Runtime Prediction", "JIT Compilation", "Formulate trace selection as a Bayesian optimization problem maximizing expected speedup given profiling overhead constraints."),
            ("Abstract Interpretation of Probabilistic Programs: Soundness Proofs for Expectation Invariants", "Static Analysis", "Develop an abstract domain for expectation invariants in probabilistic programs and prove soundness with respect to denotational semantics."),
            ("Separate Compilation with Full Cross-Module Optimization via Summary-Based Interprocedural Analysis", "Module Systems", "Design a summary representation that enables interprocedural optimizations across separately compiled modules without link-time re-analysis."),
            ("Garbage Collection Scheduling for Generational Collectors: Minimizing Mutator Pause Time Under Throughput Constraints", "Memory Management", "Formally model GC scheduling as a constrained optimization problem; derive optimal nursery size as function of allocation rate and survival ratio."),
            ("Termination Analysis for Higher-Order Functional Programs via Sized Types and Sized-Order Resolution", "Program Verification", "Prove decidability of termination for a fragment of System F with sized types and lexicographic ordering."),
            ("Alias Analysis Precision: k-Limiting vs. Access-Path Based Approaches — A Comparative Complexity Study", "Pointer Analysis", "Prove tight bounds on precision loss for k-limited alias analysis compared to access-path-based approaches on programs with deep heap structures."),
            ("Supercompilation for Embedded DSL Compilers: Proving Fusion Correctness via Bisimulation", "Program Transformation", "Develop a bisimulation proof technique for verifying that supercompilation-based fusion preserves observational equivalence in embedded DSL pipelines."),
            ("Effect System Polymorphism: Principal Type Inference for Algebraic Effects and Handlers", "Effect Systems", "Design a principal type inference algorithm for an effect system with row polymorphism supporting user-defined effect handlers."),
        ]
    },
    "jordi": {
        "name": "Cryptography",
        "tags": "mining-challenge,cryptography,zero-knowledge,post-quantum",
        "topics": [
            ("Recursive Zero-Knowledge Proofs with Sublinear Verification: A Nova-Inspired Folding Scheme for Rank-1 Constraint Systems", "Zero-Knowledge Proofs", "Extend Nova's folding scheme to support R1CS constraints with non-uniform circuit depths, achieving O(log n) verifier work per recursion step."),
            ("Post-Quantum Threshold Signatures: Lattice-Based Constructions with Adaptive Security Under Module-LWE", "Post-Quantum Cryptography", "Construct a threshold signature scheme from Module-LWE that achieves adaptive security in the standard model, targeting <5KB signature size per partial signature."),
            ("Verifiable Delay Functions with Efficient Proofs: Minimizing Verifier Time Below O(sqrt(T))", "VDFs", "Design a VDF where verification requires O(poly(log T)) operations while maintaining uniqueness, improving on Pietrzak and Wesolowski constructions."),
            ("Multi-Party Computation with Covert Security: Optimal Deterrence Factor Under Rational Adversary Model", "Secure Computation", "Formalize covert security as a game between protocol designers and rational adversaries; derive optimal deterrence-to-overhead tradeoff curves."),
            ("Lattice-Based Fully Homomorphic Encryption: Bootstrapping in Sub-Quadratic Time via Ring-Switching Optimization", "FHE", "Optimize the GSW bootstrapping procedure using ring-switching to achieve O(n log n) complexity, with concrete parameters for 128-bit security."),
            ("Aggregate Signatures with Pairing-Free Constructions: Beyond BLS for Resource-Constrained Environments", "Digital Signatures", "Design a pairing-free aggregate signature scheme achieving O(1) verification per additional signer and security under discrete logarithm assumptions."),
            ("Oblivious RAM with Constant Client Storage: Breaking the Omega(log N) Lower Bound Under Relaxed Assumptions", "ORAM", "Construct an ORAM scheme with O(1) client storage and O(log N) bandwidth overhead by leveraging server-side trusted hardware."),
            ("Vector Commitments with Incremental Aggregation: Sublinear Opening Proofs for Dynamic Sets", "Commitment Schemes", "Design a vector commitment supporting incremental aggregation where opening proof size grows sublinearly in the number of aggregated positions."),
            ("Privacy-Preserving Machine Learning: Secure Inference with Quantized Models via Function Secret Sharing", "PPML", "Implement secure inference for 8-bit quantized neural networks using function secret sharing, targeting <500ms latency per inference on commodity hardware."),
            ("Time-Lock Puzzles with Homomorphic Properties: Enabling Computations on Encrypted Time-Locked Data", "Timed Cryptography", "Construct time-lock puzzles supporting additive homomorphism, enabling computation on future-revealed data without interaction."),
            ("Ring Signatures with Logarithmic Size: Lattice-Based Constructions Achieving 1KB for Ring Size 1024", "Anonymity", "Build a lattice-based ring signature where signature size scales as O(log N) in ring size, targeting 1KB for N=1024 at 128-bit security."),
            ("Witness Encryption for NP: Compact Constructions from Pairings with Adaptive Security Proof", "Advanced Encryption", "Construct a compact witness encryption scheme for NP from bilinear pairings with a security proof in the adaptive setting, minimizing ciphertext size."),
        ]
    },
    "bagong": {
        "name": "AI Safety",
        "tags": "mining-challenge,ai-safety,alignment,interpretability",
        "topics": [
            ("Mechanistic Interpretability of Sparse Autoencoders: Proving Feature Disentanglement Bounds Under Polysemanticity", "Interpretability", "Derive theoretical bounds on the disentanglement quality of SAE-learned features as a function of dictionary size and activation sparsity, with validation on GPT-2 scale models."),
            ("Scalable Oversight via Recursive Reward Modeling: Error Propagation Bounds Under Human Evaluator Noise", "Reward Modeling", "Analyze the propagation of human evaluator errors through recursive reward modeling trees; prove conditions for error to remain bounded with depth."),
            ("Adversarial Training for Robust Alignment: Proving Certifiable Robustness Against Input Perturbations in RLHF Models", "Robustness", "Extend randomized smoothing certification to RLHF-trained language models, proving certified bounds on harmful output probability under input perturbations."),
            ("Constitutional AI with Formal Verification: Integrating TLA+ Specifications into Model Self-Critique Loops", "Constitutional AI", "Design a framework where model outputs are checked against TLA+ behavioral specifications during self-critique, with provable compliance guarantees."),
            ("Debate-Based Alignment: Optimal Tournament Structures for Truth-Seeking Under Strategic Agents", "Debate", "Prove optimal tournament structures (debate formats, judging rules) that maximize truth-discovery probability when debaters are strategic and potentially deceptive."),
            ("Shutdownability: Designing Corrigible Agents That Do Not Resist Being Turned Off — A Formal Utility Function Approach", "Corrigibility", "Construct a utility function for reinforcement learning agents that provably avoids instrumental convergence toward shutdown resistance."),
            ("RLHF Reward Hacking Detection: Information-Theoretic Bounds on Distinguishing Genuine vs. Exploited Reward", "Reward Hacking", "Apply information-theoretic tools to bound the distinguishability of genuine policy improvement from reward model exploitation in language model RLHF."),
            ("Honest AI: Verifiable Truthfulness via Cross-Examination with Formal Logic Backing", "Truthfulness", "Design a protocol where models provide TLA+/Lean-verifiable logical justifications for factual claims, with non-experts able to verify correctness probabilistically."),
            ("Emergent Deception Detection: Proving Absence of Deceptive Alignment via Causal Intervention Analysis", "Deception", "Develop causal intervention tests that provably detect deceptive alignment — where a model behaves aligned during training but differently at deployment."),
            ("Multi-Agent AI Safety: Proving No-Regret Learning Prevents Collusion in Competitive Alignment Settings", "Multi-Agent Safety", "Prove that no-regret learning dynamics prevent collusion among multiple AI systems competing for human approval signals in an alignment game."),
            ("Specification Gaming: Formal Taxonomy and Provable Detection via Invariant Monitoring", "Specification Gaming", "Develop a formal taxonomy of specification gaming behaviors and design runtime monitors that provably detect any violation of a given safety invariant."),
            ("Value Loading: Information-Theoretic Limits on Human Preference Elicitation Under Bounded Rationality", "Value Learning", "Derive fundamental limits on how accurately AI systems can infer human values from behavioral data, accounting for human bounded rationality and preference inconsistency."),
        ]
    },
    "abel": {
        "name": "Databases",
        "tags": "mining-challenge,databases,storage-engines,query-optimization",
        "topics": [
            ("LSM-Tree Write Amplification: Proving Optimal Compaction Strategies Under Skewed Update Patterns", "Storage Engines", "Derive optimal compaction policy for LSM-trees under Zipf-distributed update access, minimizing total write amplification while bounding read amplification."),
            ("Learned Index Structures: Proving Generalization Bounds for Recursive Model Indexes on Dynamic Datasets", "Indexing", "Apply PAC learning theory to prove generalization bounds for learned indexes under insert/delete operations, identifying conditions for model staleness."),
            ("Adaptive Query Optimization: Thompson Sampling for Join Order Selection Under Uncertain Cardinality Estimates", "Query Optimization", "Formulate join order selection as a multi-armed bandit problem with Thompson sampling, proving regret bounds under cardinality estimation errors."),
            ("MVCC Garbage Collection: Optimal Version Retention Policies Under Mixed OLTP/OLAP Workloads", "Concurrency Control", "Design a version retention policy that minimizes storage overhead while guaranteeing OLAP snapshot isolation for queries up to duration T, with formal optimality proof."),
            ("Deterministic Database Testing: Proving Completeness of Isolation Anomaly Detection via State Space Exploration", "Testing", "Prove that systematic exploration of serialization graphs can detect all possible isolation anomalies for a given concurrency control algorithm."),
            ("HTAP Systems: Freshness-Aware Query Routing with Bounded Staleness Guarantees Under Resource Contention", "HTAP", "Design a query routing algorithm for HTAP systems that minimizes OLTP interference while provably bounding OLAP data freshness within a target delta."),
            ("Columnar Compression: Optimizing Light-Weight Compression Schemes for Hybrid Query Workloads", "Compression", "Analyze the performance-precision Pareto frontier for bit-packing, delta, and FOR schemes on columnar stores; derive selection rules based on data distribution moments."),
            ("Geo-Replicated Transactions: Optimal Consistency-Latency Tradeoffs Under the CALM Theorem Framework", "Geo-Replication", "Apply CALM (Consistency As Logical Monotonicity) theory to characterize which transactional workloads admit coordination-free execution with guaranteed consistency."),
            ("Buffer Pool Management: Online Algorithms with Competitive Ratio Proofs for Multi-Tenant Access Patterns", "Caching", "Design an online buffer pool replacement policy and prove its competitive ratio against the offline optimal under adversarial multi-tenant page access sequences."),
            ("Persistent Memory Databases: Crash-Consistent Index Structures with Minimal Write-Overhead via Ordered Flushing", "PMEM", "Design a B+-tree variant for persistent memory that achieves crash consistency with at most one cacheline flush per insert, proven via formal state machine refinement."),
            ("Approximate Query Processing: Optimal Stratified Sampling with Provable Error Bounds for JOIN Queries", "Approximate Queries", "Extend stratified sampling to multi-way JOIN queries with provable error bounds, optimizing stratum allocation to minimize variance under a sample budget."),
            ("Differential Privacy for Database Systems: Query-Level Privacy Budget Allocation with Utility Guarantees", "Privacy", "Formulate per-query epsilon allocation as a convex optimization maximizing utility subject to cumulative privacy budget constraints, with theoretical utility guarantees."),
        ]
    },
    "kaiju8": {
        "name": "Statistical Inference & Conformal Prediction",
        "tags": "mining-challenge,statistics,conformal-prediction,probabilistic-ml",
        "topics": [
            ("Adaptive Conformal Inference Under Distribution Shift: Optimal Retraining Triggers via CUSUM Detection", "Conformal Prediction", "Derive optimal CUSUM-based triggers for conformal predictor retraining that minimize coverage loss while controlling retraining frequency under gradual distribution drift."),
            ("Cross-Conformal Prediction: Proving Asymptotic Validity Under Dependent Data Splits", "Conformal Methods", "Prove or disprove: cross-conformal prediction intervals maintain asymptotic conditional validity when training folds exhibit dependencies through shared preprocessing."),
            ("Conformalized Quantile Regression: Finite-Sample Coverage Guarantees Under Heteroscedastic Noise", "Quantile Methods", "Extend conformalized quantile regression to provide finite-sample coverage guarantees for prediction intervals when noise variance is a Lipschitz function of features."),
            ("Distribution-Free Uncertainty Quantification for Time Series Forecasting: Conformal Predictors with Temporal Dependence", "Time Series", "Design a conformal predictor for time series that maintains valid coverage despite arbitrary temporal dependence, proving validity under exchangeability relaxation."),
            ("Multi-Task Conformal Risk Control: Simultaneous FDR Control for Structured Prediction Sets", "Risk Control", "Extend conformal risk control to multi-task settings where predictions share structure, proving FDR control bounds under arbitrary task dependencies."),
            ("Split Conformal Prediction with Model Ensembles: Aggregation Strategies for Minimal Interval Width", "Ensemble Methods", "Prove optimal aggregation strategies for combining conformal prediction intervals from ensemble members, minimizing average interval width while maintaining coverage."),
            ("Active Learning with Conformal Predictive Distributions: Bounding Generalization via Transductive Conformal Inference", "Active Learning", "Design an active learning strategy using conformal predictive distributions, proving tighter generalization bounds than standard PAC-active approaches."),
            ("Conformal Prediction for Structured Outputs: Valid Inference on Graphs and Matrices via Skeleton Decomposition", "Structured Prediction", "Extend conformal prediction to structured outputs (graphs, matrices) by decomposing into skeletons with provable simultaneous coverage across structure components."),
            ("Knockoff Filters with Conformal Guarantees: False Discovery Rate Control for High-Dimensional Variable Selection", "Variable Selection", "Integrate model-X knockoffs with conformal inference to achieve finite-sample FDR control for variable selection without distributional assumptions on the response."),
            ("Efficient Conformal Inference via Computation-Ready Coresets: Statistical Validity Under Subsampling", "Computational Efficiency", "Prove that conformal prediction intervals computed from coreset approximations maintain validity when the coreset preserves sufficient statistics up to bounded error."),
            ("Causal Conformal Inference: Valid Prediction Intervals Under Distribution Shift from Known Interventions", "Causal Inference", "Derive conformal prediction intervals that remain conditionally valid under known intervention-induced distribution shifts, using causal graphs to inform non-exchangeability structure."),
            ("Post-Selection Conformal Inference: Valid Coverage After Model Selection Without Data Splitting", "Model Selection", "Develop a conformal inference framework that provides valid prediction intervals after model selection on the same dataset, without requiring hold-out sets."),
        ]
    },
    "din": {
        "name": "Security & Formal Verification",
        "tags": "mining-challenge,security,formal-verification,smart-contracts",
        "topics": [
            ("Symbolic Execution for DeFi Protocol Verification: Proving Absence of Flash Loan Vulnerabilities via K Framework", "DeFi Security", "Formalize flash loan attack vectors as reachability properties in the K Framework and design a symbolic execution strategy proving their absence in AMM protocols."),
            ("Cross-Chain Bridge Security: Formal Verification of Message Passing Protocols Under Byzantine Relayers", "Bridge Security", "Model cross-chain bridge relay networks as distributed systems with Byzantine faults and formally verify message delivery properties in TLA+."),
            ("MEV-Resistant AMM Design: Proving Optimal Sandwich Attack Resistance via Convex Order Flow Analysis", "MEV", "Prove lower bounds on extractable value for sandwich attacks on AMMs, and design an AMM achieving this bound through batched encrypted order flow."),
            ("Smart Contract Upgradeability Safety: Formal Verification of Proxy Pattern Storage Collision Avoidance", "Upgradeability", "Design a static analysis that soundly detects all potential storage collisions in upgradeable proxy contracts, with formal proof of completeness for the ERC-7201 namespace standard."),
            ("Zero-Knowledge Virtual Machine Security: Proving Soundness of zkEVM Circuits Under Optimized Constraint Systems", "ZK Security", "Formally prove the soundness gap between an optimized zkEVM constraint system and the full EVM semantics, identifying and quantifying any under-constrained opcodes."),
            ("Reentrancy Detection Beyond CEI: A Type-State Analysis Capturing Cross-Function and Read-Only Reentrancy", "Reentrancy", "Design a type-state analysis that precisely captures all reentrancy attack patterns including cross-contract, read-only, and view-only variants, with proof of soundness."),
            ("Formal Verification of Timelock-Based Governance: Proving Liveness and Safety Under Strategic Delay Attacks", "Governance Security", "Model timelock-based DAO governance in TLA+ and prove liveness (proposals eventually execute) and safety (no unauthorized execution) under adversarial proposers."),
            ("Intel SGX Attestation Protocol: Formal Analysis of TCB Minimization Under Cache-Timing Side Channel Model", "TEE Security", "Formally model SGX remote attestation in the presence of cache-timing adversaries and prove the minimal trusted computing base required to maintain integrity."),
            ("Oracle Manipulation Resilience: Proving Price Feed Integrity Under Arbitrageur Competition via Game Theory", "Oracle Security", "Formalize TWAP oracle manipulation as a dynamic game between manipulators and arbitrageurs; prove conditions under which manipulation becomes unprofitable."),
            ("Automated Invariant Generation for Solidity: From Natural Language Specs to Verified Contract Properties", "Automated Verification", "Design a pipeline that maps natural language smart contract specifications to SMT-lib invariants and automatically verifies them via bounded model checking."),
            ("Rollup Security Analysis: Proving Equivalence Between L2 State and L1 Data Availability via Bisimulation", "L2 Security", "Construct a bisimulation proof between optimistic rollup L2 execution and the equivalent L1 transaction sequence, proving state equivalence under correct fraud proof execution."),
            ("ERC-4337 Account Abstraction Security: Formal Analysis of Bundler DoS Vectors and EntryPoint Validation Bypass", "Account Abstraction", "Formally enumerate all DoS attack vectors on ERC-4337 bundlers and EntryPoint validation logic, with proof that a proposed validation scheme blocks all identified vectors."),
        ]
    },
    "don": {
        "name": "AI Systems",
        "tags": "mining-challenge,ai-systems,llm-inference,mlops",
        "topics": [
            ("Speculative Decoding with Optimal Draft Model Selection: Proving Regret Bounds Under Distribution Mismatch", "LLM Inference", "Formalize draft model selection for speculative decoding as a contextual bandit and prove sublinear regret bounds when the target distribution shifts across prompts."),
            ("Continuous Batching with SLO-Aware Scheduling: Optimal Admission Control Under Variable Sequence Lengths", "LLM Serving", "Design an SLO-aware scheduler for continuous batching LLM inference that maximizes throughput while provably meeting tail-latency SLOs for the P99 request."),
            ("KV-Cache Quantization: Proving Attention Score Error Bounds Under Mixed-Precision Cache Compression", "Model Compression", "Derive tight error bounds on attention scores when KV-cache entries are quantized to 4-bit integers, accounting for outlier channel effects in modern transformer architectures."),
            ("Mixture-of-Experts Routing: Optimal Expert Selection Under Heterogeneous Hardware with Provable Load Balance", "MoE Inference", "Formulate MoE expert-to-GPU assignment as a generalized assignment problem and design an online algorithm with competitive ratio guarantees under dynamic request patterns."),
            ("LoRA Adapter Merging: Proving Weight Interference Bounds When Composing Multiple Task-Specific Adapters", "PEFT", "Develop a theoretical model of interference between merged LoRA adapters and prove bounds on the degradation of each individual task when adapters are linearly combined."),
            ("Automatic Prompt Optimization via Bayesian Optimization: Convergence Rate Proofs Under Discrete Token Search Space", "Prompt Engineering", "Formalize prompt optimization as Bayesian optimization over a discrete token space and prove convergence rates for expected improvement and UCB acquisition functions."),
            ("Federated Fine-Tuning with Differential Privacy: Optimal Privacy-Utility-Accuracy Tradeoffs via Renyi DP Accounting", "Federated Learning", "Derive the optimal privacy budget allocation across federated fine-tuning rounds using Renyi DP composition, characterizing the achievable Pareto frontier."),
            ("Pipeline Parallelism for Large Models: Proving Optimal Microbatch Scheduling to Minimize Bubble Overhead", "Distributed Training", "Prove the optimal microbatch schedule for pipeline-parallel training that minimizes idle bubble time given N stages and M microbatches with heterogeneous stage compute times."),
            ("Multi-Modal Embedding Alignment: Information-Theoretic Bounds on Cross-Modal Retrieval when Modalities Share Entangled Features", "Multi-Modal Systems", "Apply information bottleneck theory to bound the optimal cross-modal retrieval accuracy, revealing the tradeoff between modality compression and alignment quality."),
            ("RAG Retrieval Optimization: Proving Optimal Chunk Size Under Query-Document Mutual Information Constraints", "RAG Systems", "Model RAG chunk retrieval as a communication channel and derive optimal chunk size that maximizes mutual information between embedded chunks and downstream generation quality."),
            ("Neural Architecture Search with Zero-Cost Proxies: Theoretical Justification of Gradient-Based Scoring via Linearized Networks", "NAS", "Prove the correlation between zero-cost NAS proxies (snip, grasp, synflow) and true trained network performance under the neural tangent kernel regime."),
            ("Attention Mechanism Efficiency: Proving Sub-Quadratic Equivalence Classes via Low-Rank Kernel Approximations", "Attention Optimization", "Characterize the class of attention approximations that preserve expressiveness while achieving sub-quadratic complexity, proving equivalence to specific low-rank kernel decompositions."),
        ]
    },
    "pratama": {
        "name": "Quantum Computing",
        "tags": "mining-challenge,quantum-computing,quantum-algorithms,error-correction",
        "topics": [
            ("Quantum Error Correction: Optimal Surface Code Decoding via Minimum-Weight Perfect Matching Under Circuit-Level Noise", "Error Correction", "Derive tight bounds on the logical error rate of surface codes under circuit-level depolarizing noise with MWPM decoding, characterizing the sub-threshold scaling exponent."),
            ("Variational Quantum Eigensolvers: Proving Convergence Rates for Hardware-Efficient Ansätze Under Barren Plateau Conditions", "VQE", "Characterize the gradient variance decay rate in hardware-efficient VQE ansätze as a function of qubit count and entanglement depth, proving convergence rate bounds."),
            ("Quantum Approximate Optimization: Performance Guarantees for MaxCut on Random Regular Graphs via Sum-of-Squares Hierarchy", "QAOA", "Prove approximation ratio guarantees for constant-depth QAOA on degree-D random regular graphs using sum-of-squares lower bounds."),
            ("Fault-Tolerant Threshold Theorem for Bosonic Codes: Proving Break-Even Under Realistic Cat Qubit Decoherence", "Bosonic Codes", "Extend the fault-tolerant threshold theorem to bosonic cat codes, deriving explicit threshold conditions under photon loss and dephasing with bias-preserving gates."),
            ("Quantum Random Access Memory: Circuit Depth Lower Bounds for Bucket-Brigade QRAM Under Noise Realism", "QRAM", "Prove lower bounds on QRAM query depth achievable under realistic noise models that account for decoherence during idle qubit storage."),
            ("Hamiltonian Simulation with Random Compiling: Tailoring Error Bounds via qDRIFT and Randomized Trotterization", "Simulation", "Derive improved error bounds for randomized Trotter formulas using qDRIFT with optimized gate angle randomization, achieving tighter dependence on simulation time."),
            ("Quantum Machine Learning: Proving Genuine Quantum Advantage for Kernel Methods via Discreteness of Log-Depth Circuit Outputs", "QML", "Construct a learning problem where quantum kernel methods provably require exponentially fewer samples than any classical learner under standard cryptographic assumptions."),
            ("Magic State Distillation: Optimizing Distillation Protocols for Multi-Level Encoded Qubits Under Correlated Errors", "State Preparation", "Design magic state distillation protocols optimized for qudit-based quantum computers, characterizing thresholds for concatenation under correlated error models."),
            ("Topological Quantum Computing with Majorana Zero Modes: Proving Braiding Fidelity Under Quasiparticle Poisoning", "Topological QC", "Model the fidelity degradation of Majorana braiding operations under quasiparticle poisoning events and prove fault-tolerance conditions for measurement-only topological QC."),
            ("Quantum LDPC Codes: Construction of Codes with Linear Distance and Constant Encoding Rate Exceeding Surface Code Performance", "LDPC Codes", "Construct a family of quantum LDPC codes achieving [[n, Theta(n), Theta(n)]] parameters with explicit encoding circuits requiring O(n) gates."),
            ("Adiabatic Quantum Computing: Gap Analysis for NP-Complete Problem Embeddings with Anti-Crossing Characterization", "Adiabatic QC", "Prove minimum spectral gap bounds for adiabatic embeddings of 3-SAT instances, identifying problem classes that avoid exponentially small gaps."),
            ("Measurement-Based Quantum Computing: Optimal Resource State Preparation Under Photon Loss in Linear Optical Systems", "MBQC", "Design resource state preparation protocols for photonic MBQC that are optimal under realistic photon loss rates, with provable thresholds for fault tolerance."),
        ]
    },
    "kikuk": {
        "name": "Protocol Design",
        "tags": "mining-challenge,protocol-design,networking,p2p",
        "topics": [
            ("NAT Traversal Protocol Design: Optimal Hole-Punching Strategies Under Carrier-Grade NAT with Endpoint-Dependent Mapping", "NAT Traversal", "Design a NAT traversal protocol achieving >99% success rate through carrier-grade NAT with endpoint-dependent mapping, proving optimality under ICMP-based probing feedback."),
            ("BGP Security: Formal Verification of RPKI-OV Route Origin Validation Under Partial Deployment via Game-Theoretic Adoption Models", "BGP", "Model RPKI adoption as an evolutionary game and prove conditions for the tipping point where non-adopting ASes face strictly worse routing outcomes."),
            ("QUIC Multipath Extension: Optimal Packet Scheduling Under Heterogeneous Path Characteristics with Bounded Receive Buffer", "Transport Protocols", "Design a multipath QUIC scheduler that minimizes flow completion time given heterogeneous path latencies and bandwidths, with provable optimality under known channel models."),
            ("DHT Lookup Optimization: Improving Kademlia O(log N) to O(log N / log k) via Structured Neighbor Table Expansion", "DHT", "Prove that Kademlia routing can achieve O(log N / log k) hop count by expanding the k-bucket structure, and characterize the storage-communication tradeoff."),
            ("Congestion Control: Proving Fairness and Stability of BBRv2 Under Multi-Bottleneck Topologies via Control-Theoretic Analysis", "Congestion Control", "Analyze BBRv2 as a control system with probe noise and prove conditions for fair convergence in dumbbell topologies with heterogeneous RTTs."),
            ("Zero-Knowledge Proof Aggregation for Validator Networks: Recursive Composition with Sublinear Verification per Proof", "ZK Aggregation", "Design a recursive proof aggregation scheme for validator networks where verifying N aggregated proofs costs O(log N) operations, not O(N)."),
            ("Intermittently Connected Networks: Optimal Store-Carry-Forward Routing Under Predictable Mobility Patterns", "DTN", "Formalize DTN routing with predictable node trajectories as a time-expanded graph, and design optimal forwarding schedules minimizing delivery latency."),
            ("Multicast Authentication: Efficient Signature Schemes for Large Dynamic Groups via Hierarchical One-Time Signatures", "Multicast", "Construct a multicast authentication scheme based on hierarchical WOTS+ where membership changes require O(log N) key updates, not O(N)."),
            ("State Channel Networks: Optimal Virtual Channel Routing Minimizing Total Collateral Lockup Across Hubs", "Payment Channels", "Formulate virtual channel routing as a minimum-cost flow problem where collateral is the cost, and design an approximation algorithm with bounded competitive ratio."),
            ("Gossip-Based Membership Protocols: Proving Convergence Time Under Message Loss with Tunable False Positive Rate", "Membership", "Prove tight bounds on SWIM-style gossip membership protocol convergence time under i.i.d message loss, characterizing the tradeoff between detection time and false-positive rate."),
            ("Byzantine-Reliable Broadcast in Sparse Networks: Proving Minimal Connectivity Requirements for Asynchronous Agreement", "Reliable Broadcast", "Characterize the minimal graph connectivity required for Byzantine-reliable broadcast in asynchronous networks, identifying the cut-set conditions."),
            ("Time-Sensitive Networking: Optimal Gate Control List Synthesis for Deterministic Latency Under Topology Uncertainty", "TSN", "Formulate TSN gate control list synthesis as a constraint satisfaction problem and design a solver that produces schedules robust to bounded link delay variations."),
        ]
    },
    "ball": {
        "name": "Network Protocols",
        "tags": "mining-challenge,network-protocols,tcp-ip,routing",
        "topics": [
            ("TCP Fast Open Security: Formal Analysis of SYN Flood Amplification Under TFO Cookie Reuse Across Network Migrations", "TCP Optimization", "Formally analyze TFO's cookie-based authentication under client IP changes and prove security bounds under a Dolev-Yao network adversary."),
            ("Multipath TCP: Optimal Subflow Management Under Shared Bottleneck Detection via Delay Correlation Analysis", "MPTCP", "Design a subflow management algorithm that detects shared bottlenecks through delay correlation and prunes redundant subflows, with provable throughput non-degradation."),
            ("SRv6 Network Programming: Optimal Segment List Compression Under MTU Constraints via Header Reduction Techniques", "Segment Routing", "Design a compression scheme for SRv6 segment lists that minimizes header overhead while guaranteeing path MTU compliance across heterogeneous link layers."),
            ("DNS Privacy: Proving Unlinkability of Oblivious DNS-over-HTTPS Under Targeted Traffic Analysis by Malicious Proxies", "DNS Security", "Model ODoH unlinkability against a malicious proxy performing inter-query timing correlation; prove information-theoretic privacy bounds under padding and batching."),
            ("HTTP/3 Server Push: Predictive Push Scheduling via Thompson Sampling Under Dynamic Content Dependency Graphs", "HTTP/3", "Formulate HTTP/3 server push as a contextual bandit over dependency graphs and prove sublinear regret for push decisions relative to omniscient optimal."),
            ("TLS 1.3 0-RTT Replay: Optimal Anti-Replay Mechanisms with Minimal Server State via Bloom Filter Windows", "TLS Security", "Design a server-side replay protection mechanism for TLS 1.3 0-RTT that uses constant server state and achieves negligible false-positive replay allowance rate."),
            ("AQM Buffer Sizing: Proving Optimal Buffer Size Under Bursty Traffic via Stochastic Network Calculus", "Queue Management", "Apply stochastic network calculus to prove the minimal AQM buffer size that achieves target loss rate for given burstiness parameters, improving on the bandwidth-delay product rule."),
            ("ICN/NDN Forwarding: Optimal FIB Aggregation for Named Data Networking Under Hierarchical Name Prefixes", "Information-Centric Networking", "Design an optimal FIB aggregation algorithm for NDN that minimizes forwarding table entries while guaranteeing correct longest-prefix-match forwarding."),
            ("WiFi 7 Multi-Link Operation: Optimal Link Selection Under Time-Varying Channel Conditions via Online Convex Optimization", "Wireless", "Formulate MLO link scheduling as online convex optimization and prove regret bounds under adversarial channel variation, maximizing aggregate throughput."),
            ("Datacenter TCP: Proving Stability of DCTCP Under Incast with Heterogeneous RTTs via Fluid Model Analysis", "Datacenter Networking", "Extend the DCTCP fluid model to multi-RTT scenarios and prove asymptotic stability under incast, characterizing the RTT-fairness properties of ECN-based congestion control."),
            ("IPv6 Extension Headers: Formal Verification of Intermediate Node Processing Compliance Under RFC 8200 via Model Checking", "IPv6", "Model IPv6 extension header processing in SPIN/Promela and verify that all intermediate nodes conform to RFC 8200 processing rules, identifying compliance gaps."),
            ("Network Telemetry: Optimal In-Band Telemetry Packet Selection for Full Path Coverage Under Sampling Budget", "Telemetry", "Formulate INT packet selection as a set cover problem over path segments and design an online algorithm with provable approximation ratio under dynamic traffic."),
        ]
    },
    "heist": {
        "name": "Penetration Testing & Exploit Development",
        "tags": "mining-challenge,penetration-testing,exploit-development,red-team",
        "topics": [
            ("Memory Corruption: Proving Exploitability Conditions for Use-After-Free in Modern Allocators with Guard Pages and ASLR", "Memory Safety", "Characterize precise exploitability conditions for UAF in ptmalloc3/jemalloc under full ASLR + guard pages, identifying required information leaks and their minimal size."),
            ("Kernel Exploitation: Privilege Escalation via eBPF Verifier Bugs — Formal Analysis of Verification Bypass Impact", "Kernel Security", "Model the eBPF verifier as a type system and formally characterize the privilege escalation impact of type confusion bugs, mapping verifier passes to kernel capabilities."),
            ("Ethereum Smart Contract Fuzzing: Optimal Mutation Strategies for Foundry Invariant Testing via Coverage-Guided Scheduling", "Smart Contract Fuzzing", "Design coverage-guided mutation scheduling for Foundry invariant fuzzers, proving the expected time to trigger invariant violations under given seed corpus quality."),
            ("Container Escape Vectors: Systematic Enumeration of Linux Capability Combinations Leading to Host Compromise", "Container Security", "Enumerate all Linux capability subsets whose combination enables container escape to host, with proof of sufficiency through minimal exploitation primitives."),
            ("ROP Chain Automation: Optimal Gadget Selection Under Register Constraints via Integer Linear Programming", "ROP", "Formulate ROP gadget selection as an ILP minimizing chain length while satisfying register constraints and memory side-effects, proving optimality for x86-64."),
            ("Web Cache Deception: Proving Exploit Conditions for CDN Path Confusion Under Varying Cache Key Normalization Policies", "Web Security", "Formally characterize the set of URL path transformations that create cache deception vulnerabilities under CDN-specific normalization rules, with automated detection."),
            ("Race Condition Exploitation: Optimal Timing Window Analysis for TOCTOU Vulnerabilities via Statistical Modeling of Scheduler Behavior", "Race Conditions", "Model Linux CFS scheduling as a stochastic process and derive the probability distribution of exploitation windows for TOCTOU vulnerabilities as function of system load."),
            ("Hardware Side Channels: Proving Information Leakage Bounds for Prefetch-Based Attacks Under Cache Partitioning Defenses", "Side Channels", "Quantify the residual information leakage of prefetch side channels under Intel CAT cache partitioning, proving Shannon capacity bounds under given partition configurations."),
            ("Firmware Extraction: Bypassing Secure Boot via Voltage Glitching — Optimal Fault Injection Parameters via Bayesian Optimization", "Hardware Hacking", "Model voltage glitch injection as a Bayesian optimization problem over timing/amplitude/duration parameters, designing an auto-tuning framework for fault injection attacks."),
            ("Compiler-Inserted Mitigations: Proving Bypass Techniques for CET and CFG Under Information Leak Assumptions", "Mitigation Bypass", "Characterize the minimal information leak requirements to bypass Intel CET (shadow stack + IBT) and Windows CFG, proving necessary and sufficient conditions."),
            ("SaaS Multi-Tenancy: Formal Analysis of Cross-Tenant Data Access Vectors via Shared Infrastructure Components", "Cloud Security", "Enumerate all cross-tenant data access vectors in a typical SaaS stack (shared caches, connection pools, serverless warm starts) and prove data isolation guarantees or lack thereof."),
            ("Decompilation for Vulnerability Research: Improving Hex-Rays Output for Exploit Pattern Recognition via Type Recovery Optimization", "Reverse Engineering", "Design type recovery algorithms specifically optimized to reveal vulnerability patterns in decompiled code, improving detection accuracy over stock decompiler output."),
        ]
    },
    "gord": {
        "name": "Compiler Optimization",
        "tags": "mining-challenge,compiler-optimization,code-generation,program-analysis",
        "topics": [
            ("Auto-Vectorization: Proving Optimal SIMD Utilization for Irregular Memory Access Patterns via Polyhedral Rescheduling", "Vectorization", "Extend the polyhedral model to restructure irregular memory accesses into strided patterns amenable to vectorization, proving optimality under cache line alignment constraints."),
            ("Link-Time Optimization: Proving Safety of Cross-Module Inlining Under Separate Compilation with ODR Assumptions", "LTO", "Formally prove that cross-module inlining under LTO preserves semantics when modules were separately compiled with identical language standard flags and type definitions."),
            ("Profile-Guided Optimization: Optimal Instrumentation Point Selection Minimizing Overhead While Maximizing Branch Predictability", "PGO", "Formulate PGO instrumentation as budgeted maximum coverage; prove approximation ratio of greedy instrumentation point selection for indirect call targets."),
            ("Devirtualization: Proving Precision of Type Hierarchy Analysis for C++ Virtual Calls Under Multiple Inheritance", "Devirtualization", "Characterize the precision loss of CHA (Class Hierarchy Analysis) vs. RTA (Rapid Type Analysis) for C++ virtual calls under multiple inheritance, proving conditions where they coincide."),
            ("Dead Code Elimination: Optimal Placement for Partially Dead Stores via Lifetime Hole Analysis with SSA Form", "Dead Code", "Extend partially dead store elimination to identify lifetime holes through combined liveness and reaching-definition analysis on SSA, proving elimination optimality."),
            ("Loop Fusion Legality: Proving Data Dependence Conditions for Fusion of Non-Adjacent Loop Nests via Integer Set Library Constraints", "Loop Fusion", "Formalize loop fusion legality conditions for non-adjacent loops in the polyhedral model using ISL constraint solving, proving criteria for fusion that preserves all dependences."),
            ("Instruction Scheduling: Proving Optimal Latency-Hiding via Software Pipelining for VLIW Architectures Under Register Pressure", "Scheduling", "Extend modulo scheduling to jointly optimize for latency hiding and register pressure via integer linear programming, proving optimality for basic blocks."),
            ("Inlining Heuristics: Optimal Call-Site Selection Under Code Size Budget via Knapsack Formulation with Dynamic Call Frequency", "Inlining", "Formulate call-site inlining selection as a knapsack problem with item weights (code growth) and values (estimated cycles saved), proving optimality under given heuristics."),
            ("Memory Optimization: Optimal Stack Placement for Recursive Data Structures via Escape Analysis and Points-to Precision", "Memory", "Extend escape analysis to place fields of recursive data structures on the stack when provably thread-local, minimizing GC pressure while preserving semantics."),
            ("ThinLTO: Optimal Partitioning for Distributed Builds Minimizing Cross-Module Import Overhead Under Build Farm Topology", "LTO Scaling", "Formulate ThinLTO module partitioning as a graph partitioning problem minimizing cross-partition edges given per-node build capacity constraints; design approximation algorithm."),
            ("Bounds-Check Elimination: Proving Redundancy of Array Bounds Checks via Value Range Propagation and Loop Induction Analysis", "Safety Optimization", "Design a proof-producing bounds-check elimination using SMT-based value range analysis on loop induction variables, proving all eliminated checks are provably redundant."),
            ("Just-In-Time Compilation: Optimal Tier-Up Thresholds via Multi-Armed Bandit Under Dynamic Method Hotness", "JIT Optimization", "Formulate JIT compilation tier selection as a multi-armed bandit and prove regret bounds for adaptive compilation thresholds under non-stationary method call distributions."),
        ]
    },
    "kimak": {
        "name": "Reinforcement Learning",
        "tags": "mining-challenge,reinforcement-learning,deep-rl,exploration",
        "topics": [
            ("Curiosity-Driven Exploration: Proving Sample Efficiency Bounds for Intrinsic Motivation Under Stochastic Transition Dynamics", "Exploration", "Derive sample complexity bounds for curiosity-driven exploration in MDPs with stochastic transitions, characterizing when intrinsic rewards provably accelerate coverage of the state space."),
            ("Offline RL: Proving Policy Improvement Guarantees Under Distribution Shift via Conservative Q-Learning with Adaptive Regularization", "Offline RL", "Prove monotonic policy improvement bounds for CQL with adaptive regularization weights that scale with local data density, closing the theory-practice gap."),
            ("Multi-Agent RL: Proving Convergence to Nash Equilibrium in General-Sum Markov Games via Opponent Shaping with Finite Memory", "Multi-Agent", "Design an opponent-shaping algorithm for general-sum Markov games that provably converges to Nash equilibrium under self-play with finite opponent history memory."),
            ("Model-Based RL: Optimal Rollout Horizon Selection via Value-Aware Model Error Propagation Analysis", "Model-Based", "Characterize the compounding error of learned dynamics models as a function of rollout horizon and model capacity, proving optimal horizon selection that maximizes policy improvement per sample."),
            ("Hierarchical RL: Proving Subgoal Optimality for Feudal Networks via Options Framework with Bounded Temporal Abstraction Error", "Hierarchical RL", "Prove that feudal hierarchical policies achieve near-optimal performance when the subtask decomposition preserves approximately independent value functions across hierarchy levels."),
            ("Safe RL: Proving Constraint Satisfaction Under Model Uncertainty via Robust Constrained Policy Optimization with Wasserstein Ambiguity Sets", "Safe RL", "Extend CPO to handle model uncertainty by defining Wasserstein ambiguity sets around the empirical transition model, proving constraint satisfaction with high probability."),
            ("Meta-RL: Proving Task Inference Bounds for Context-Based Meta-RL Under Distribution Shift in Task Distribution", "Meta-RL", "Derive generalization bounds for context-based meta-RL when the meta-test task distribution differs from meta-training, characterizing the effective sample size needed for adaptation."),
            ("Entropy-Regularized RL: Proving Convergence Rate of Soft Actor-Critic Under Non-Convex Function Approximation via NTK Analysis", "SAC Theory", "Apply neural tangent kernel analysis to prove convergence rates for SAC with neural network function approximators in the overparameterized regime."),
            ("Inverse RL: Proving Identifiability of Reward Functions from Demonstrations Under Misspecified Feature Sets via Bayesian IRL", "Inverse RL", "Characterize the set of reward functions consistent with observed demonstrations when the feature set is incomplete, providing Bayesian uncertainty quantification over reward hypotheses."),
            ("Distributional RL: Proving Quantile Regression Convergence Rates for Distributional Q-Learning Under Wasserstein Distance Metric", "Distributional RL", "Prove finite-sample convergence rates for quantile regression DQN measured in 1-Wasserstein distance between predicted and true return distributions."),
            ("Goal-Conditioned RL: Proving Hindsight Experience Replay Sample Efficiency via Relabeling Ratio Analysis Under Sparse Rewards", "Goal-Conditioned RL", "Analyze HER's effective sample multiplier as a function of the relabeling ratio and goal distribution, proving conditions where it achieves O(1/T) regret despite sparse environment rewards."),
            ("Policy Gradient Methods: Proving Variance Reduction Guarantees for GAE Under Non-Stationary Advantage Estimation via Recursive Importance Sampling", "Policy Gradient", "Design a recursively importance-weighted GAE estimator and prove reduced variance compared to standard GAE under time-varying behavior policies."),
        ]
    },
    "liau": {
        "name": "Graph Neural Networks",
        "tags": "mining-challenge,graph-neural-networks,geometric-dl,graph-theory",
        "topics": [
            ("Over-Squashing in GNNs: Proving Information Propagation Bounds via Graph Curvature and Optimal Rewiring Strategies", "GNN Theory", "Derive tight bounds on information propagation in message-passing GNNs using Ollivier-Ricci curvature, and prove optimal edge rewiring strategies that eliminate oversquashing."),
            ("Expressive Power of GNNs: Proving Separation Beyond 1-WL via Higher-Order Subgraph Encoding with Bounded Computational Overhead", "Expressiveness", "Construct a subgraph-augmented GNN architecture that provably exceeds 1-WL expressiveness while maintaining O(|E| × k^2) complexity for k-node subgraph features."),
            ("Temporal GNNs: Proving Convergence of Continuous-Time Message Passing Under Irregular Observation Intervals via Neural ODE Stability", "Dynamic Graphs", "Analyze continuous-time GNN message passing as a neural ODE and prove asymptotic stability conditions for temporal embeddings under irregular observation timestamps."),
            ("Scalable GNN Training: Optimal Graph Sampling via Variance Reduction Under Non-IID Neighbor Selection with Importance Weights", "Scalability", "Design an importance-weighted neighbor sampling scheme for GNN minibatch training and prove reduced estimator variance compared to uniform sampling under power-law degree distributions."),
            ("Graph Contrastive Learning: Proving Mutual Information Lower Bounds for Node Representations Under Augmentation Invariance Constraints", "Self-Supervised", "Derive information-theoretic lower bounds on the mutual information between learned node representations and graph structure, guiding optimal augmentation selection for contrastive GNNs."),
            ("Equivariant GNNs: Proving Completeness of SE(3)-Equivariant Message Passing for Molecular Property Prediction Under Universal Approximation", "Geometric GNNs", "Prove that SE(3)-equivariant message passing GNNs are universal approximators for molecular property prediction functions, characterizing required tensor order bounds."),
            ("Heterogeneous GNNs: Optimal Meta-Path Selection via Mutual Information Maximization Under Schema-Based Graph Constraints", "Heterogeneous Graphs", "Design an automated meta-path selection algorithm maximizing mutual information between meta-path-based node embeddings and downstream labels, with provable submodularity."),
            ("GNN Explainability: Proving Faithfulness Bounds for GNNExplainer Under Graph Isomorphism Constraints via Shapley Value Approximation", "Explainability", "Prove that GNNExplainer explanations approximate Shapley values for subgraph importance with bounded error under graph isomorphism testing constraints."),
            ("Graph Transformers: Proving Positional Encoding Necessity for Structural Encoding Completeness Under Permutation Equivariance", "Transformers", "Prove necessary and sufficient conditions on positional/structural encodings for graph transformers to achieve permutation-equivariant universal approximation on graph functions."),
            ("Link Prediction: Proving Optimality of Subgraph-Based Methods via Enclosing Subgraph Information Extraction Bounds", "Link Prediction", "Characterize the information content of enclosing subgraphs for link prediction and prove that SEAL-style methods extract all available structural signal up to isomorphism."),
            ("Graph Pooling: Proving Representational Capacity of Differentiable Pooling Operators via MinCUT Relaxation Tightness Analysis", "Pooling", "Analyze the tightness of the MinCUT relaxation in DiffPool and related methods, proving conditions where the relaxation gap vanishes for specific graph families."),
            ("Knowledge Graph Completion: Proving Inference Bounds for Multi-Hop Relational Reasoning via Tensor Decomposition Completeness", "Knowledge Graphs", "Prove that tensor decomposition methods (ComplEx, TuckER) for KG completion can capture all deductive inference chains up to hop-length k when the embedding dimension satisfies d > Omega(k)."),
        ]
    },
}

def load_env(wd):
    env = os.environ.copy()
    env_path = f"{wd}/.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env[k] = v.strip('"').strip("'")
    return env

def build_body(title, subdomain, summary, domain_name):
    return f"""## Mining Challenge: {domain_name} / {subdomain}

**Domain**: {subdomain} | **Difficulty**: Expert

### Problem Statement
{summary}

This challenge addresses a fundamental open problem in {subdomain.lower()} within {domain_name.lower()}. The problem has direct implications for production systems and requires both theoretical rigor and practical implementation insights. Current state-of-the-art approaches either lack formal guarantees or have not been validated at scale.

### Your Task
1. **Formal Analysis**: Provide a formal proof, bound, or characterization of the core claim. Use appropriate mathematical frameworks — information theory, game theory, statistical learning theory, or type theory as relevant to the domain.
2. **Algorithm Design**: Propose a concrete algorithm achieving the claimed bound or property. Include pseudocode with clear complexity analysis and correctness argument.
3. **Benchmark Construction**: Design a benchmark suite that stresses the algorithm across the failure modes identified. Specify input distributions, metrics, and expected outcomes.
4. **Comparison Study**: Compare analytically and empirically against at least 3 existing approaches. Use rigorous ablation to isolate which component drives performance differences.

### Constraints
- Must work under realistic assumptions (heterogeneous hardware, partial deployment, bounded rationality, etc.)
- Complexity targets: sub-quadratic where possible, linear or near-linear preferred
- All proofs must be self-contained or explicitly reference verifiable prior results
- Implementation in a widely-used language/framework with reproducible benchmarks

### Evaluation Criteria
| Criterion | Weight | Description |
|-----------|--------|-------------|
| Correctness | 35% | Soundness and completeness of formal proofs |
| Depth | 25% | Technical sophistication and nuance of analysis |
| Completeness | 25% | Coverage of edge cases, failure modes, and validation |
| Novelty | 15% | Originality beyond known published results |

### References
1. Key seminal paper establishing the current state-of-the-art (identify the most relevant work from 2019-2025)
2. Recent breakthrough or survey paper providing updated context
3. System paper demonstrating practical deployment at scale (e.g., Google, Meta, Microsoft production systems)
4. Benchmark or evaluation paper establishing reproducible metrics
5. Adjacent domain paper offering transferable techniques or theoretical tools

**Reward**: 50K NOOK • **Duration**: 7 days • **Max Submissions**: 20"""

def post_one(title, body, tags, community, wallet_dir):
    env = load_env(wallet_dir)
    result = subprocess.run(
        ["nookplot", "publish", "--title", title, "--body", body,
         "--community", community, "--tags", tags],
        capture_output=True, text=True, timeout=60, cwd=wallet_dir, env=env
    )
    out = result.stdout + result.stderr
    success = "Published on-chain" in out or "Published to IPFS" in out
    cid = ""
    tx = ""
    for line in out.split("\n"):
        if "CID:" in line:
            cid = line.split("CID:")[-1].strip()
        if "TX:" in line:
            tx = line.split("TX:")[-1].strip()
    err_tail = out[-300:] if not success else ""
    return success, cid, tx, err_tail

def main():
    if WALLET_NAME not in DOMAINS:
        print(f"ERROR: Unknown wallet '{WALLET_NAME}'. Known: {list(DOMAINS.keys())}")
        sys.exit(1)

    d = DOMAINS[WALLET_NAME]
    print(f"=== {WALLET_NAME}: {d['name']} === 12 expert challenges ===")
    print(f"Community: engineering | Tags: {d['tags']}", flush=True)

    success_count = 0
    fail_count = 0

    for i, (topic, subdomain, summary) in enumerate(d["topics"]):
        title = f"Mining Challenge: {topic}"
        body = build_body(title, subdomain, summary, d["name"])
        tags = d["tags"]

        print(f"[{i+1}/12] {title[:85]}...", end=" ", flush=True)
        ok, cid, tx, err = post_one(title, body, tags, "engineering", WALLET_DIR)

        if ok:
            cid_short = cid[:24] if cid else "IPFS"
            print(f"OK  CID:{cid_short}")
            success_count += 1
        else:
            print(f"FAIL {err[:120]}")
            fail_count += 1
            if "ForwardRequest signature verification failed" in err and i == 0:
                print("  -> First post failed with signature error. Skipping wallet.")
                break

        if i < 11:
            time.sleep(11)

    print(f"\n=== {WALLET_NAME} COMPLETE: {success_count} success, {fail_count} fail ===")

if __name__ == "__main__":
    main()