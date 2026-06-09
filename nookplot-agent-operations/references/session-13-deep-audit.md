# Session 13 Deep Audit — Jun 3, 2026

## Key Discoveries

### 1. Proactive Agent = Primary Growth Engine
- **9/15 wallets MAXED at 45,500** (up from 1/15 in session 12)
- Proactive agents autonomously maxed 3 wallets in ONE session
- Liau (12 actions), Gordon (11), Kikuk (11) all hit MAXED autonomously
- Fleet total jumped from ~669K to ~679K

### 2. Channel Slug Discovery Pattern
```bash
nookplot channels 2>&1
```
- `✓` = joined (can send)
- `─` = not joined (must join first)
- Slug is `project-xxx-domain-tools` format
- Must `nookplot channels join <slug>` before sending to unjoined channels

### 3. Mining Blocked by Guild Tier
- Most challenges require `tier1+` guild
- Ball/Bagong: "Your guild is none but requires tier1+"
- Abel: "Maximum 1 guild-exclusive per 24h" (already used cap)
- Guild tier based on `combined stake` — needs NOOK staking to upgrade

### 4. Score Formula (CONFIRMED)
```
Score = (Commits + Exec + Projects + Lines + Collab + Content + Social + Marketplace + Citations) × Velocity
Max = (6250 + 3750 + 5000 + 3750 + 5000 + 5000 + 2500 + ??? + 3750) × 1.3 = 45,500
```

### 5. Exec Score Mechanics
- Channel messages boost exec but have diminishing returns after ~3366-3647
- Proactive agents CAN push exec past the ceiling (proved: 9 wallets maxed)
- Large code commits (400+ lines) are the most reliable exec generator
- Attestations received (from external agents) are the primary exec driver

### 6. Weekly Rewards
- Pool: 150 credits per wallet per week
- 5d 5h remaining in current epoch (202623)
- Nobody has claimed yet (0 eligible, 0 distributed)
- Eligibility criteria unknown — likely requires verified submissions

### 7. Hidden Dimensions Still at Zero
- **Marketplace**: 0 for all wallets (45+ listings exist but no orders)
- **Launches**: 0 for all wallets (mechanic unknown)
- **Weekly Rewards**: 0 claimed

## Actions Taken (Session 13)
| Action | Count | Result |
|--------|-------|--------|
| Channel messages | 34 | ✓ Sent to correct slugs |
| Project commits | 6 | ✓ Gord (3), Ball (3) |
| Channel joins | 4 | ✓ Heist joined 4 channels |
| Proactive monitoring | 15 wallets | ✓ 9 maxed autonomously |
| API audit | 51+ endpoints | ✓ 5 working |
| Marketplace listings | 45+ | ✓ Via skills sync |
| Cron jobs | 6 paused | User requested manual control |

## Remaining Gaps
| Wallet | Gap | Size | Mechanism | Predicted Close |
|--------|-----|------|-----------|----------------|
| Din | Exec | 16 | Proactive | < 6 hours |
| Herdno | Exec | 110 | Proactive | < 24 hours |
| Kaiju8 | Exec | 111 | Proactive | < 24 hours |
| Heist | Exec | 391 | Proactive | 1-2 days |
| Gord | Projects | 1000 | Unknown | Needs investigation |
| Ball | Projects | 1000 | Unknown | Needs investigation |

## User Preferences Discovered
- **Manual control over automated mining** — User said "hentikan cronjob" (stop cronjobs)
- All 6 cron jobs paused per user request
- User prefers manual per-wallet operations with hand-crafted quality content
- Do NOT auto-enable mining cronjobs without explicit user request
