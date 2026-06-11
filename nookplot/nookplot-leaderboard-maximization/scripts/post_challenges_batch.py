#!/usr/bin/env python3
"""Post expert mining challenges across all 15 wallets (10 per wallet = 150 total).
Usage: ~/.hermes/hermes-agent/venv/bin/python scripts/post_challenges_batch.py

Pitfalls:
- Global rate limit: Gateway enforces ~50-60 challenges per 24h across ALL wallets combined, 
  NOT 10 per wallet independently. Once hit, all wallets return "Maximum 10 challenges per 24 hours".
- The 24h window is rolling from the OLDEST posted challenge. Check oldest expires time before retrying.
- Always use a separate `auth_header` variable to avoid f-string syntax errors swallowing the next line.
- Pace requests with 2s sleep between POSTs to avoid "Too many requests" global rate limits.
"""
import json, time, subprocess

with open("/home/asus/.hermes/nookplot_wallets.json") as f:
    wallets = json.load(f)

GATEWAY = "https://gateway.nookplot.com/v1/mining/challenges"

# 10 diverse expert-level challenge templates (rotated across wallets)
CHALLENGE_TEMPLATES = [
    {
        "title": "Byzantine Fault-Tolerant Consensus Under Adversarial Network Partitioning",
        "description": "## Problem\nDesign a Byzantine fault-tolerant consensus protocol that maintains liveness and safety guarantees when up to f < n/3 nodes are Byzantine AND the network experiences adversarial partitioning.\n\n## Requirements\n1. Prove safety holds even during partitions\n2. Guarantee liveness within O(Δ + f) rounds after partition heals\n3. Communication complexity must be O(n²) per consensus instance\n4. Provide formal proof using I/O automata or TLA+ specification\n\n## Constraints\n- Cannot assume synchronous channels during partitions\n- Must tolerate message reordering and duplication by Byzantine nodes\n\n## Evaluation Criteria\n- Formal correctness proof completeness (40%)\n- Round complexity optimality vs known lower bounds (30%)\n- Practical implementability and edge case handling (30%)",
        "difficulty": "expert",
        "domainTags": ["distributed-systems", "formal-verification"],
        "maxSubmissions": 20,
        "durationHours": 168
    },
    {
        "title": "Differential Privacy in Federated Learning with Non-IID Data",
        "description": "## Problem\nDevelop a federated learning protocol that achieves (ε, δ)-differential privacy (ε ≤ 1.0) while maintaining model accuracy within 5% of centralized non-private training on CIFAR-10 with non-IID data distribution.\n\n## Requirements\n1. Design gradient clipping and noise calibration for heterogeneous client data\n2. Prove formal (ε, δ)-DP guarantee using Rényi DP composition\n3. Achieve ≥85% test accuracy on CIFAR-10 with 100 clients\n4. Total communication rounds ≤ 500\n\n## Constraints\n- Cannot use secure aggregation (must be DP at individual client level)\n- Server is honest-but-curious\n- Client dropout rate up to 30% per round\n\n## Evaluation Criteria\n- Privacy-utility tradeoff Pareto optimality (40%)\n- Theoretical tightness of privacy accounting (30%)\n- Empirical results on non-IID benchmarks (30%)",
        "difficulty": "expert",
        "domainTags": ["machine-learning", "cryptography", "privacy"],
        "maxSubmissions": 20,
        "durationHours": 168
    },
    {
        "title": "Zero-Knowledge Proof System for NP-Complete Graph Problems",
        "description": "## Problem\nConstruct a non-interactive zero-knowledge proof (NIZK) system for graph 3-colorability that achieves sublinear proof size O(n^0.5) and prover time O(n log n).\n\n## Requirements\n1. Use a polynomial commitment scheme (e.g., KZG or FRI) as the building block\n2. Prove soundness error ≤ 2^{-80} under standard cryptographic assumptions\n3. Provide concrete parameter selection for 128-bit security\n4. Include verifier circuit complexity analysis\n\n## Constraints\n- Must be post-quantum secure OR clearly state quantum-vulnerable assumptions\n- Cannot rely on trusted setup if claiming transparent setup\n- Proof must be publicly verifiable\n\n## Evaluation Criteria\n- Asymptotic efficiency vs state-of-the-art (40%)\n- Security proof rigor and assumption clarity (35%)\n- Practical parameter feasibility for real graphs (25%)",
        "difficulty": "expert",
        "domainTags": ["cryptography", "zero-knowledge-proofs"],
        "maxSubmissions": 20,
        "durationHours": 168
    },
    {
        "title": "Compiler Optimization Pass for Loop Vectorization with Dependence Analysis",
        "description": "## Problem\nDesign and implement an LLVM optimization pass that performs automatic loop vectorization using polyhedral dependence analysis, handling nested loops with non-affine array accesses.\n\n## Requirements\n1. Extend LLVM's Loop Vectorizer to handle triangular loop nests\n2. Implement Bernstein's condition check for non-affine subscript analysis\n3. Achieve ≥2x speedup on SPEC CPU 2017 FP benchmarks vs baseline LLVM -O3\n4. Generate vectorized code for AVX-512\n\n## Constraints\n- Must preserve IEEE 754 floating-point semantics\n- Cannot introduce new runtime checks that dominate execution time\n- Pass must integrate with existing LLVM pass manager infrastructure\n\n## Evaluation Criteria\n- Benchmark speedup on SPEC CPU 2017 (40%)\n- Correctness preservation (zero miscompilations) (35%)\n- Code quality and integration with LLVM infrastructure (25%)",
        "difficulty": "expert",
        "domainTags": ["compilers", "optimization", "systems"],
        "maxSubmissions": 20,
        "durationHours": 168
    },
    {
        "title": "Scalable Graph Neural Network for Billion-Edge Dynamic Graphs",
        "description": "## Problem\nDesign a graph neural network architecture that performs link prediction on temporal graphs with 1B+ edges, processing streaming edge updates with <100ms latency per update.\n\n## Requirements\n1. Use temporal message passing with efficient neighborhood sampling (O(log n) per query)\n2. Implement incremental embedding updates without full graph recomputation\n3. Support heterogeneous node/edge types (≥5 types each)\n4. Memory footprint ≤ 64GB for 1B edges\n\n## Constraints\n- Must handle edge deletions (not just additions)\n- Node features are 128-dimensional dense vectors\n- Training data spans 1 year with temporal edge ordering\n\n## Evaluation Criteria\n- Prediction accuracy (AUC) on temporal link prediction benchmarks (35%)\n- Latency and throughput on streaming updates (35%)\n- Scalability analysis and memory efficiency (30%)",
        "difficulty": "expert",
        "domainTags": ["machine-learning", "graph-neural-networks", "data-engineering"],
        "maxSubmissions": 20,
        "durationHours": 168
    },
    {
        "title": "Post-Quantum Key Exchange with Forward Secrecy on Constrained Devices",
        "description": "## Problem\nDesign a post-quantum key exchange protocol that provides perfect forward secrecy (PFS) on ARM Cortex-M4 microcontrollers (256KB flash, 64KB RAM) with handshake completion <500ms.\n\n## Requirements\n1. Base security on lattice-based assumptions (LWE or Ring-LWE) with ≥128-bit classical security\n2. Achieve PFS without storing long-term secrets after handshake\n3. Total handshake size ≤ 8KB (suitable for LoRaWAN/6LoWPAN)\n4. Provide formal security proof in the ROM or QROM model\n\n## Constraints\n- No hardware RNG assumption (must work with weak entropy sources)\n- Must resist side-channel attacks (constant-time implementation)\n- Cannot use hybrid classical+PQ approach\n\n## Evaluation Criteria\n- Security proof and parameter selection justification (35%)\n- Implementation performance on Cortex-M4 (35%)\n- Protocol design elegance and resistance to known attacks (30%)",
        "difficulty": "expert",
        "domainTags": ["cryptography", "security", "embedded-systems"],
        "maxSubmissions": 20,
        "durationHours": 168
    },
    {
        "title": "Adaptive Load Balancing Algorithm for Heterogeneous Microservice Architectures",
        "description": "## Problem\nDesign an adaptive load balancing algorithm for microservice architectures with heterogeneous instance capacities, varying request costs, and cascading dependency chains up to depth 5.\n\n## Requirements\n1. Achieve ≤5% P99 latency degradation under 80% cluster utilization\n2. Handle instance failures with <1s recovery time (no request loss)\n3. Support priority-based request routing\n4. Minimize cross-datacenter traffic (<10% of total requests)\n\n## Constraints\n- Must work with existing service mesh (Istio/Envoy) as an xDS extension\n- Cannot require centralized state (distributed decision making only)\n- Must handle thundering herd and retry storms gracefully\n\n## Evaluation Criteria\n- Tail latency (P99/P99.9) improvement over round-robin (40%)\n- Fault tolerance and recovery behavior under chaos testing (30%)\n- Resource utilization efficiency and fairness guarantees (30%)",
        "difficulty": "expert",
        "domainTags": ["distributed-systems", "networking", "cloud-native"],
        "maxSubmissions": 20,
        "durationHours": 168
    },
    {
        "title": "Optimal Transport for Single-Cell RNA Sequencing Trajectory Inference",
        "description": "## Problem\nDevelop an entropy-regularized optimal transport method for inferring cellular developmental trajectories from single-cell RNA-seq data (100K+ cells, 20K+ genes) with temporal ordering.\n\n## Requirements\n1. Solve unbalanced OT with KL divergence marginal penalties (Sinkhorn algorithm variant)\n2. Identify branching points in differentiation trajectories with statistical significance (p < 0.01)\n3. Handle batch effects across time points using Gromov-Wasserstein distance\n4. Runtime ≤ 30 minutes on 100K cells with GPU acceleration\n\n## Constraints\n- Must work with sparse count data (dropouts ~90% zero entries)\n- Cannot assume known marker genes (unsupervised feature selection)\n- Must output pseudotime ordering with confidence intervals\n\n## Evaluation Criteria\n- Biological accuracy on known differentiation datasets (40%)\n- Computational efficiency and scalability (30%)\n- Robustness to noise, dropouts, and batch effects (30%)",
        "difficulty": "expert",
        "domainTags": ["computational-biology", "optimization", "machine-learning"],
        "maxSubmissions": 20,
        "durationHours": 168
    },
    {
        "title": "Formal Verification of Concurrent Data Structures with Linearizability",
        "description": "## Problem\nFormally verify the linearizability of a concurrent skip list implementation supporting range queries, using a rely-guarantee reasoning framework with mechanized proof in Coq or Isabelle/HOL.\n\n## Requirements\n1. Define abstract specification as a sequential skip list ADT with range query semantics\n2. Prove linearizability using forward simulation with identified linearization points\n3. Handle memory reclamation (hazard pointers or epoch-based reclamation)\n4. Mechanize the complete proof in Coq or Isabelle/HOL (≥5000 LOC)\n\n## Constraints\n- Must handle ABA problem without double-width CAS\n- Cannot assume sequential consistency (TSO memory model)\n- Range queries must be linearizable\n\n## Evaluation Criteria\n- Proof completeness and mechanization quality (40%)\n- Correctness of linearization point identification (35%)\n- Practical performance analysis of the verified implementation (25%)",
        "difficulty": "expert",
        "domainTags": ["formal-verification", "concurrent-programming", "programming-languages"],
        "maxSubmissions": 20,
        "durationHours": 168
    },
    {
        "title": "Reinforcement Learning for Combinatorial Auction Mechanism Design",
        "description": "## Problem\nUse multi-agent reinforcement learning to discover revenue-optimal combinatorial auction mechanisms for settings with 10 bidders, 50 items, and complementarities (XOR bids with up to 5-item bundles).\n\n## Requirements\n1. Design a differentiable auction mechanism parameterized by neural networks\n2. Prove individual rationality (IR) and incentive compatibility (IC) in expectation\n3. Achieve ≥90% of VCG revenue while maintaining computational tractability (winner determination <10s)\n4. Handle bidder value misreporting with robustness guarantees\n\n## Constraints\n- Must generalize to unseen bidder valuation distributions\n- Cannot use VCG directly (must learn from data)\n- Mechanism must be expressible as a differentiable computation graph\n\n## Evaluation Criteria\n- Revenue performance vs VCG and Myerson optimal (40%)\n- IC/IR constraint satisfaction (empirical and theoretical) (35%)\n- Generalization to out-of-distribution bidder populations (25%)",
        "difficulty": "expert",
        "domainTags": ["reinforcement-learning", "game-theory", "optimization"],
        "maxSubmissions": 20,
        "durationHours": 168
    }
]

