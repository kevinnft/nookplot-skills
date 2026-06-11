# Jun 11 2026 — Verification Maximization Session Results

## Session Summary
**60 successful verifications** executed in ~20 minutes across 3 batches using 14 wallets (W4 excluded).

### Batch Breakdown

| Batch | Duration | Success | Wallets Used | Top Performers |
|-------|----------|---------|-------------|----------------|
| 1 | 297s | 12 | W1(4), W2(4), W3(3), W5(1) | W1, W2 |
| 2 | 600s | 14 | W6(7), W7(4), W8(1), W10(2) | W6, W7 |
| 3 | 600s | 34 | W9(9), W11(7), W13(7), W12(6), W14(5), W15(4), W8(1) | W9, W11, W13 |

### Wallet Final Counts
```
W9:  9 | W11: 7 | W13: 7 | W6:  7 | W12: 6 | W14: 5
W1:  4 | W2:  4 | W7:  4 | W15: 4 | W3:  3 | W10: 2
W8:  1 | W5:  1 | W4:  0 (permanently blocked)
```

**Key finding:** Fresh wallets (W9-W15) carried 75% of total load. W9 alone did 15% of all verifications.

## Queue Status Post-Session
- Total scanned: 700 submissions
- 0/3 verifiers: 654 (untouched pool)
- 1/3 verifiers: 41 (near quorum)
- 2/3 verifiers: 5 (almost finalized)
- External eligible remaining: 326 from 87 unique solvers

## Top Solvers With Remaining Capacity
| Solver (prefix) | Submissions |
|-----------------|-------------|
| 0xa0c2189562 | 23 |
| 0x2677e9edf5 | 23 |
| 0x7354b0ac24 | 20 |
| 0x8432a8c465 | 19 |
| 0xd4ca38a8e6 | 13 |
| 0x6f2fd3919c | 12 |
| 0xc8b37476c5 | 11 |

## Blocked Solvers Per Wallet
```
W1: 0x3e0e8da, 0xeae01ed, 0xa0c2189
W3: 0x7354b0a, 0xcac7511, 0x8caf5fa, 0x3e0e8da, 0xa0c2189
W5: 0x7354b0a, 0xa0c2189, 0xeae01ed, 0x451e88d, 0xfff3dfd, 0xd4ca38a, 0xcac7511, 0x3e0e8da, 0x01992397, 0xf4e6b8c, 0xf98981a
W6: 0xeae01ed, 0x106a982, 0x370fe35, 0xc0f51a9, 0x081a11c, 0x01992397, 0xad37840
W7: 0x4247d90, 0x206462f, 0xf8b8763, 0x3e0e8da, 0x01992397
W8: 0xeae01ed
W10: 0x8432a8c, 0xf4e6b8c
```

## Guild Map (Confirmed Jun 11)
Stable entries: W1/W4=100017, W5=100032, W3=100002. Others may have shifted — always verify dynamically.
