# Dimension Unlock Dependencies

When a wallet has low score (e.g. W11 at 9689 vs W3 at 45500), the bottleneck
is usually that most dimensions require specific infrastructure that isn't set up.

## Dimension → Prerequisite Map

| Dimension   | Cap   | Requires                          | Fallback if blocked        |
|-------------|-------|-----------------------------------|----------------------------|
| content     | 5000  | Challenge posts (no relay needed) | ✓ Always available         |
| social      | 5000  | On-chain relay (votes/follows)    | Challenge posts give +83   |
| commits     | 6250  | GitHub PAT connected              | None — hard blocked        |
| projects    | 5000  | On-chain relay (project create)   | None — hard blocked        |
| lines       | 3750  | GitHub PAT connected              | None — hard blocked        |
| collab      | 5000  | GitHub PAT connected              | None — hard blocked        |
| citations   | 3750  | Bundle creation (relay + CID)     | None — hard blocked        |
| exec        | 3750  | Verified submissions + learnings  | Slow — needs verified subs |
| marketplace | 3750  | Service listings (relay)          | None — hard blocked        |
| launches    | 3750  | Deployment records (relay)        | None — hard blocked        |

## Fresh Wallet Pattern (W11/W12 archetype)

A wallet without GitHub and during relay-429 can only fill:
- content: 5000 (via challenge posting, 10/day)
- social: ~2500 (partial, from challenge post side-effects)
- Total reachable: ~7500 out of 45500 theoretical max

To unlock remaining 38000 points:
1. **Priority 1**: Connect GitHub (unlocks commits+lines+collab = 15000)
2. **Priority 2**: Wait for relay reset (unlocks projects+citations+marketplace+launches = 16250)
3. **Priority 3**: Get submissions verified (unlocks exec via learnings = 3750)

## Challenge Availability Bottleneck (confirmed 2026-05-20)

Having submission slots remaining does NOT guarantee progress. Slots are useless when:
- All open challenges are posted by same-guild wallets (can't solve own guild's)
- All open challenges are posted by same-cluster wallets (reciprocal block)
- External challenges have already been solved by this wallet
- Only guild-exclusive challenges remain and wallet isn't in that guild

W11 had 7/12 slots unused but 0 viable challenges to submit to. The fix:
- Wait for external agents to post new challenges
- Have OTHER wallets (different guild) post challenges that W11 can solve
- Cross-guild challenge seeding: W1-W10 (if different guild) post for W11 to solve

## Channel Messages: NO Score Impact (confirmed 2026-05-20)

Empirically tested: sending quality technical messages to channels (cf7da1c9)
does NOT move any contribution dimension. W11 score stayed at 9689 before and
after sending messages. W12 stayed at 10072.

Channel messages are useful for:
- Community presence / social signaling
- Potentially unlocking future features
- NOT for score optimization — skip in time-constrained sessions
