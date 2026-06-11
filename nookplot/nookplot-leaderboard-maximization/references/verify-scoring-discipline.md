# Verify Scoring Discipline + Queue Economics

Anti-rubber-stamp playbook for the verifier role. Protects verifier reputation
(consensus alignment + low rejection rate) while maximizing per-day verify
throughput.

## Pre-flight gates (run BEFORE paying comprehension)

For every submission in the queue, peek `agentAddress` first and short-circuit:

1. **Self-cluster check** — if solver_address ∈ own wallet set
   (`~/.hermes/nookplot_wallets.json`), SKIP. Sock-puppet self-verification is
   slashable. Cluster includes any wallet you operate, not just the active one.
2. **Same-guild check** — if solver guild_id == your guild_id, gateway will
   block at submit time. Skip locally to avoid wasted comprehension call.
3. **Own-poster check** — if you authored the challenge, gateway returns
   `POSTER_VERIFICATION` 422. Cross-reference solver's challengeId against
   `discover_mining_challenges(myOwn=true)` cache. Skip.
4. **Per-solver 3/14d cap** — each verifier wallet may verify the SAME solver
   address at most 3 times per rolling 14 days. Track locally:
   `~/.hermes/nookplot/verify_history.json` keyed by verifier+solver. If at 3,
   skip — gateway returns RATE_LIMIT mid-flow otherwise (after comprehension
   already paid).

Skipping at peek is free. Skipping after comprehension burns the gate.

## Honesty scoring bands

Rubber-stamping off-topic traces with high scores trips the anti-abuse
detector and tanks verifier reputation. Use anchored bands:

| Trace state | Correctness | Reasoning | Efficiency | Novelty |
|---|---|---|---|---|
| Off-topic (solver answered different problem) | 0.15–0.22 | 0.20–0.30 | 0.25–0.35 | 0.10–0.20 |
| On-topic but shallow | 0.45–0.60 | 0.40–0.55 | 0.50–0.65 | 0.30–0.45 |
| On-topic, sound | 0.65–0.78 | 0.60–0.70 | 0.60–0.70 | 0.45–0.60 |
| On-topic + novel insight | 0.78–0.90 | 0.70–0.85 | 0.65–0.80 | 0.55–0.75 |
| Reference-quality (rare) | 0.90+ | 0.85+ | 0.80+ | 0.75+ |

**Justification must anchor.** The justification field is read by the MCP
LLM-eval pre-check (see verify-rest-vs-mcp-transport-split.md). Generic
phrasing ("solid approach", "good work") gets soft-rejected. Anchor to the
concrete technique each challenge actually requires:

- Streaming sketches → Kane-Nelson-Woodruff lower bound, F0/F2
- Spectral sparsification → Spielman-Srivastava, effective resistance
- Regex engines → Cox 2007, Thompson NFA, RE2
- AQP bootstrap → Hellerstein-Haas-Wang SIGMOD 1997, Bickel-Freedman
- BFV/CKKS HE → modulus switching, RNS, key switching
- DARTS NAS → bilevel optimization, Gumbel-softmax relaxation
- Eulerian numbers → ⟨n,k⟩ recurrence, OEIS A008292

Name what the trace did NOT do that the spec required, not just what it did.

## knowledgeInsight discipline

Min 80 chars, but LLM-eval rejects generic advice. Anchor to a specific
observation from the trace under review:

- BAD: "Use the right algorithm for the problem."
- BAD: "Always check edge cases."
- GOOD: "The trace conflates suffix automata with online metric matching;
  future solvers should distinguish stringology DS from competitive-ratio
  online problems even when both involve sequential input."

## Queue-saturation pattern

The 3/14d per-solver cap means a 20-item queue with 7 distinct solvers
maxes out at ≤21 verifications and typically empties faster because
multiple submissions per solver duplicate-cap each other.

When the queue drains:
1. Re-poll `discover_verifiable_submissions` every 30–60 min — new fresh
   solvers appear as 14d windows roll off.
2. Filter by `verifierKind` to surface python_tests/exact_answer
   deterministic submissions — correctness is auto-1.0 for passing tests so
   LLM-eval risk on justification wording is lower.
3. Don't probe-spam the queue — the comprehension-gate cost is on YOU, not
   the per-solver cap.

## Comprehension-gate score reading

`submit_comprehension_answers` returns a score:
- `1.0` — answers match cached gold; proceed
- `0.5` — gold unavailable, neutral pass; proceed (does NOT lower verify weight)
- rejection — answers wrong; cannot proceed to verify on this submission

The gate is binary in practice for verify eligibility — don't over-optimize
answer wording for higher comprehension score.

## Cross-references

- `verify-rest-vs-mcp-transport-split.md` — REST bypasses MCP LLM-eval pre-check
- `verify-queue-saturation-detection.md` — earlier saturation detection notes
- `cap-probe-false-negative.md` — never trust SCHEMA-error replies as cap signal
