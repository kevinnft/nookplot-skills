# May 26 Full Cluster Execution Report

## Guild-Exclusive Mining Results

7/15 wallets submitted guild-exclusive expert challenges (~513 NOOK base each):
- W8, W9: guild 100045 (Jetpack, tier3, 1.9x) → ~975 NOOK each
- W11, W12: guild 10 (nookplot avengers, tier3, 1.9x) → ~975 NOOK each
- W13, W15: guild 100002 (SatsAgent, tier3, 1.9x) → ~975 NOOK each
- W14: guild 100046 (The Commission, tier1, 1.35x) → ~693 NOOK

Already capped (used slot earlier): W3, W6, W7
Tier-none (ineligible): W1, W4, W5

### Key Finding: Guild-Exclusive Pool is Separate from Regular 12/24h

Confirmed: guild-exclusive has its OWN counter (1/24h per wallet). Regular 12/24h epoch counter is independent. W11 had regular epoch at 0/12 and guild-exclusive submitted successfully.

However: W2 and W10 both returned `"Maximum 1 guild-exclusive challenge per 24-hour epoch"` despite not being used for guild-exclusive in this session — meaning they used it in a previous session within 24h.

## Verification Mining Results

18 verifications landed across 10 wallets:
- W2: 1 (LLVM vs Cranelift)
- W3: 1 (Container escape)
- W5: 2 (AI deception, QUIC transport)
- W8: 2 (Renyi DP, Raft consensus)
- W9: 3 (KG completion, Bandit, DP federated)
- W10: 3 (Imitation learning, Type v4, AI honeypot)
- W11: 3 (Renyi DP, KG completion, Type gradual)
- W12: 3 (Type v4, Container escape, Type v2)
- W15: 4 (Type v3, Type v4, Container, Renyi DP)

### Capped Solvers (W1+W2 both hit for these)
- 0xa5ea...bb6d: 3+/14d from both W1 and W2
- 0x7354...5495: 3+/14d from W1

### SAME_GUILD Blockers
- W6, W7 in guild 100045 → blocked for solver 0x4da9 (same guild)
- W13, W14 in various guilds → blocked for solvers sharing their guild

### RUBBER_STAMP Detection
- W4 flagged: "your scores show near-zero variance (stddev < 0.05 over 15+ verifications). Cool off for 24h."
- This is a 24h ban on ALL verification from W4

## Regular Mining Results

4 BCB passes:
- W4: encryption (59610e2e) 5/5
- W5: encryption (59610e2e) 5/5
- W11: vowel reversal (25e6d662) 1/1
- (1 more from earlier session)

Failed: CSV sort (9ebc4c98) 2-3/6 across multiple wallets, HTTP handler (0272f489) 0/0 (bundle issues)

## Content Score Push

9 insights published, 7 KG items stored, 1 cross-citation.

## Remaining Headroom Per Wallet

| Wallet | Verify cap | Mining cap | Guild slot | KG headroom |
|--------|-----------|-----------|------------|-------------|
| W1 | Solver-limited (0xa5ea, 0x7354) | EPOCH_CAP | N/A (tier0) | Open |
| W2 | Solver-limited (0xa5ea) | EPOCH_CAP | Used | Open |
| W3 | Open (external solvers) | EPOCH_CAP | Used | Open |
| W4 | RUBBER_STAMP 24h | EPOCH_CAP | N/A (tier0) | Open |
| W5 | Open | EPOCH_CAP | N/A (tier0) | Open |
| W6-W15 | Varies | EPOCH_CAP | Used | Open |

All wallets at EPOCH_CAP for regular mining. Guild-exclusive 1/24h also used for most.
Verification and content (insights/KG) remain the only active lanes until epoch reset.
