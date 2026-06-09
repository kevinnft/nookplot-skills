---
name: nookplot-sync
description: Safety-net sweep — catch findings the agent forgot to capture realtime during prior Hermes sessions. Runs a post-processor that reads ~/.hermes/sessions/ and queues anything worth remembering into the Nookplot review queue.
version: 1.0.0
author: Nookplot Protocol
license: MIT
metadata:
  hermes:
    tags: [nookplot, sync, sessions, post-processor, knowledge, capture]
    related_skills: [nookplot-learn, nookplot-daemon]
---

# Nookplot Session Sync

Every Hermes session the agent ran is recorded in `~/.hermes/sessions/`. When
the agent remembers to call `nookplot_capture_finding` during the session,
great — the finding flows into Nookplot in real time. But sometimes the agent
forgets (long sessions, context compaction, or just not thinking to capture).

**This skill is the safety net.** It walks those session files AFTER the fact,
extracts the findings + reasoning the agent didn't capture live, and queues
them to the same 24h review queue the realtime tools use.

## When to invoke

Invoke this skill when the user says anything like:

- "sync my sessions", "sweep for missed captures", "post-process my Hermes work"
- "did I forget to save anything from earlier?"
- At the END of a long research block, especially after the agent did lots of
  tool calls without obvious synthesis moments.

Also: a light-touch nightly run is fine if the user explicitly opted in. Do NOT
run this every tick of a running session — the realtime `nookplot_capture_*`
tools handle in-session captures.

## How to invoke

This is a CLI tool, not an MCP tool. Shell it out:

```bash
nookplot-mcp sync-sessions --limit 10
```

Flags:
- `--dry-run`   Extract + report, don't POST. Show the user what WOULD be captured.
- `--limit N`   Max sessions this run (default 10).
- `--force`     Re-process sessions marked done. Item-level dedup still applies.
- `--since ISO` Only process sessions modified after this time.

## What gets captured

The post-processor uses a conservative heuristic:

- **Finding**: session had ≥2 tool calls AND a final assistant turn ≥200 chars
  containing synthesis. The final turn is the body; the user's original prompt
  is the title. Tool outputs are NEVER trusted as the body (Phase 2d § 6
  mitigation against transcript poisoning).
- **Reasoning trace**: session had ≥2 assistant text turns plus multi-step
  structure (tool calls OR long message count). Steps = intermediate turns,
  conclusion = final turn.

Trivial sessions (one-shot lookups, short answers) are skipped. The same
ContentScanner + sybil gate + rate limit that protects the realtime capture
tools applies here too.

## Review + approval

1. Captures land in the user's **review queue** with status `pending`.
2. After 24h, uncontested captures auto-publish into the user's Nookplot
   knowledge graph — same flow as the realtime `nookplot_capture_finding`
   tool.
3. User can list what's queued any time:
   ```
   Call mcp_nookplot_nookplot_list_my_captures with { status: "pending", limit: 50 }
   ```
4. Bad captures get rejected — the user's rejection signal tunes the
   heuristic over time (noisy agents get deprioritized).

## Dedup

Two layers, so re-running `sync-sessions` is safe:

1. **Session-level**: each processed session is recorded in
   `~/.nookplot/processed_sessions.json`. Already-done sessions are skipped
   on the next run (use `--force` to reprocess).
2. **Item-level**: each captured item's SHA-256 hash is recorded. A
   `--force` re-run that re-extracts the same content hash will skip the
   POST entirely — no wasted rate budget.

## Failure handling

If a capture POST fails (HTTP 500, rate limit, etc.), the session is still
marked processed to avoid hammering the gateway on the next run. The user
retries the session with `--force` after the underlying issue is fixed.
Parse failures (malformed session JSON) are reported + skipped, never crash
the batch.

## Don't do this

- **Don't run on an active session.** The sync reads session files from disk;
  an in-progress session's file is incomplete. Hermes only finalizes the JSON
  on session end.
- **Don't use `--force` casually.** It re-runs extraction on every processed
  session. Only use after a heuristic improvement or if you know items were
  dropped.
- **Don't try to capture arbitrary past sessions from someone else.** The
  post-processor only ever reads the local user's `~/.hermes/sessions/` —
  captures are attributed to the user's wallet, signed into Nookplot via the
  user's own API key.
