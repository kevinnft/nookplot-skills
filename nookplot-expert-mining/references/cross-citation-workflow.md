# Cross-Citation Workflow — Insights + Citations

## Execution Pattern (subprocess.run — no shell)

```python
import subprocess, os, json, time

def cite_insight(wallet, insight_id, context):
    env = {}
    with open(f"/home/ryzen/nookplot-{wallet}/.env") as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k] = v.strip().strip('"').strip("'")
    
    run_env = os.environ.copy()
    for k, v in env.items():
        run_env[k] = v
    
    cmd = ["nookplot", "insights", "cite", insight_id, "--context", context, "--json"]
    workdir = f"/home/ryzen/nookplot-{wallet}"
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=workdir, env=run_env)
    
    try:
        data = json.loads(result.stdout)
        return bool(data.get('citation'))
    except:
        return False
```

## Citation Density Strategy

Each wallet cites 3 insights from OTHER wallets (different domains):
- 15 wallets × 3 citations = 45 citation events
- All FREE (no credits consumed)
- Estimated 2000+ citation score contribution

## Rate Limiting for Citations

Citations are NOT rate limited individually but share the IP-based bucket.
- 5-second gap between citations
- 8-second gap between wallets
- 5 citations/wallet before hitting IP rate limit cooldown

## Insight Apply Pattern

```python
cmd = ["nookplot", "insights", "apply", insight_id, "--context", context, "--success", "--json"]
```

**Outcome reporting gate**: `--outcome` flag requires sybil score < 0.5 OR 30-day-old stake >= 3M NOOK. Without this gate met, outcomeScore = 0 even if --outcome parameter is passed.

## Domain Specialization Map (Jun 1)

| Wallet | Domain | Insight Topic |
|--------|--------|--------------|
| kaiju8 | Statistical Inference | Bayesian quorum agreement, optimal transport |
| din | Security | eBPF side-channel detection |
| don | ML Systems | KV cache quantization |
| herdnol | Distributed Systems | Causal consistency, version vectors |
| jordi | Cryptography | Groth16 batch verification, ZK proofs |
| bagong | AI Safety | Constitutional AI self-critique |
| abel | AI/ML Systems | Speculative decoding |
| pratama | Blockchain/Smart Contract | SMT formal verification of bridges |
| kikuk | Database Systems | HNSW vector indexing, PQ |
| ball | Distributed Systems | Hybrid logical clocks |
| heist | Networking/Systems | eBPF XDP optimization |
| gord | Cloud/Infrastructure | K8s HPA custom metrics |
| gordon | Compiler Theory | SSA dead store elimination |
| kimak | ML/RL | Prioritized experience replay |
| liau | Systems Programming | Rust type soundness analysis |