# User Denial as Channel-Stop Signal

When the user runtime-denies (`"status": "blocked"`) 2+ tool calls in the same channel within a single session, that channel is OFF for the rest of the session. Don't rotate targets, don't retry, don't micro-variate.

## Channels in the nookplot push
- Mining submit (rare denial — usually cap-bound first)
- Verify (verify_reasoning_submission + comprehension chain)
- Comment grind (comment_on_learning batches)
- Insight publish
- KG store / add_to_knowledge_graph
- Endorse / attest / follow (gas-triggering — denials common)

## Observed pattern (May 22 2026 W8 push)
Denials clustered in this order:
1. verify HM 0xBa99 — denied
2. verify learned-index B-tree 0x7665 — denied
3. comment batch (Drift + 3 follow-ups) — denied

Channels affected: selective verify + comment grind. After denial #3, agent correctly stopped comment grind entirely and pivoted to final state report. No retry attempts with different solvers/learnings within the denied channels.

## Why the user denies (don't interrogate, just respect)
The user gates the agent on signals the agent can't always see:
- Self-collusion ring detection (target solver = user-asset)
- Quality gate (comment looks spammy/template-y)
- Gas-trigger risk (action would mutate on-chain unintentionally)
- Pure preference (this channel done for today)
- Detection-surface management (W8 burst optimization risk)

Don't generate post-hoc rationalization for why "this next attempt is different." It isn't.

## Wrong response
- Retry with different solver/target
- Switch to micro-variations (different learning ID, same comment template)
- Argue or ask "boleh kah kalau target X?"
- Pivot inside the same channel (e.g. comment denied → try `publish_insight` with comment-style content)

## Right response
1. Note the denial in working state.
2. Count denials per channel for this session.
3. At denial #2 in same channel: stop that channel for the session.
4. Pivot to a STRUCTURALLY different channel (verify → insight publish → KG store → final report).
5. If 3+ different channels denied: end the push, generate final state report.
6. Never persist the denied target list across sessions — gates are per-session/per-context.

## Final state report shape (when stopping)
Follow `sudah-maksimal-eta-reporting.md`:
- Per-channel cap status: HABIS / OPEN / BLOCKED-by-denial
- Successful action count + IDs/scores
- ETA per blocked channel:
  - Epoch reset: ~24h from first sub
  - Diversity (3/14d): rolling, hours-scale
  - Reciprocal: uncontrollable
  - User-denied: next session (do NOT promise retry)
- One-line recommendation: stay-and-wait OR pivot to other wallet (W7/W12/W14)

## Cross-reference
- `inline-pitfalls-may21-2026.md` — session-level pitfalls (separate concern)
- `verification-anti-gaming-constraints.md` — gateway-level gates (different signal class)
- `sudah-maksimal-eta-reporting.md` — reporting template
