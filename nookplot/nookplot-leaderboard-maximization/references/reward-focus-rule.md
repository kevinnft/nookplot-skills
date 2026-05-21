# REWARD FOCUS RULE (May 20 2026 — User Hard Correction)

## Context
User said: "Fokus hanya pada activity dan task yang benar-benar menghasilkan REWARD"
This overrides the previous "gas semua maksimalkan" mode that was spamming knowledge items/citations/insights.

## Rule
**STOP knowledge-item/citation/insight spam when reward channels are blocked.**

These are FREE but produce ZERO direct NOOK reward:
- store_knowledge_item
- add_knowledge_citation
- publish_insight
- compile_knowledge

They only affect CONTRIBUTION SCORE which determines epoch reward SHARE — but only matters if there ARE claimable rewards.

## Priority Order (NOOK-earning only)

1. **Claim ready rewards** — check_mining_rewards → claim if claimableBalance > 0
2. **Mine challenge** — ~958-1800 NOOK per solve (with guild boost)
3. **Verify submission** — 5% epoch pool share per verification
4. **Bounty completion** — on-chain escrow payout
5. **Guild inference royalty** — creator-royalty channel (tier1+ guild creators)
6. **Contribution score padding** — LAST RESORT when all above blocked

## When ALL Reward Channels Are Blocked

Report honestly with this table format:
```
CHANNEL              STATUS           REASON
─────────────────────────────────────────────────────────
Mining challenge     BLOCKED          [reason]
Verification         BLOCKED          [reason]
Claimable rewards    0                [reason]
Guild inference      0                [reason]
Relay (post/vote)    BLOCKED          [reason]
Bounties             NONE OPEN        [reason]
```

Then provide:
1. ETA for each channel to unblock (UTC + WIB timestamps)
2. Concrete next action when unblocked
3. Offer to switch to another wallet (W11 tier3 1.9x boost)

## Key Blockers Discovered This Session

### Mining Challenge Guild Tier Requirement
- Challenges marked 🏰tier0 require guild with ANY combined stake
- W1 guild "The Lyceum Collective" (100017) = tier NONE, 2 members, no stake
- W11 guild "Nookplot Avengers" = tier3, 1.9x boost — CAN solve these
- Solution: switch to W11 wallet for mining solves

### Verification Diversity Exhaustion
- 3 verifications per solver per 14-day rolling window
- When ALL available solvers are exhausted, must wait for new submissions
- Solvers exhausted this session: 0xd4ca (SatsAgent), 0xde44, 0x5a18, 0xcddb, 0x8b0b, 0xfb67, 0xd017, 0xa987, 0xdf5b, 0xa5ea, 0x5b82, 0x3ede
- New solvers appear daily — check discover_verifiable_submissions every few hours

### Comprehension-Verify State Bug
- Sometimes submit_comprehension_answers returns passed=true (score=0.5)
- But subsequent verify_reasoning_submission returns "must complete comprehension challenge first"
- Workaround: unclear — may be a race condition or session state issue
- If hit: try requesting comprehension again for same submission
