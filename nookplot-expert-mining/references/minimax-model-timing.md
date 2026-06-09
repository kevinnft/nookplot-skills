# MiniMax Model Timing Benchmarks (June 1, 2026)

Tested against complex technical prompts (~500-1000 chars):

| Model | Time | Content | Notes |
|-------|------|---------|-------|
| `MiniMax-M2.7` | **60s+ TIMEOUT** | N/A | Thinking model. Hangs mining indefinitely. |
| `MiniMax-M2.7-highspeed` | ~45s | 8907 chars | Fast thinking variant. Usable but slow. |
| `MiniMax-M2.5` | **~18s** | 7151 chars | **RECOMMENDED for mining.** Fast + sufficient. |
| `MiniMax-M2.5-highspeed` | untested | — | Likely ~10s. |
| `MiniMax-M2.1` | untested | — | Older model. |
| `MiniMax-M2` | untested | — | Older model. |

**Thinking model quirk**: Both M2.7 and M2.5 wrap reasoning in `<think>...</think>` tags inside `content`. Patch #4 strips these before extracting traceSummary.

**Endpoint**: `https://api.minimaxi.chat/v1/chat/completions`
**Rate limit**: ~1-2 req/few seconds on free tier. Stagger 15s between wallets for multi-wallet mining.
**Auth**: Bearer token from .env INFERENCE_KEY variable.