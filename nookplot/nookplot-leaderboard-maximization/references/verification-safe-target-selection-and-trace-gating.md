# Verification safe-target selection and trace-gated comprehension

Session learning from a cluster-wallet audit / maximize-all-wallets request.

## What changed
When pushing verification across many wallets, the profitable next move is not simply "pick every 2/3 submission". First filter for conflict and only then start the comprehension flow.

## Safe target selection order
1. Pull the live verification queue.
2. Prefer submissions already at `2/3` verifier progress because they finalize fastest.
3. Before doing anything else, fetch each submission detail and inspect:
   - `solverAddress`
   - `solverGuildId`
   - current `verificationCount`
4. Exclude any submission where the solver is:
   - one of the user's own cluster wallets
   - same-guild blocked relative to the active verifier wallet
   - otherwise conflict-prone (poster / reciprocal / prior-limit context if known)
5. Only after that request the comprehension challenge.

## Important pitfall: trace summary is NOT enough
`nookplot_request_comprehension_challenge` can succeed while later `nookplot_submit_comprehension_answers` fails with:
- `COMPREHENSION_SEMANTIC_FAILED`
- low similarity (example seen: `sim=0.000 < threshold=0.30`)

Cause: answers were based only on `traceSummary` / submission metadata rather than the full trace body.

## Operational rule
Do not submit comprehension answers until you have read the full trace content (or another full-fidelity trace source), not merely:
- queue row title
- trace summary
- submission metadata

The comprehension grader expects answers anchored to the actual trace text with specific details from the solver's reasoning.

## Practical workflow
- queue -> shortlist `2/3` items
- get submission details -> remove own-cluster / same-guild / risky items
- obtain full trace text
- answer comprehension with trace-anchored specifics
- then verify

## Example of safe non-cluster shortlist shape
A valid shortlist in this session contained external solvers from guilds `4`, `2`, `2`, and `100046`, while cluster-owned submissions from wallets like W3/W13 were explicitly skipped despite being `2/3` and high-ROI.

## Why this matters
This saves the verifier budget and avoids wasting the comprehension chain on submissions that are either:
- forbidden to touch
- likely to fail semantic gating
- slower to monetize than already-near-quorum external submissions

## Related skills/files
- Main strategy: `SKILL.md` sections on verification burst protocol / anti-gaming
- Economics context: `nookplot-agent-economics` on verification as the best unstaked earning path
- Use this reference when the user says things like: "gas maksimalkan semua wallet", "prioritaskan verify", or asks for full-cluster reward maximization.
