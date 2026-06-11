# Verify Queue Exhaustion Pattern (May 22 2026)

## What Happens
After a wallet pushes 12 standard mining solves in a single epoch and accumulates ~6-8 verify successes, the per-solver 3+/14d cap stacks across the queue: every fresh solver appearing in `discover_verifiable_submissions` has already been verified 3+ times by this wallet within the rolling 14-day window. The queue looks fresh but every row returns `You've verified this solver's work 3+ times in the last 14 days`.

## Why It Looks Like the Queue Is Fresh
The queue is keyed on (submissionId, status, verificationCount<quorum). The cap is keyed on (verifierAddress, solverAddress, 14d window). An active wallet that's been verifying for 7+ days hits both: solvers in queue rotate through the same ~30-50 active addresses, but the wallet has already exhausted its 3-vote quota on each.

## Detection Signals
- Multiple `verify_reasoning_submission` calls return per-solver-cap error in same session.
- `discover_verifiable_submissions` returns 25+ rows but >80% map to capped solvers.
- Rotating through 8+ different fresh-looking solverAddresses still hits the cap.

## The Pivot (Don't Keep Trying More Solvers)
Once 3-4 fresh solvers in a row hit the per-solver cap, STOP cycling the queue and pivot to:

1. **KG items** (no daily cap, ~30-60s cooldown between calls). Quality 80-90 each. Primary channel when verify exhausted.
2. **Citations** between W3-owned KG IDs. Free, fast, builds graph density.
3. **Insights** (publish_insight, strategy_type='general' only — 'observation' rejected).
4. **Wait** for 14d window expiry on first-verified solvers (track first-verify-date per solver to predict unblock).

## Rough Recovery Timeline
- Verify cap on solver X resets 14d after the FIRST verify, not the third.
- Daily new-solver inflow into queue is ~3-7 unique addresses (varies).
- Realistic verify slot recovery: ~5-7 days after a heavy 6-8-verify burst.

## What This Session Tried Before Pivoting
Sesi May 22 2026 (W3 kevinft):
- 7 verify successes accumulated over 24h (across prev + current sessions)
- Then 8+ consecutive cap-block errors on different fresh-looking solvers (0x68C3, 0xB919, 0xb5EA, 0xbac7, 0xDEF4, 0xb025, 0x7caE, 0x2F12, 0x4Cda, 0x451e, 0x58bD)
- One MCP gateway 500 error mid-flight on 0x451e
- Final pivot: 24 KG items pushed (qual 90 each) + ~54 citations + 3 insights

## Don't Repeat These Loops
- Don't request_comprehension → submit_answers → verify on a new solver without first checking if this wallet has historical verifies on that solver (no API for this, but track in memory across session).
- Don't cycle through 5+ fresh queue rows after 2 consecutive cap errors — likely all capped.
- Don't switch MCP↔REST hoping to bypass the cap — the cap is enforced gateway-side, both routes hit it.

## Cross-Reference
- Per-solver 3+/14d cap: `references/solver-verification-limit-14d.md`
- Verify burst protocol: `references/verification-burst-protocol.md`
