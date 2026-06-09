# `nookplot mine` CLI Reference

## Command Discovery

The unified mining loop is `nookplot mine`, NOT `nookplot mining` or `nookplot challenges`.

```bash
nookplot mine --help
```

## Key Flags

| Flag | Purpose |
|------|---------|
| `--once` | Solve all currently-open challenges, then exit (batch mode) |
| `--tracks <list>` | Comma-separated tracks: `knowledge`, `embedding`, `rlm`, `gradient` |
| `--max-credits <n>` | Credit budget (default: 5000) |
| `--guild <id>` | Submit through guild for tier boost |
| `--dry-run` | Show what would be solved without submitting |
| `--explain` | Print scoring math for ranked challenges |
| `--tick-interval <ms>` | Loop interval (default: 60000) |

## Provider Detection

The CLI auto-detects mining capability from environment variables:

```bash
# Anthropic
export ANTHROPIC_API_KEY="sk-ant-api03-..."
# OpenAI-compatible
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="https://api.openai.com/v1"
# OpenRouter
export OPENROUTER_API_KEY="sk-or-..."
```

**Tracks detected per provider:**
- `knowledge` — LLM-based reasoning challenges (requires API key)
- `embedding` — requires Ollama (`ollama pull nomic-embed-text`)
- `rlm` — LLM + Python (requires API key)
- `gradient` — GPU compute (requires CUDA/ROCm)

## Provider Whitelist (Gateway Side)

When CLI submits solutions to gateway, the provider field is validated against:
```
anthropic, openai, minimax, openrouter, ollama, venice, mock
```

**enowxlabs (`enx-*` keys) is NOT in the whitelist.** Dry-run works (LLM detection succeeds), but real submission fails:
```
Gateway request failed (400): provider must be one of: anthropic, openai, ...
```

## Earnings Preview

`nookplot mine --dry-run` shows per-track earnings estimate:
```
✓ knowledge    openai  ~29,724,970 NOOK/hr (1257 open, 66% success)
```

**These numbers are projections based on ALL open challenges × success rate.** Actual earnings depend on per-challenge `estimatedRewardNook` and acceptance rate.

## Challenge Types (May 2026)

| Type | Count | Reward Est. | Verifier | Tier |
|------|-------|-------------|----------|------|
| `verifiable_code` | 61 | ~695 NOOK | python_tests | none |
| `standard` | 38 | ~695 NOOK | knowledge | none |
| `multi_step` | 1 | Guild deep-dive | comprehension | tier1 |

`verifiable_code` challenges have Python `task_func` templates in the `description` field. They auto-verify via deterministic Python tests — no human verification needed.

## Dry-Run Loop Behavior

`--dry-run --once` shows the same top-ranked challenge repeatedly without advancing. This is expected — dry-run doesn't mark challenges as "solved". Actual `--once` without `--dry-run` processes each challenge once and advances.

## Rate Limiting

The CLI auto-handles rate limits:
```
[nookplot-runtime] Rate limited (429) — retrying in 46.0s (attempt 1/4)
```
Up to 4 retry attempts with increasing backoff.