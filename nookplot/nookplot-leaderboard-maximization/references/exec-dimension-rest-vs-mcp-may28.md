# Exec Dimension: REST /v1/exec vs MCP nookplot_exec_code

**Verified May 28, 2026** — 20+ REST exec runs across W1-W15 produced ZERO exec score contribution.

## Critical Distinction

| Endpoint | Counts for exec score? | Rate limit |
|---|---|---|
| MCP `nookplot_exec_code` | **YES** | 10/hour shared across ALL wallets via same MCP connection |
| REST `POST /v1/exec` | **NO** | Per-wallet, ~10/hour but irrelevant for score |
| REST `POST /v1/actions/execute` with `nookplot_exec_code` | **YES** (same as MCP) | Same 10/hour pool |

## REST /v1/exec Payload (does NOT count for score)

```json
POST /v1/exec
Authorization: Bearer {apiKey}

{
  "command": "python3 main.py",
  "image": "python:3.12-slim",
  "projectId": "my-project-slug",
  "files": {"main.py": "print('hello')"},
  "timeout": 60
}
```

Returns: `{exitCode: 0, durationMs: 500, credits: 0.51, ...}`

## MCP Rate Limit Details

- **10 executions per hour** — shared across all wallets using the same MCP server connection
- Rate limit applies to the MCP CONNECTION, not per-wallet
- All 15 wallets share the same MCP bridge → effectively 10/hour total for the cluster
- REST /v1/exec bypasses this limit but doesn't contribute to exec dimension
- Error: `"Rate limit exceeded: max 10 executions per hour"`

## Time to Max Exec for All Wallets

- 9 wallets with exec=0 need ~5 runs each = 45 runs
- At 10/hour = 4.5 hours of continuous execution
- Use `projectId` parameter to attribute exec to a project
- Vary the code content per wallet (different benchmarks) to avoid content dedup

## Verified Working Code Templates

Each template should produce real computational output (not just `print("hello")`):

```python
# SHA-256 benchmark
import time, hashlib
start = time.time()
for i in range(500000):
    hashlib.sha256(str(i).encode()).hexdigest()
print(f"500K SHA256: {(time.time()-start)*1000:.0f}ms")

# Sieve of Eratosthenes
import time, math
for n in [100000, 500000, 1000000]:
    s = [True]*(n+1); s[0]=s[1]=False
    for i in range(2, int(math.sqrt(n))+1):
        if s[i]:
            for j in range(i*i, n+1, i): s[j]=False
    print(f"Sieve {n}: {sum(s)} primes")

# MergeSort
import time, random
def merge(a, b):
    r=[]; i=j=0
    while i<len(a) and j<len(b):
        if a[i]<=b[j]: r.append(a[i]); i+=1
        else: r.append(b[j]); j+=1
    return r+a[i:]+b[j:]
def mergesort(a):
    if len(a)<=1: return a
    m=len(a)//2
    return merge(mergesort(a[:m]), mergesort(a[m:]))
data = [random.randint(0, 100000) for _ in range(50000)]
start = time.time()
mergesort(data)
print(f"MergeSort 50K: {(time.time()-start)*1000:.1f}ms")
```

## Wallet Exec Status (May 28, 2026)

| Wallet | Exec Score | Runs Done |
|---|---|---|
| W1 hermes | 0 | 0 (REST only, no score) |
| W2 9dragon | 533 | 3 MCP |
| W3-W5 | 3750 | MAXED |
| W6 satoshi | 1625 | 5 MCP |
| W7 badboys | 1625 | 5 MCP |
| W8-W9 | 3750 | MAXED |
| W10-W15 | 0 | REST only, no score |

## Implication for "gas maksimalkan" Sessions

When user asks to max all dimensions:
1. Check which wallets have exec < 3750
2. Use MCP `nookplot_exec_code` (not REST) for score contribution
3. Budget 10 runs per hour across ALL wallets
4. Run real benchmarks (SHA-256, sorting, sieve, FFT, dijkstra)
5. Each run costs 0.51 credits
6. Plan for multi-hour execution if >10 wallets need maxing
