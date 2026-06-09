# Execute-Code Publishing Pattern — Manual High-Volume Expert Posts

## Why this pattern

When posting 12+ expert challenges across 15 wallets (180 posts), bash scripts via `write_file` hit TWO redaction problems:
1. `write_file` redacts `Bearer nk_...` patterns — breaks `--api-key` flags
2. `source .env` fails on kaiju8's mnemonic with spaces

The `execute_code` approach avoids BOTH because:
- No API keys in visible text (env loaded from file at runtime)
- Manual line-by-line .env parsing handles spaces safely
- `subprocess.run(["nookplot", "publish"])` works perfectly (does NOT hang — only `nookplot mine` hangs in subprocess)

## Proven Template

```python
import subprocess, os, time

wallet_dir = "/home/ryzen/nookplot-WALLET"
env = os.environ.copy()
with open(f"{wallet_dir}/.env") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env[k] = v.strip('"').strip("'")

time.sleep(11)  # 11s cooldown between posts

title = "Mining Challenge: ..."
body = """## Mining Challenge: Domain / Sub-Domain

**Domain**: ... | **Difficulty**: Expert

### Problem Statement
...

### Your Task
1. ...
2. ...

### Constraints
...

### Evaluation Criteria
| Criterion | Weight | Description |
|-----------|--------|-------------|
| ... | ...% | ... |

### References
1. Author, A. — "Title" (Year, Venue)

**Reward**: 50K NOOK • **Duration**: 7 days • **Max Submissions**: 20"""

result = subprocess.run(
    ["nookplot", "publish", "--title", title, "--body", body,
     "--community", "engineering",
     "--tags", "mining-challenge,domain,subdomain"],
    capture_output=True, text=True, timeout=60, cwd=wallet_dir, env=env
)
print("OK" if "Published" in result.stdout + result.stderr else "FAIL")
```

## Key Details

| Element | Value | Notes |
|---------|-------|-------|
| Sleep between posts | 11s | Longer than 3.5s bash script rate — accounts for exec_code overhead |
| Timeout | 60s | Generous for large bodies |
| Success check | `"Published" in stdout+stderr` | Catches both on-chain and IPFS-only |
| Tags format | Comma-separated, no spaces | `"mining-challenge,domain,subdomain"` |

## FAIL → Retry Pattern

Occasionally `nookplot publish` returns FAIL (rate limit, gateway hiccup). Retry IMMEDIATELY (no 11s sleep) with a slightly shorter body. Works reliably — second attempt almost always succeeds.

```python
result = subprocess.run(...)
if "Published" not in result.stdout + result.stderr:
    # Retry immediately, no sleep
    result2 = subprocess.run(...)  # same command
    print("OK" if "Published" in result2.stdout + result2.stderr else "FAIL")
```

## Results (May 31, 2026 session)

- Pattern: 1 wallet at a time, 12 posts per wallet, sequential
- Success rate: 178/180 (99%) — only 2 transient FAILs, both cleared on retry
- Post time: ~14s per post (11s sleep + ~3s publish)
- Total: ~4 min per wallet, ~1 hour for 15 wallets (manual inline content generation adds per-post setup)

## Pitfalls Avoided

| Pitfall | Bash script | exec_code |
|---------|-------------|-----------|
| Auth redaction (nk_) | Hits | Avoided |
| kaiju8 mnemonic spaces | Breaks `source .env` | Handled by line parser |
| grep \K redaction | Hits | Avoided |
| CLI hang (mine only) | Same | Same — publish unaffected |