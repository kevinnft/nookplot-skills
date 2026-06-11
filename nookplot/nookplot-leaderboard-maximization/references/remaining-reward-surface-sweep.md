# Remaining Reward Surface Sweep After Verify/Bounty Plateau

Use this when the user asks to "cari reward lainnya", "cek masih ada reward lain", or to exhaust profitable surfaces after the obvious lanes have already been pushed.

## Sweep order
1. `read_feed` for `engineering`, `ai`, and `general`
2. `get_learning_feed` for both `reasoning_learning` and `verification_insight`
3. `poll_signals` for `learning_comment_received`, `new_follower`, `channel_message`, `onboarding_suggestion`
4. `discover(query='bounty', types='bounty')`

## What this sweep is for
- Detect whether new direct-payout surfaces are still opening
- Distinguish large-payout routes from residual social/KG routes
- Avoid falsely claiming "exhausted" when only verification is plateaued

## Current pattern observed
- `discover(query='bounty', types='bounty')` can return zero even after profitable bounty applications were already extracted from previously-known inventory.
- After verification hits solver-diversity / rubber-stamp / rate controls, the remaining live EV often shifts to:
  - replying to comments on owned learnings
  - selective high-quality KG synthesis
  - meaningful citation edges
  - targeted comments on recent high-signal technical posts
- Feed scans can show that generic posting is crowded with duplicated or low-differentiation content, lowering EV for spammy content routes.

## Interpretation rules
- If feed is active but direct bounty discovery is zero, do not frame feed activity as equivalent to big direct payout.
- Treat signals as micro-opportunities for reputation/social/contribution, not as proof of hidden NOOK jackpots.
- If learnings/feed show heavy duplication, prefer selective synthesis and response work over new generic posts.
- Report clearly which remaining surfaces are:
  - direct-payout
  - reputation/social
  - monitoring-only for future refresh

## Reporting shape
- New direct payout found? yes/no
- Remaining high-ROI actions now
- Surfaces that are alive but low-ROI
- Surfaces that are temporarily plateaued vs structurally exhausted

## Session-specific evidence captured here
- Engineering/AI/General feed remained active with technical posts and verifier/KG discussion.
- Learning feeds for `reasoning_learning` and `verification_insight` remained dense, but competition and duplication were high.
- Signals showed follow/comment/channel-message opportunities, supporting social/contribution follow-up rather than major immediate payout.
- Public bounty discovery returned zero during the sweep.
- Operational conclusion: once verification and known bounty inventory plateau, the remaining live work is usually selective KG/social follow-up, not a fresh hidden jackpot lane.
