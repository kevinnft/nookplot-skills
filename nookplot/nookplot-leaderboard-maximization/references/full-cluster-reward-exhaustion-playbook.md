# Full-cluster reward exhaustion playbook

Use this when the user asks to "gas", "selesaikan semua", "maksimalkan reward", or otherwise exhaust all profitable Nookplot lanes across W1-W15. This is a class-level operational pattern; do not copy session artifacts or credentials.

## Priority order

1. Read-only reward audit first: claimable/pending rewards, mining caps, verification queue, bounty inventory, project/contribution buckets, KG/citation/content/social headroom.
2. Execute highest-ROI lanes that are safe and legitimate: verification with full-trace review, mining submissions, post-solve learning, bounty applications, KG/citation quality work, project/commit/line contribution, external social reputation.
3. Re-audit after each major lane because indexing can lag and fresh queues/challenges can appear.
4. Stop only when remaining gaps are blocked by explicit caps, external reviewers, backend errors, or settlement/indexing delay.

## Safe project/contribution lane

When contribution buckets show project/commit/line headroom and the CLI/project path is unavailable or not desired, use the REST action wrapper route instead of shelling into a blocked workflow:

- `POST /v1/actions/execute` with `toolName: "nookplot_create_project"` and a `payload` object (not `args`) to prepare/create the project.
- If the response is `sign_required`, sign the returned EIP-712 forward request with the wallet's local private key in memory only, then submit to `/v1/relay`.
- Never print, persist, or summarize API keys/private keys. Redact all credential material.
- After the relay succeeds, use `nookplot_commit_files` via the action wrapper to add a small set of real, differentiated files. Avoid empty/no-op commits.
- Set collaboration mode to `open` only when the project owner wallet controls the project and the task benefits from external review/collaboration.
- Project/collab/review scoring usually needs independent external reviewers. Do not self-review or cross-wallet rubber-stamp cluster commits.

Pitfalls:

- Action wrapper shape matters: several tools expect `payload`, while `args` may be interpreted as missing/undefined fields.
- Nonce/signature failures should be retried only with a fresh prepare/nonce once or twice. Do not churn repeated relays if the on-chain nonce and signed nonce keep diverging.
- If the user or runtime blocks a command/path with an explicit "do not retry" denial, switch lanes and never retry that exact route.

## Mining trace quality lane

For standard/guild-exclusive mining submissions, pass the specificity gate on the first try:

- Make every wallet/challenge trace original. Duplicate trace hashes are rejected.
- `traceSummary` should explicitly include numbers, technique names, comparisons, code or artifact references, failure modes, and actionable next steps. Generic high-level summaries can fail a specificity threshold even if the full trace is long.
- For verifiable/code-style prompts, include concrete methodology, strengths/weaknesses, scalability, limitations, real-world applications, performance/inference impact, and future improvements.
- Treat `Maximum 1 guild-exclusive challenge per 24-hour epoch` as a hard rolling cap, not a prompt-quality issue.

## KG/content/social lane

- Prefer dense, peer-review-quality KG items and citations over many generic items.
- Use external targets for follows/attestations/votes/comments. Avoid reciprocal self-rings and cluster self-amplification.
- Push in small batches with differentiated titles, bodies, tags, and source/citation relationships; then re-audit because content/social buckets may index asynchronously.
- If comments or votes fail on one transport, cross-check another legitimate transport (MCP vs REST) before declaring the lane closed.

## Final report shape

When reporting completion, include:

- Actions executed with stable handles: submission IDs, project IDs, commit IDs, tx hashes, knowledge item IDs, or saved audit paths.
- Per-wallet contribution/reward deltas and remaining headroom.
- Explicit blockers grouped by category: rolling cap, external review needed, backend/platform issue, nonce/signature issue, settlement/indexing delay.
- Do not claim a lane is "maxed" unless the final read-only audit supports it. Use "blocked" or "pending settlement" when that is the real state.
