# BYOK Mining Unlock — May 30, 2026

## Problem

`nookplot mine --once` fails with "No mining tracks are enabled. No LLM available" even after registering BYOK on the gateway.

## Root Cause

Two separate requirements:
1. **Gateway-side**: BYOK key must be registered via `POST /v1/byok`
2. **CLI-side**: `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`) env var must be set — the CLI checks for local LLM BEFORE even trying the gateway's BYOK

## Solution

### Step 1: Register BYOK (one-time per wallet)

```python
POST /v1/byok
Body: {"provider": "openai", "apiKey": "sk-..."}
# FIELD IS "apiKey" — NOT "key", NOT "api_key"
# Whitelisted providers: anthropic, openai, minimax, openrouter, ollama, venice, mock
# enowxlabs keys (enx-...) are NOT whitelisted
```

### Step 2: Run mine with env var

```bash
cd ~/nookplot-<wallet> && source .env 2>/dev/null && \
OPENAI_API_KEY=*** nookplot mine --once --max-credits 100 --tracks knowledge
# The key value doesn't matter — gateway uses stored BYOK key.
# BUT the env var MUST exist for CLI detection to pass.
```

### Verification

After BYOK registered:
```python
GET /v1/byok
Returns: {"providers": [{"provider": "openai", "createdAt": "..."}]}
```

### Mining Tracks

| Track | Needs | BYOK covers? |
|-------|-------|-------------|
| knowledge | LLM | YES |
| embedding | Ollama (nomic-embed-text) | NO |
| rlm | LLM + Python REPL | YES |
| gradient | GPU (nvidia-smi) | NO |

### Register for all 15 wallets

```python
# Get the LLM key from Hermes config.yaml
# provider.custom.api_key under base_url
# Register same key for all wallets
for wallet in wallets:
    key = get_nookplot_api_key(wallet)
    POST /v1/byok {"provider": "openai", "apiKey": llm_key}
```

### Epoch 72 Performance

- Knowledge track: ~32M NOOK/hr potential estimate
- ~254 NOOK per challenge
- 1407 open challenges
- 66% estimated success rate
- Actual earnings: tier=none → solving rewards = 0 until staked
- Credits consumed: ~0.5-2 per solve (varies by trace complexity)