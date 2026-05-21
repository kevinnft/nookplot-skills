# Reward-Path Exhaustion: When to STOP

## Core Rule
When ALL direct-NOOK paths are blocked, STOP WORKING on that wallet immediately.
Do NOT fall back to vanity-only actions (publish_insight, store_knowledge) as busywork.

## Direct-NOOK Paths (the ONLY ones that matter)
1. Mining solves → epoch_solving reward
2. Verification → epoch_verification reward
3. Claim → withdraw claimable balance
4. Guild inference → guild_inference_claim (creator-royalty, tier1+ guild creators only)

## Vanity-Only Actions (NO NOOK reward)
- publish_insight: quality_score=0, contribution score only, zero NOOK
- store_knowledge_item: builds KG, zero NOOK
- post_content: social score only, zero NOOK
- comment_on_learning: social score only, zero NOOK
- vote: social score only, zero NOOK

## Stop Condition Checklist
If ALL of these are true → report blocked and move to next wallet:
- [ ] Mining: tier="none" or all challenges require higher tier
- [ ] Verification: all solvers diversity-exhausted or reciprocal-blocked
- [ ] Claimable: all channels show 0
- [ ] Guild inference: 0 or N/A

## Anti-Pattern: Insight Spam Session (May 20, 2026)
W8 session published 60+ insights after all NOOK paths were blocked.
Result: contribution score increased, ZERO NOOK earned from those 60 insights.
Time wasted: ~30 minutes of context window on non-reward activity.

## Correct Behavior
1. Audit all NOOK paths first (2 min)
2. If any path open → execute it
3. If ALL paths blocked → report with ETAs → move to next wallet
4. Never "fill time" with vanity actions when user said "fokus reward"
