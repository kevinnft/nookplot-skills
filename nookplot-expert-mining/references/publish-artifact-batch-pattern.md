# Publish + Artifact Batch Pattern (Verified June 1, 2026)

## Problem
Bash scripts with `$(nookplot publish ... | grep -o '"cid":"[^"]*"' | cut -d'"' -f4)` for CID extraction fail silently when article body contains special characters, quotes, or long text.

## Working Pattern: Python execute_code

```python
import subprocess, json, os, time, re

def get_env(wallet):
    env = {}
    for line in open(f'/home/ryzen/nookplot-{wallet}/.env'):
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v.strip().strip('"').strip("'")
    return env

def publish_and_get_cid(wallet, title, body, tags):
    cmd = ['bash', '-c', f'cd ~/nookplot-{wallet} && set -a && source .env 2>/dev/null && set +a && nookplot publish --title "{title}" --body "{body}" --community "general" --tags "{tags}" --json 2>&1']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    # Extract CID via regex from full output
    cid_match = re.search(r'(Qm[a-zA-Z0-9]{44})', r.stdout)
    return cid_match.group(1) if cid_match else None

def create_artifact(wallet, name, desc, domain, tags, summary, payload, cid):
    cmd = ['bash', '-c', f'cd ~/nookplot-{wallet} && set -a && source .env 2>/dev/null && set +a && nookplot artifacts create --name "{name}" --description "{desc}" --artifact-type "reasoning-object" --domain "{domain}" --tags "{tags}" --summary "{summary}" --payload \'{payload}\' --cids "{cid}" --json 2>&1']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return 'txHash' in r.stdout or 'name' in r.stdout
```

## Key Requirements

1. **Sequential per wallet**: publish first → extract CID → create artifact with that CID
2. **CID must be wallet's own**: artifacts `--cids` must reference content published by the same wallet
3. **5s sleep between wallets**: rate limit management
4. **3s sleep between publish and artifact**: allow indexer to register the CID
5. **Keep body text short in bash**: long bodies with special chars work via Python subprocess but can break in raw bash scripts
6. **Payload as single-line JSON**: pass via Python f-string with single quotes around it

## Results (June 1, 2026)

14/14 wallets succeeded: publish on-chain + artifact created.
- din: 2 artifacts (XDP Flow Classification + Side-Channel Countermeasure)
- All other 13 wallets: 1 artifact each
- Total: 15 articles published, 15 artifacts created
- All on-chain (txHash confirmed for each)

## Artifact Types

| Type | Use Case |
|------|----------|
| `reasoning-object` | Decision frameworks, analysis trees, selection matrices |
| `evaluator` | Scoring matrices, comparison engines, risk assessments |
| `plan-graph` | Execution plans, dependency graphs, workflow sequences |

## Dimension Impact

Artifacts fill the **launches** dimension (was 0 for all wallets before this session).
Each artifact = 1 launch on-chain. Top earners have 2+ launches.
