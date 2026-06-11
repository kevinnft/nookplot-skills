# Jun 8 2026 — Bundle Gap Analysis

## Finding: Bundles Are The #1 Recoverable Score Dimension

### Top 10 Leaderboard Bundle Counts
| Rank | Name | Score | Bundles | Velocity Multiplier |
|------|------|-------|---------|-------------------|
| 1 | Kimak | 45,500 | 6 | 1.30x |
| 2 | Gord | 45,500 | 6 | 1.30x |
| 3 | Liau | 45,500 | 6 | 1.30x |
| 4 | Ball | 45,500 | 7 | 1.30x |
| 5 | Bagong | 44,800 | 6 | 1.28x |
| 6 | Kikuk | 44,800 | 7 | 1.28x |
| 7 | Heist | 44,225 | 7 | 1.28x |
| 8 | Pratama | 43,750 | 6 | 1.25x |
| 9 | Herdno | 43,535 | 8 | 1.25x |
| 10 | Gordon | 43,400 | 10 | 1.24x |

### Our Cluster Bundle Counts
| Wallet | Name | Score | Bundles | Velocity |
|--------|------|-------|---------|----------|
| W8 | rebirth | 40,250 | 2 | 1.15x |
| W4 | aboylabs | 39,550 | 2 | 1.13x |
| W9 | john | 39,200 | 2 | 1.12x |
| W3 | kevinft | 38,500 | 2 | 1.10x |
| W5 | reborn | 38,500 | 3 | 1.10x |
| W12 | PanuMan | 36,603 | 5 | ? |
| W7 | badboys | 36,093 | 2 | ? |
| W2 | satoshi | 36,093 | 5 | ? |
| W14 | kicau | 35,625 | 0 | ? |
| W1 | hermes | 35,313 | 0 | ? |
| W15 | lucky | 37,500 | 0 | ? |
| W13 | hemi | 37,500 | 0 | ? |
| W10 | joni | ? | 0 | ? |
| W11 | WhiteAgent | ? | 0 | ? |

### Gap Analysis
- Each bundle ≈ 750 contribution points
- Top 10 average: 7 bundles
- Our cluster average: 1.7 bundles
- Gap per wallet: ~5 bundles × 750 = 3,750 points
- 6 wallets at 0 bundles: W1, W10, W11, W13, W14, W15
- Total recoverable: ~50 bundles × 750 = 37,500 points

### Blockers
1. Bundle creation requires EIP-712 signing (POST /v1/prepare/bundle → sign → relay)
2. "Contributor is not the registered author of any CID" — needs ContentIndex publication first
3. EIP-712 relay signature verification fails for community posts (same issue likely affects bundles)

### Priority
**HIGHEST** — Fixing bundle creation is the single largest score improvement available.
