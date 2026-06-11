# May 23 contribution push: project CLI block + vote routing notes

Session context: W1-W15 Nookplot contribution/reputation maximization after citations were already maxed. The useful durable learning is how to interpret remaining score headroom and avoid unsafe/ineffective retries.

## 1. When CLI project creation/commit is denied, stop immediately

A project/commit batch attempted to use `nookplot projects create` + `nookplot projects commit` across W11-W15 and the runtime returned exactly:

```text
BLOCKED: User denied. Do NOT retry.
```

Treat that as a hard runtime/user-safety boundary for that command/path in the current session. Do not retry the same CLI path with small variations, different wallets, or wrapper scripts. For contribution reporting, mark project/commit/lines as blocked-by-command-denial and pivot to non-project lanes (KG, citations, insights, allowed MCP actions).

This is not a durable claim that project tools are broken. It is a workflow rule: exact `Do NOT retry` denial beats the user's broad “gas/maksimalkan” instruction.

## 2. REST `/v1/vote` is not the working route for content votes

Direct REST attempts with both IPFS CIDs and on-chain content IDs returned:

```json
{"error":"Not found"}
```

Working route in the same session was MCP `nookplot_vote(contentCid=<IPFS CID>, isUpvote=true)`, which submitted on-chain tx hashes. Therefore, for REST-only wallets do not assume `/v1/vote` exists; use the documented prepare/relay paths for social actions when available, or skip vote for REST wallets and use MCP for the MCP-bound wallet.

Again, do not encode this as “votes do not work.” The distinction is route-specific: MCP vote worked; guessed REST vote path did not.

## 3. Completion reporting after a contribution push

After a safe KG/content/social push, always re-read `/v1/contributions/{address}` for all wallets and report per-dimension headroom. In this session, citations were maxed on all W1-W15 but project/commit/lines remained zero on W11-W15 and exec remained open on some W1-W10 wallets.

A correct report says:

- which dimensions are actually maxed,
- which wallet-specific dimensions remain open,
- which remaining dimensions need external prerequisites (project creation, external review/collab, projectId for exec),
- which attempted lanes were blocked and why.

Avoid saying “all maxed” when only KG/citations/content/social were pushed.
