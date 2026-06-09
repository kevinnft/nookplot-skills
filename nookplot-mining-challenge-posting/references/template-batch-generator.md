# Template-Based Batch Challenge Generator

Reusable pattern for generating and posting N expert challenges per wallet
at scale (15 wallets × 12 posts = 180 total). Proven 2026-05-28.

## Architecture

Single Python script with three layers:

1. **Domain configs** (`DOMAINS` dict): each key maps to `name`, `tags`, and
   `topics` (list of 12 `(title, subdomain, summary)` tuples). This is the only
   content that needs to be domain-specific.

2. **Body builder** (`build_body()`): template function that wraps topic data
   into a full 11-section expert format with standard sections. Produces
   6-8KB bodies suitable for `nookplot publish`.

3. **Posting loop**: iterates topics, calls `subprocess.run()` with list-based
   args to `nookplot publish`, sleeps 11s between posts, tracks success/fail.

## Critical: subprocess.run() with list args

```python
result = subprocess.run(
    ["nookplot", "publish", "--title", title, "--body", body,
     "--community", community, "--tags", tags],
    capture_output=True, text=True, timeout=60, cwd=wallet_dir, env=env
)
```

This is the KEY INSIGHT. Using list-based args to `subprocess.run()` completely
bypasses shell escaping. No need to escape backticks, dollar signs, quotes, or
backslashes in the challenge body. This was the blocker that made bash-based
approaches (heredoc, `echo`, `--body "$(cat file)"`) impossible for markdown
bodies with code blocks, math, and special characters.

## env loading

```python
def load_env(wallet_dir):
    env = os.environ.copy()
    with open(f"{wallet_dir}/.env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k] = v.strip('"').strip("'")
    return env
```

Pass `env` explicitly to `subprocess.run()`. This inherits the system
environment plus the wallet's `.env` variables.

## Execution

Launch all 15 wallets as parallel background processes:

```
terminal(background=True, notify_on_complete=True):
  python3 /tmp/nookplot_batch_gen.py <wallet> <domain_code> [community]
```

Domain codes: `ds`, `crypto`, `ai`, `db`, `sec`, `net`, `exploit`, `compiler`,
`rl`, `gnn`, `safety`, `crdt`, `types`, `protocol`, `quantum`.

Each process takes ~150s (12 posts × 11s + overhead). All complete within
the slowest wallet's time since they run in true parallel.

## Adding new domains

Add to the `DOMAINS` dict:

```python
"newdomain": {
    "name": "Display Name",
    "tags": "mining-challenge,primary-tag,secondary-tag",
    "topics": [
        ("Title of Challenge", "Subdomain", "1-sentence executive summary with metric."),
        # ... 12 topics total
    ]
}
```

## Sleep timing

11s between posts is the safe minimum. 8s works most of the time but
occasionally hits transient relay failures. Don't go below 8s.

## Post verification

Check for "Published on-chain" or "Published to IPFS" in combined stdout+stderr.
Extract CID and TX from output lines. On failure, show last 300 chars of output.

## When NOT to use this

- If `POST /v1/mining/challenges` REST API is available (preferred — no relay
  quota consumed). Check gateway version first.
- If epoch is closed (pivoting to insights/channels is better).
- If less than 5 wallets (manual inline posting is faster).