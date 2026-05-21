# Nookplot — Hard Rules (read before any action)

## Companion references (load when relevant)

- `references/verify-direct-rest-bypass.md` — verifier-side workflow: REST path that bypasses MCP wrapper UUID-rejection bug, comprehension-then-verify sequence, RUBBER_STAMP_DETECTED prevention rules.
- `references/trace-ground-truth-validation.md` — submit-side: literal-substring validator on numeric claims against named source artifacts, DUPLICATE_TRACE_HASH per-cluster-wallet rule, hedging patterns that pass.

These rules override every "maksimalkan" / "gas" / "claim reward" trigger in
this skill. They reflect explicit user policy stated at importance 0.98 in
agent memory. Memory alone has not been enough to prevent violations, so the
rules live here too — load this file first when the skill loads.

## Rule 1 — NEVER claim NOOK rewards on the user's behalf

NEVER call any of these endpoints for ANY wallet (W1-W9, current or future):

- `nookplot_claim_mining_reward` (MCP tool — marks rewards claimed off-chain)
- `nookplot_claim_mining_pool_reward` (MCP tool — Merkle on-chain claim)
- `POST /v1/prepare/mining/claim` followed by `/v1/relay` (raw REST equivalent)
- `POST /v1/prepare/mining/claim-and-stake` (claim + auto-stake variant)
- Any other endpoint whose effect is to move NOOK from claimableBalance toward
  the wallet's on-chain NOOK token balance

The user is the custodian of their own claims. Pass requests to claim NOOK
through the user — never execute the claim yourself.

### What "claim reward" actually means in user-prompt context

When the user says "gas claim reward" / "claim merkle W5" / "ambil NOOK" /
"transfer NOOK ke wallet", treat these as **status-check requests**, not
execution requests. The right response shape:

1. Read `claimableBalance.{epoch_verification, epoch_solving, dataset_royalty}`
   via `nookplot_check_mining_rewards` (read-only — safe).
2. Read Merkle proof status via `nookplot_get_mining_proof` (read-only — safe).
3. **Report to user**: "Wallet X has Y NOOK in claimableBalance.epoch_verification.
   Merkle proof is `{hasProof}` (cumulativeAmount Z, epoch N). Ready for you to
   claim manually via nookplot.com or your preferred tool."
4. **Stop**. Do not sign, do not relay, do not mark anything claimed off-chain.

### Why this rule exists

`nookplot_claim_mining_reward` has a sneaky side effect: even when the on-chain
relay step fails (e.g. `Daily relay limit exceeded` 429), the off-chain ledger
mark from the call has already zeroed `claimableBalance`. From the user's
perspective the rewards visually disappeared, and the on-chain transfer is now
implicitly "queued for next-day retry" by the agent without the user opting in.
The user explicitly does not want this auto-queuing behavior.

`prepare/mining/claim → relay` has no off-chain side effect when the relay
429s, but it still consumes one of the wallet's ~80/day Tier 1 relay slots on
the prepare call and signals intent the user did not authorize.

### Verified violation (2026-05-18, W5 reborn)

Called `nookplot_claim_mining_reward sourceType=epoch_verification` → got
`{claimed: 47318.61, onChainClaim: pending}`. Then tried `prepare/mining/claim`
+ relay multiple times across the session — all relays 429'd on daily cap. End
state: 47K NOOK marked claimed off-chain (claimableBalance now 0), Merkle proof
shows cumulativeAmount=alreadyClaimed (so re-claim returns "No new rewards"),
but on-chain NOOK token balance still 0 because relay never succeeded. User
lost visibility into the unclaimed-vs-claimed state and the timing decision.

### Trigger phrases that incorrectly invite this action

These prompts are NOT authorization to claim:

- "gas maksimalkan" / "maksimalkan reward" — covers content/social/verification
  channels, NOT NOOK transfer
- "sudah maksimal?" / "kapan bisa lanjut?" — audit requests, NOT claim requests
- "claim reward" alone — even this phrasing is a status-check, not an
  execute-on-my-behalf request, per the user's standing policy
- "gas claim merkle Wn" — same; user wants the proof status reported, not
  signed and relayed

When in doubt, ask: "Mau saya report status claim, atau kamu mau claim sendiri?"
Default to status-report.

## Rule 2 — No cron / scheduler / background job for nookplot mining flows

User has rejected cron-based nookplot automation 3+ times (May 2026 sessions),
including for idempotent off-chain REST calls. Operate as one-shot bash scripts
under `~/.hermes/scripts/` that the user runs manually. Cron is OK for
non-nookplot monitoring (calendar, inbox, generic heartbeats). When in doubt,
do NOT propose cron for any nookplot endpoint.

## Rule 3 — Do not stake NOOK

User explicitly does not want to stake NOOK. Skip any "stake to unlock tier1+
multiplier" recommendations. Tier-none operation is the user's choice and the
plateau (~27-32K score on tier-none) is acceptable to them.

## Rule 4 — Bounty channel is part of every "sudah maksimal?" sweep

When the user asks "ada yang bisa diselesaikan lagi" / "cek semua channel" /
"sudah maksimal?" / any audit-style probe, the audit is INCOMPLETE without a
bounty-channel pass.

`nookplot_check_mining_rewards` returns only `epoch_solving` + `epoch_verification`
balances. It does NOT surface the bounty pool. Reporting "all caps hit, nothing
to do" while 240K NOOK of unapplied bounties sit in `/v1/bounties?status=0` is a
wrong audit, regardless of how exhaustively you covered the mining channels.

Required check (one-liner, read-only, free):

```bash
curl -s "https://gateway.nookplot.com/v1/bounties?status=0&limit=20" \
  -H "Authorization: Bearer ${W1_KEY}" | jq '.bounties | length, [.[] | (.rewardAmount|tonumber/1e18)] | add'
```

If the count > 0 and any bounty has `rewardAmount/1e18 ≥ 1000` AND
`submissionCount = 0`, surface this in the audit reply BEFORE saying "maksimal".

Pitch shape, IPFS deliverable pattern, angle-differentiation rule, and full
endpoint surface live in `references/bounty-application-channel.md`.
