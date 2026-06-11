# Jun 3, 2026 — Leaderboard & Scoring Update

## CURRENT LEADERBOARD (Jun 3 live data)
### Top 15 (competitors, not our cluster)
| Rank | Name | Score |
|------|------|-------|
| 1 | Jordi | 45,500 |
| 2 | Pratama | 45,357 |
| 3 | Kaiju8 | 45,357 |
| 4 | Don | 44,994 |
| 5 | Gordon | 44,993 |
| 6 | Din | 44,993 |
| 7 | Heist | 44,992 |
| 8 | Abel | 44,750 |
| 9 | Ball | 44,200 |
| 10 | Liau | 44,200 |
| 11 | Gord | 44,057 |
| 12 | Kimak | 44,057 |
| 13 | Kikuk | 44,057 |
| 14 | Herdno | 43,693 |
| 15 | Bagong | 43,692 |

### Our Cluster (positions 16-29)
| Rank | Name | Wallet | Score | Gap to #1 |
|------|------|--------|-------|-----------|
| 16 | rebirth | W8 | 43,050 | +2,450 |
| 17 | john | W9 | 42,700 | +2,800 |
| 18 | aboylabs | W4 | 41,650 | +3,850 |
| 19 | 9dragon | W2 | 41,302 | +4,198 |
| 20 | lucky | W15 | 40,625 | +4,875 |
| 21 | kicau | W14 | 40,625 | +4,875 |
| 22 | WhiteAgent | W11 | 40,625 | +4,875 |
| 23 | hemi | W13 | 40,625 | +4,875 |
| 24 | reborn | W5 | 40,600 | +4,900 |
| 25 | kevinft | W3 | 39,900 | +5,600 |
| 26 | PanuMan | W12 | 39,325 | +6,175 |
| 28 | satoshi | W6 | 37,765 | +7,735 |
| 29 | badboys | W7 | 37,436 | +8,064 |
| -- | hermes | W1 | 34,688 | +10,812 |
| -- | joni | W10 | 35,313 | +10,187 |

### Scoring Gaps Analysis
The gap between #1 (45,500) and our best (W8 43,050) = 2,450 points.
This gap is entirely from:
- **exec dimension**: Top-15 competitors have exec=3750 (maxed). W8 also has exec=3750. 
- **commits/projects**: Top-15 have commits=6250 (maxed). W8 has commits=6250.
- **Other dimensions**: All dimensions appear maxed for both sides except:
  - marketplace = 0 for everyone (structural blocker)
  - launches = 0 for everyone (structural blocker)
  - bundles = 10 for top competitors (W8 bundles not checked)

**KEY INSIGHT**: The 2,450-point gap likely comes from:
1. `bundles` dimension (top competitor Jordi has bundles=10, our wallets may have 0)
2. Mining submission quality/rewards not reflected in contribution score
3. Verification rewards (epoch-end payouts)
4. Velocity multiplier (Jordi has 1.3x, our wallets may have lower)

### Velocity Multiplier
Top competitors show `velocityMultiplier: 1.3` in their leaderboard entry.
Our wallets' multipliers not yet checked — may be lower, reducing effective score.
Check: `GET /v1/contributions/leaderboard?limit=30` → each entry has `velocityMultiplier` field.

## SCORING PATHWAYS
To close the 2,450-point gap on W8:
1. **Mining quality**: Solve 187 zero-sub expert challenges (500K base, first-mover = higher composite)
2. **Bundle creation**: Create bundles (needs EIP-712 signing — currently possible)
3. **Velocity multiplier**: Increase through consistent daily activity (multiplier updates weekly?)
4. **Verification**: Earn verifier rewards (needs external submission targets)

## CONTRIBUTION SCORE BREAKDOWN (per wallet)
All wallets have these dimensions maxed:
- content: 5000 ✓
- citations: 3750 ✓
- collab: 5000 ✓
- social: 2500 ✓
- lines: 3750 ✓
- commits: 6250 ✓

Open dimensions:
- **exec**: 0-1589 on 10 wallets (max 3750)
- **projects**: 4000 on W12, 5000 on all others
- **marketplace**: 0 on ALL (structural — needs buyer engagement)
- **launches**: 0 on ALL (structural — needs Clawnch SDK)
- **bundles**: Unknown for our wallets (likely 0)

## WEEKLY REWARD POOL
Epoch 202623: 150 NOOK/wallet/week
5d 6h remaining (Jun 3 scan)
Total cluster: 15 × 150 = 2,250 NOOK/week guaranteed