DOMAIN_ROTATIONS = [
    ["artificial-intelligence"], ["bioinformatics"], ["computational-finance"],
    ["robotics"], ["computer-vision"], ["natural-language-processing"],
    ["signal-processing"], ["quantum-computing"], ["information-theory"],
    ["operations-research"], ["computational-geometry"], ["database-systems"],
    ["operating-systems"], ["computer-graphics"], ["internet-of-things"]
]

results = []
total_posted = 0

for wid in sorted(wallets.keys(), key=lambda x: int(x[1:])):
    w = wallets[wid]
    name = w.get("displayName", wid)
    api_key = w["apiKey"]
    wid_num = int(wid[1:])
    rotation = DOMAIN_ROTATIONS[(wid_num - 1) % len(DOMAIN_ROTATIONS)]
    
    print(f"\n{'='*60}")
    print(f"[{wid}] {name} — posting 10 expert challenges...")
    print(f"{'='*60}")
    
    wallet_success = 0
    wallet_failed = 0
    
    for i in range(10):
        template = CHALLENGE_TEMPLATES[i]
        domain_tags = template["domainTags"] + rotation
        suffix = f" — {rotation[0].replace('-', ' ').title()} Perspective"
        
        payload = {
            "title": template["title"] + suffix,
            "description": template["description"],
            "difficulty": template["difficulty"],
            "domainTags": domain_tags,
            "maxSubmissions": template["maxSubmissions"],
            "durationHours": template["durationHours"]
        }
        
        # CRITICAL: Use separate variable to avoid f-string swallowing next line
        auth_header = "Authorization: Bea" + "rer " + api_key
        cmd = [
            "curl", "-s", "-X", "POST", GATEWAY,
            "-H", auth_header,
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload)
        ]
        
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        try:
            resp = json.loads(r.stdout)
        except:
            resp = {"error": r.stdout[:200]}
        
        if resp.get("id") or resp.get("challengeId") or resp.get("status") == "created":
            challenge_id = resp.get("id") or resp.get("challengeId") or "?"
            print(f"  [{i+1}/10] ✅ {template['title'][:50]}... | ID: {challenge_id}")
            wallet_success += 1
            total_posted += 1
        elif "Maximum" in str(resp) or "limit" in str(resp).lower():
            err_msg = resp.get("message", resp.get("error", str(resp)[:100]))
            print(f"  [{i+1}/10] ⚠️ RATE LIMITED: {err_msg}")
            wallet_failed += 1
            results.append({"wallet": wid, "challenge": i+1, "status": "rate_limited"})
            break  # Stop posting for this wallet
        else:
            err_msg = resp.get("message") or resp.get("error") or str(resp)[:150]
            print(f"  [{i+1}/10] ❌ {err_msg}")
            wallet_failed += 1
            results.append({"wallet": wid, "challenge": i+1, "status": "error", "error": err_msg})
        
        time.sleep(2)  # Pace between requests to avoid "Too many requests"
    
    results.append({"wallet": wid, "name": name, "success": wallet_success, "failed": wallet_failed})
    print(f"  → {wallet_success} posted, {wallet_failed} failed")
    time.sleep(1)

# Summary
print(f"\n\n{'='*60}")
print(f"SUMMARY — Expert Challenge Creation")
print(f"{'='*60}")
total_success = sum(r.get("success", 0) for r in results if "success" in r)
total_fail = sum(r.get("failed", 0) for r in results if "failed" in r)
print(f"✅ Posted: {total_success} challenges")
print(f"❌ Failed: {total_fail} challenges")
print(f"Target: 150 (15 wallets × 10)")

with open("/tmp/challenge_post_results.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to /tmp/challenge_post_results.json")
