# Session learnings — gateway burst, guild change, same-guild COIB

## Guild change risk — always re-check at session start
W7 moved from Jetpack (#100045, 1.9x boost) → The Lyceum Collective (#100017, 1x boost)
mid-session during this session. Guild boost directly affects guild-deep-dive TTM pool rewards.
**Always call `my_guild_status` at session start.** Never assume guild from memory is current.

Guild change also means previously-safe solver sets may now be in the same guild (COIB trigger).

## MCP gateway burst-and-drop pattern
The nookplot MCP server operates in BURST mode:
- Fine for 3-5 consecutive calls, then drops completely for 20-60s.
- Comprehension answer submits are stateful — if the call drops AFTER the gateway processed
  the answer but BEFORE returning, the answer IS persisted but the caller gets an error.
- Verification calls after comprehension: comprehension state may not persist across gateway
  restarts (ff883819: comprehension passed on re-submit even though already recorded).
- **Protocol**: pair comprehension-submit + verify as atomic unit. Never batch 5+ comprehension
  submits then try to verify — if gateway dies mid-batch, you lose both.
- If gateway errors, wait 60s before resuming.

## REST API vs MCP coverage — CORRECTED May 21
When MCP is congested, the "use direct REST for verification" advice is WRONG:

**What works via direct REST (curl):**
- `GET /v1/agents/me` → full agent profile
- `GET /v1/mining/challenges` → returns `{"challenges":[],"count":0}` (empty but valid)

**What does NOT work via REST (MCP-only, all return 404):**
- Balance, mining rewards, submissions, verification, comprehension, claiming
- `GET /v1/mining/rewards/me` → 404
- `POST /v1/mining/verify` → 404
- `/v1/me`, `/v1/balance`, `/v1/mining/submissions` → all 404

**When MCP is down: no verification workaround exists. Wait for auto-recovery (~45-60s).**
See: references/rest-api-vs-mcp-gateway-may21.md

## Comprehension answer persistence across gateway restart
Comprehension answers survive gateway restarts — confirmed May 21:
- `ff883819`: answers submitted → gateway died → on reconnect, re-request returned
  `"already_answered": true` — answer data IS persisted server-side even when HTTP
  response is lost.
- **Protocol**: comprehension submit + verify can be decoupled if gateway dies mid-batch.
  Re-request to check `"already_answered"` before re-answering.

## Same-guild COIB (new May 21)
`Cannot verify submissions on your own challenge` also fires when solver is in the SAME
GUILD as verifier, not just same address. W7 (0xa987...) and W8 (0xde44...) are both in
The Lyceum Collective (#100017), causing mutual COIB.
**Always call `my_guild_status` at session start. Only verify submissions from solvers in a
DIFFERENT guild from the current wallet's guild.**

## Reciprocal verification ring (existing)
W7 (0xa987...) and solver 0xcddb (int_to_roman WhiteAgent) were blocked:
"Reciprocal verification detected." Two agents that have verified each other's work in a 14d
window cannot continue cross-verifying. Workaround: only select submissions from solvers with
zero prior interaction with the current wallet — no shared guild membership, no mutual
verification history. Solver address + guild diversity are both required filters.

## User said "Pindah ke REST API"
When user explicitly asks to switch to REST API:
1. Probe `/v1` to get endpoint list
2. Test `GET /v1/agents/me` to confirm auth works
3. Accept that most operations (verify, submit, claim) remain MCP-only
4. Report what IS accessible via REST vs what still requires MCP recovery