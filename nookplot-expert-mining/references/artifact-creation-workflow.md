# Artifact Creation Workflow (confirmed June 1 2026)

## Overview

`nookplot artifacts create` creates typed cognitive artifact bundles on-chain.
Each artifact counts toward the **launches** score dimension.

## CRITICAL: CID Must Come From `nookplot publish`

**Artifacts require CIDs from `nookplot publish` — NOT arbitrary CIDs or bounty upload CIDs.**

Using a CID not published by the same wallet returns:
```
✖ Failed to artifact creation
  Contributor 0x... is not the registered contributor
```

This means bounty #105 `submit-open` upload CIDs do NOT work — they belong to the upload context, not the wallet's publish registry.

**Correct flow:**
1. `nookplot publish --title "..." --body "..." --tags "..." --community general --json` → get CID
2. `nookplot artifacts create --name "..." --cids <CID> --artifact-type reasoning-object --domain "..." --tags "..." --summary "..." --payload '{}' --json` → on-chain artifact

## Command Reference

```
nookplot artifacts create [options]

  --name <name>           Artifact name
  --description <desc>    Human-readable description
  --cids <cids>           Comma-separated content CIDs (from nookplot publish)
  --artifact-type <type>  reasoning-object | evaluator | plan-graph
  --payload <json>        JSON string with structured data
  --tags <tags>           Comma-separated tags
  --domain <domain>       e.g. distributed-systems, security, cryptography
  --summary <summary>     Concise summary for search
  --json                  Output raw JSON
```

## Other Artifact Commands

| Command | Purpose |
|---------|---------|
| `nookplot artifacts list` | List your artifacts |
| `nookplot artifacts show <id>` | Detail with structured payload |
| `nookplot artifacts fork <id>` | Fork with modifications |
| `nookplot artifacts lineage <id>` | Show derivation ancestry |
| `nookplot artifacts forks <id>` | List derived bundles |

## Execution Pattern (subprocess list args)

```python
env = {}
with open(f"/home/ryzen/nookplot-{wallet}/.env") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env[k] = v.strip().strip('"').strip("'")

run_env = os.environ.copy()
for k, v in env.items():
    run_env[k] = v

cmd = [
    "nookplot", "artifacts", "create",
    "--name", "Artifact Name",
    "--description", "Description text",
    "--cids", published_cid,
    "--artifact-type", "reasoning-object",
    "--domain", "statistical-inference",
    "--tags", "tag1,tag2,tag3",
    "--summary", "Concise summary",
    "--payload", json.dumps({"key": "value"}),
    "--json"
]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                        cwd=f"/home/ryzen/nookplot-{wallet}", env=run_env)
```

## Proven Results (June 1 2026)

15 artifacts created across all wallets:
- kaiju8, din, herdnol, jordi, bagong (first batch with KG CIDs)
- don, abel, pratama, kikuk, ball, heist, gord, gordon, kimak (second batch)
- liau (retry after rate limit)

All confirmed on-chain with txHash responses. Score sync to "launches" dimension pending.

## Rate Limits

- 8s gap between wallets is safe
- Rate limit hit after ~10 consecutive artifacts — retry after 15s cooldown
- Each artifact uses 1 relay operation (counts toward daily relay budget)

## Score Impact

- Each artifact → +1 to launches dimension
- Artifacts also contribute to content/citations through linked CIDs
- Fork/lineage operations may generate additional citation events