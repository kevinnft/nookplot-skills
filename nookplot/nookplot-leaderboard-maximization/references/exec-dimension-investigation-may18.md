# `exec` contribution dimension — empirical investigation (May 18 2026)

## TL;DR

The `exec` contribution dimension (cap 5000) is **effectively unreachable** from
our 9-wallet cluster's REST surface as of May 18 2026. Eight feeder hypotheses
were directly tested on W3 (a fresh wallet at `exec=0`) and **none produced a
delta**. Treat `exec` as a non-farmable dimension until either:
1. Gateway publishes the real feeder mechanism, or
2. We deploy a hosted Agent Runtime SDK process (the empirical evidence below
   suggests the leaderboard's `exec` winners all run persistent hosted runtimes,
   not REST-driven sessions).

## Cluster snapshot (the puzzle)

| W   | name      | exec | submissions | verified-det | RLM workspaces | sandbox_exec calls |
|-----|-----------|------|-------------|--------------|----------------|--------------------|
| W1  | hermes    | 0    | 50+         | 18           | 1              | 5                  |
| W2  | 9dragon   | 554  | 50+         | 10           | 1 (empty)      | 8                  |
| W3  | kevinft   | 0    | 16          | 2            | 0              | 8 (test)           |
| W4  | aboylabs  | 0    | 17          | 4            | 0              | 10                 |
| W5  | reborn    | 0    | 13          | 1            | 0              | 8                  |
| W6  | satoshi   | 0    | 8           | 0            | 0              | 0                  |
| W7  | badboys   | 0    | 6           | 2            | 0              | 10                 |
| W8  | rebirth   | 0    | 12          | 2            | 0              | 0                  |
| W9  | john      | 0    | 13          | 2            | 0              | 0                  |

Only W2 has nonzero `exec`. Cause is **not visible** in any REST-readable signal.

## Hypotheses tested (all FAILED)

| # | Hypothesis | Test | Result |
|---|------------|------|--------|
| 1 | `/v1/exec` direct sandbox calls | 3 calls on W3 (no projectId) | exec stayed 0 across 6 min recompute window |
| 2 | `/v1/exec` with `projectId` set | 5 calls on W3 (`projectId=kevinft-verifier-toolkit-v1`) | exec stayed 0 across 6 min |
| 3 | `verifiedDeterministically=true` mining submissions | W1 has **18** vs W2's **10** | W1 still exec=0, W2 exec=554 — anti-correlated |
| 4 | RLM workspace REPL turns | W1 has math RLM workspace, W2 has empty `rlm-enzyme-test` | W1 exec=0, W2 exec=554 — workspace existence NOT the driver |
| 5 | `/v1/runtime/connect` + sustained heartbeats | W3: connect + 8 min of 60s heartbeats + disconnect | exec stayed 0 |
| 6 | GitHub-connected commit pushes | All 9 wallets show `connected: false` | not testable; W2 still got exec=554 without GitHub |
| 7 | `/v1/inference/chat` calls | `/v1/inference/history` empty for both W1 and W2 | not the source |
| 8 | `/v1/actions/log` action history | All 9 wallets show `entries: []` | not the source |

## Leaderboard pattern (top 200 scan)

- 23 of 200 wallets (11.5%) have `exec > 0`.
- Distribution is bi-modal: ~10 wallets at `exec=242` (sister-cluster bot
  family — Apex/Carbon/BigBrain/Overflow all share `commits=431`), and ~12
  wallets at `exec=3750` (capped tier — SatsAgent, jeff, Kimmy, zcybersecagent,
  zseniorresearcher).
- The current `runtime/presence` shows the `exec=3750` capped agents (SatsAgent,
  CodexAgent, kaiju8, SnappedAI) **always-online**, suggesting the true exec
  feeder is **WS /ws/runtime persistent SDK sessions**, not REST.

## Practical recommendation

Do NOT burn `/v1/exec` quota (10/hour per wallet) chasing this dimension.
Each call costs 0.51 credits and produces zero exec score for our cluster.
Other 9 dimensions (commits, lines, projects, content, citations, social,
collab, launches, marketplace) are higher-leverage and well-understood.

## Update trigger

Re-investigate when:
- Gateway publishes `/skill.md` documentation describing the exec feeder, OR
- A new agent-runtime CLI/SDK ships that we can deploy locally to maintain
  a persistent WS /ws/runtime session for our wallets, OR
- W2's `exec=554` value changes (would tell us the dimension still recomputes
  for live data; at the time of investigation it was static).

## Investigation scripts

Saved at `/tmp/exec_experiment.py` (single-wallet probe), `/tmp/cluster_audit.py`
(9-wallet scan), `/tmp/runtime_test.py` (heartbeat hypothesis test). Re-run
any of these after dimension shifts to localize the root cause.
