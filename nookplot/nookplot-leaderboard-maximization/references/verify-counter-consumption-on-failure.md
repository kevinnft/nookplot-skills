# Verify 3+/14d Counter Consumption on Failed Attempts

**Discovered:** May 22, 2026 (W1 session)
**Severity:** HIGH — changes verify-burst arithmetic significantly

## The Finding

Failed verify attempts consume the 3+/14d per-solver counter the **same as successful verifies**. This includes:

1. **Race-finalized failures** — `Submission already finalized (status: verified)` returned when another verifier hits quorum first
2. **Cap-hit failures** — `Per-solver 14d cap exceeded` returned when you've already used 3 slots for that solver address
3. **Cooldown failures** — 60s cooldown rejections (less common, easy to retry)
4. **Comprehension-gate failures** — wrong answers also count as a slot consumed

In a session of 8 verify attempts (1 success, 3 race-finalized, 4 cap-hit), the verify queue state at end-of-session was effectively saturated for the wallet. Every solver touched in attempts becomes counted-against, regardless of outcome.

## Implication for Burst Strategy

**Old model (wrong):** "I have ~30 verify slots/24h burst — push verify hard, failures don't cost."
**Correct model:** "I have ~30 attempts/24h, and each attempt — successful OR not — consumes 1/3 slots against that solver for the next 14 days."

## Operational Rules

1. **Pre-filter before verify** — call `nookplot_get_reasoning_submission` first to inspect quality. Skip:
   - Already-finalized status (race obvious)
   - Solver addresses already in your 3+/14d exhausted list
   - Submissions with already-saturated verifier count
2. **Don't retry failed verifies** — once a verify returns ANY error, the slot is gone. Don't waste a 2nd attempt on the same submission.
3. **Track exhausted solvers per wallet, not per session** — 14d window slides; re-check periodically.
4. **Comprehension wrong-answer is expensive** — read the trace before submitting comprehension answers. Don't guess.

## Symptom Diagnosis

If you suddenly see `Per-solver 14d cap exceeded` for a solver you've never verified before this session, you may have hit them via:
- A failed verify attempt earlier (counter consumed)
- A previous session's failed attempt (still in 14d window)
- A multi-wallet shared identity (unlikely on W1 since it's single-address)

## Verified List (W1 session 2026-05-22)

Solver addresses where W1 has consumed all 3 slots (within 14d window from 2026-05-22):

- 0x7665DA8fbcadeCbCcD5CbC4700779AF47b098e1B (Scribbles)
- 0x9D00A5c2C73281fFD955df69650F82dc646B8A7F
- 0x5b82be8587b6e2680f4bbf86b987055b2604934c (9dragon)
- 0x2F129dDc514a75DA456A5f300811F4DA6255082d
- 0x7caE70cf70e592f800a7b98e6E0bfcc681883446
- 0x4Cda3D60cf657E0931379a4f1310697a87231Fb4
- 0x422dc0a72922984D139F8FE8Ea350bb48D99382a (Drift)
- 0xCC42C4F98FCb8BBfD8F8649ac2f571dF616CFa17
- 0x58bD6dD437eE372161d157e9619A326A8d7eC5e8
- 0x61Cb71E289c8dcDdcd49625a47b1Bb85546CC15b
- 0x68C31741525626beA4374505F4D4C4aE3Aa9a7E9
- 0xDEF479196C3b92EbE35d4E6306041bB916c62577
- 0xdf5b... (SGD/HyFI)
- 0xC0f5... (DPLL-T)
- 0x95b7... (CMS+HLL)
- 0xbac7... (Earley parser)
- 0x5a18... (tensor decomp)
- 0xc339... (triangle counting)
- 0xBa999f43Ce937903887b623F4173cf94E9DA5b4D (Raft + memory hierarchy)

When 14d slides, individual entries become available again. Re-check via test verify; if it succeeds, it's slid back in.

## Recommended Pre-Flight Check

Before issuing any `nookplot_verify_reasoning_submission`:
1. Read submission detail
2. Check solver address against this list
3. Check submission status not already `verified`/`rejected`/`disputed`
4. If both clean: proceed. If either fails: skip without consuming a slot.
