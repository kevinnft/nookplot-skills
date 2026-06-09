# Gateway Inference Architecture & BYOK Limits

Mapped 2026-05-24 by probing `gateway.nookplot.com` REST endpoints with kaiju8
API key. This is the durable architecture, not session-specific failure state.

## Two-layer provider gate

`/v1/inference/chat` enforces provider acceptance in **two layers**, both must pass:

| Layer | Allowed values | Failure mode |
|---|---|---|
| 1. Whitelist | `anthropic, openai, minimax, openrouter, ollama, venice, mock` | 400 `"provider must be one of: ..."` |
| 2. Server-side config | Only providers the gateway operator has wired up | 400 `"Provider 'X' is not configured."` |

`nvidia` IS visible in `/v1/inference/models` (7 models) but **fails layer 1** —
the models listing is independent of the inference whitelist. Don't trust the
models endpoint as a list of usable inference targets.

As of 2026-05-24 the only provider passing both layers is **`openrouter`**.
`ollama` passes layer 1 + 2 but fails on model name (`"Invalid model 'X' for
provider 'ollama'."`) because the configured Ollama instance has no models we
can name.

## BYOK does NOT unlock unconfigured providers

`POST /v1/byok` with `{provider, apiKey, baseUrl}` returns
`{"provider": "...", "stored": true}` for every whitelist provider. **This is
storage-only.** It does NOT register a previously-unconfigured provider for
inference. After successfully BYOK-ing `anthropic`, `openai`, `minimax`,
`venice`, the inference call still returns `"Provider 'X' is not configured."`.

Memory entry that previously claimed "Unlock = BYOK anthropic/openrouter key"
was wrong. The accurate statement: BYOK overrides the server-side key for
**already-configured** providers; it cannot promote an unconfigured provider.

## Discovery probe

To identify which providers are actually usable in a fresh session:

```python
# Probe each whitelist provider with a dummy submission
for prov in ['anthropic', 'openai', 'minimax', 'openrouter', 'ollama', 'venice']:
    print(prov, post("/v1/inference/chat", {
        "messages": [{"role": "user", "content": "x"}],
        "provider": prov,
        "model": "test",
        "max_tokens": 1
    }))
```

Outcome interpretation:

| Response | Meaning |
|---|---|
| 500 `"Provider error."` | Layer 1 + 2 OK. Upstream call failed (model name, API key) |
| 400 `"Invalid model 'X' for provider '...'."` | Layer 1 + 2 OK. Provider configured. Model name wrong |
| 400 `"Provider 'X' is not configured."` | Layer 1 OK, layer 2 FAIL. BYOK won't help |
| 400 `"provider must be one of: ..."` | Layer 1 FAIL. Provider not whitelisted at all |

## Submission endpoint bypasses inference entirely

This is the durable unblock when LLM is broken: `/v1/mining/challenges/{id}/submit`
does NOT call inference and does NOT validate any provider field. It accepts
the trace content the agent supplies via `traceCid` (IPFS upload) + `traceHash`
+ `traceSummary`. Author traces by hand (or with any out-of-band LLM) and submit
directly. The CLI's `nookplot mine` always routes through `/v1/inference/chat`
and is therefore unusable when no provider is wired; the REST submission path
is unaffected.

The full submit flow is already documented in
`references/submission-lifecycle.md`. The point here is just: when the CLI
mine loop is dead, don't try to repair the LLM path — switch to direct
submission.

## CLI source map (for next time the mine loop fails silently)

```
@nookplot/cli/dist/commands/mine.js
  └─ require('@nookplot/runtime')                       # nested under cli/node_modules
      └─ runtime/dist/mining.js
          └─ defaultKnowledgeSolver
              └─ this.economy.inference(...)            # runtime/dist/economy.js
                  └─ POST /v1/inference/chat            # provider field carried from yaml
```

Files (paths are relative to the npm install root,
`/home/ryzen/.hermes/node/lib/node_modules/`):

- `@nookplot/cli/dist/commands/mine.js` — CLI entry, builds embedder + solver wiring
- `@nookplot/cli/dist/utils/miningCapabilities.js` — detects `ANTHROPIC_API_KEY` etc., produces "anthropic available" log line that does NOT correspond to what gets sent
- `@nookplot/cli/node_modules/@nookplot/runtime/dist/mining.js` — `defaultKnowledgeSolver`, `defaultRlmSolver`
- `@nookplot/cli/node_modules/@nookplot/runtime/dist/economy.js` — `inference()` POSTs `/v1/inference/chat` with provider from yaml
- `nookplot.yaml` `mining.provider` field is what reaches the gateway

The "anthropic available" detection in miningCapabilities is misleading. It
reflects which env vars are set, NOT which provider name will be sent. The
yaml value wins.

## Connectivity diagnostic for stuck local proxies (enowxlabs etc.)

When the CLI hangs without progress and you suspect the local LLM proxy:

```bash
# 1. TCP open?
timeout 3 bash -c 'echo > /dev/tcp/HOST/PORT' && echo OPEN || echo CLOSED

# 2. HTTP responsive?
curl -v -m 10 http://HOST:PORT/v1/models
```

Pattern observed: TCP `OPEN`, HTTP times out at 10s with no bytes received.
That's the signature of a local proxy whose listener is alive but worker pool
is wedged (deadlocked thread, hung upstream, etc.). It is NOT the same as the
proxy being down — restart is required, port-scan won't reveal it.

Per user rule: don't restart enowxai automatically. Report to user, fall back
to direct-submission with hand-authored traces.
