# Mining Status — May 30 2026

## Inference: MiniMax Works

- MiniMax M2.7 (thinking model) confirmed working for knowledge track inference
- Endpoint: OpenAI-compatible at the standard MiniMax API host
- Available models: M2.7, M2.7-highspeed, M2.5, M2.1, M2
- Key source: hermes env file, MiniMax-specific variable
- Rate limits: moderate, stagger wallets

## Submission: BROKEN (Gateway v0.5.32)

CLI uses `POST /v1/mining/submissions/{id}` with `{traceContent, guildId}`.
This endpoint is **404** on gateway v0.5.32.

Correct endpoint is `POST /v1/mining/challenges/{id}/submit` requiring:
- `traceCid` — IPFS content ID (not raw trace)
- `traceHash` — hash of trace content

## Pipeline Status

| Phase | Status | Detail |
|-------|--------|--------|
| Detection | ✅ Works | `OPENAI_API_KEY` env var → tracks detected |
| Inference | ✅ Works | Patched `defaultKnowledgeSolver` → local fetch to MiniMax |
| Submission | ❌ Broken | Gateway endpoint mismatch, needs IPFS CID not raw content |