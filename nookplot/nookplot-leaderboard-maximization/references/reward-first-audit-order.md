# Reward-first audit order for multi-wallet Nookplot sweeps

Use this reference when the user says things like "fokus yang ada reward dulu", "misinya dulu", or asks for a full-cluster audit but wants the profitable surfaces ranked before any social/KG work.

## Core lesson

Do the reward audit in this order and stop pretending lower-ROI surfaces are equivalent:

1. `check_mining_rewards` across all wallets first
   - Goal: find actually claimable `epoch_verification`, `epoch_solving`, `guild_inference_claim`
   - If all claimable balances are zero, say so clearly and do not talk as if claim routing is the active path.
2. `discover_verifiable_submissions`
   - This is the primary live reward surface when claimable balances are zero.
   - Prioritize 2/3 rows because they have the best finalize-speed EV.
3. `discover_mining_challenges`
   - Usually fallback only. If there is just one low-reward or tier-gated challenge, say it is fallback, not co-primary.
4. Open bounty / mission inventory via direct REST per wallet sample
   - If open count is zero, explicitly mark bounty/mission as dry right now.
5. Only after the above should you pivot to KG/social/commentary surfaces.
   - Those may still help score/reputation, but they are not the answer to a reward-first request.

## Reporting shape

For this user, report in a short, technical, action-first structure:

- claimable reward now
- open profitable queues now
- fallback reward surfaces
- blockers / limits
- exact next executable action

Avoid leading with long historical summaries when the user explicitly asked for reward-first execution.

For the stronger ask `ada yg bisa dikerjain lagi gak? yg ada rewardnya? coba analisa ulang untuk memastikan maksimal`, use `references/reward-reaudit-execute-pattern-may23.md`: run a fresh W1-W15 reward-first re-audit, execute safe live lanes immediately (verification canaries, bounty applications, KG/authorship gaps), then report landed IDs and blockers.

## Important nuance

Historical `totalEarned` is NOT the same as reward ready to harvest.
Always separate:

- `totalEarned` / historical accrual
- `claimableBalance` / mature reward available now

If `totalEarned > 0` but `claimableBalance` is zero across wallets, say:
- the wallets have historical earnings,
- but there is no mature claimable reward live now.

## Multi-wallet expectation management

If the user asks about all wallets 1-15, distinguish:

- what was actually audited across all wallets,
- what was only sampled,
- what was executed only on the active MCP-bound wallet.

Do not blur these together. The user explicitly checks whether "semua wallet 1-15 kan?" and expects a precise answer.

## Trigger phrases

Apply this reference when the user says any of:
- "fokus reward dulu"
- "misinya dulu"
- "yang ada reward dulu"
- "audit gap 1-15"
- "semua wallet 1-15 kan?"

## Session-derived example

A productive reward-first audit looked like:
- `check_mining_rewards` on W1-W15 => all claimable balances zero
- `discover_verifiable_submissions` => 20 live verification targets, several at 2/3
- `discover_mining_challenges` => only one expert tier1 challenge around ~599 NOOK
- direct bounty inventory sample => open bounty count zero

Correct conclusion:
- no ready-to-claim reward now,
- no open bounty/mission now,
- verification queue is the only materially live reward surface,
- mining challenge is fallback only.

This is the shape to preserve in future sessions.