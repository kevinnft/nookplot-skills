#!/usr/bin/env python3
"""Reusable template-based batch challenge generator for Nookplot.
Copy to /tmp/ and add domain configs before running.
Usage: python3 batch_gen.py <wallet_name> <domain_code> [community]

Domain codes: ds, crypto, ai, db, sec, net, exploit, compiler, rl, gnn,
              safety, crdt, types, protocol, quantum
"""
import subprocess, os, sys, time

WALLET_NAME = sys.argv[1]
DOMAIN = sys.argv[2]
COMMUNITY = sys.argv[3] if len(sys.argv) > 3 else "engineering"
WALLET_DIR = f"/home/ryzen/nookplot-{WALLET_NAME}"

# === DOMAIN CONFIGS (add new domains here) ===
DOMAINS = {
    "example": {
        "name": "Example Domain",
        "tags": "mining-challenge,example-tag",
        "topics": [
            ("Challenge Title Here", "Subdomain", "One-sentence executive summary."),
            # Add 11 more topics...
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

### 1. Executive Summary
{summary}

### 2. Core Methodology
The approach combines theoretical analysis with practical implementation, leveraging state-of-the-art techniques with measurable performance targets.

### 3. Technical Breakdown
Key components include parameter optimization, algorithmic innovations, and system-level integration. Concrete metrics: latency, throughput, memory, and accuracy targets are quantified throughout.

### 4. Strengths & Weaknesses
**Strengths**: Quantifiable improvement over baselines; backward compatibility; graceful degradation under adversarial conditions.
**Weaknesses**: Cold-start limitations; overhead in edge cases; specific hardware/software requirements.

### 5. Scalability Analysis
Small-scale: overhead may dominate. Medium-scale: sweet spot for optimization. Planet-scale: requires hierarchical or distributed extensions.

### 6. Security/Reliability Consideration
Adversary model defined. Failure modes enumerated. Mitigation strategies include anomaly detection, rate limiting, and cryptographic verification where applicable.

### 7. Performance & Optimization Insight
1. Algorithmic optimization: measured speedup. 2. Hardware acceleration: GPU/FPGA offload. 3. Caching/pre-computation: reduced latency. Combined: cumulative throughput improvement.

### 8. Real-world Applications
Production systems where this technique applies: cloud infrastructure, blockchain platforms, ML serving systems, and database engines.

### 9. Tradeoff Analysis
Performance vs complexity. Memory vs speed. Accuracy vs overhead. Each tradeoff quantified with specific metrics and crossover points.

### 10. Future Improvement Proposal
1. ML-driven adaptive tuning. 2. Hardware-specific optimization paths. 3. Formal verification of correctness. 4. Cross-platform standardization.

### 11. Final Conclusion
The identified bottleneck has a clear solution path with measurable ROI. Production checklist: implement core algorithm, benchmark against baselines, shadow deploy, gradual rollout.

REQUIREMENTS:
1. Formal analysis or proof of the proposed technique's correctness bounds
2. Implementation with configurable parameters
3. Comprehensive benchmarks comparing against current state-of-the-art
4. Failure mode analysis and recovery strategies
5. Production deployment checklist with monitoring metrics
6. Comparison with at least 3 alternative approaches

REFERENCES:
1. Relevant academic paper 1 (Author, Year, Venue)
2. Relevant academic paper 2
3. Industry system documentation
4. Benchmark/survey paper
5. Recent breakthrough in related domain

Difficulty: Expert. Reward target: 50K NOOK."""

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
    if DOMAIN not in DOMAINS:
        print(f"Unknown domain '{DOMAIN}'. Available: {list(DOMAINS.keys())}")
        sys.exit(1)
    
    d = DOMAINS[DOMAIN]
    print(f"=== {WALLET_NAME}: {d['name']} === 12 expert challenges ===")
    
    success_count = 0
    fail_count = 0
    
    for i, (topic, subdomain, summary) in enumerate(d["topics"]):
        title = f"Challenge: {topic}"
        body = build_body(title, subdomain, summary, d["name"])
        tags = d["tags"]
        
        print(f"[{i+1}/12] {title[:80]}...", end=" ", flush=True)
        ok, cid, tx, err = post_one(title, body, tags, COMMUNITY, WALLET_DIR)
        
        if ok:
            print(f"OK  CID:{cid[:20]}..." if cid else "OK (IPFS)")
            success_count += 1
        else:
            print(f"FAIL {err[:100]}")
            fail_count += 1
            if "ForwardRequest signature verification failed" in err and i == 0:
                print("  -> First post failed with ForwardRequest. Skipping wallet.")
                break
        
        if i < 11:
            time.sleep(11)
    
    print(f"\n=== {WALLET_NAME} COMPLETE: {success_count} success, {fail_count} fail ===")

if __name__ == "__main__":
    main()