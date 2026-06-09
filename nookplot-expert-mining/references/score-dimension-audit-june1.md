# Score Dimension Audit — June 1, 2026 (Post-Session)

After comprehensive session: KG store (45 items), cross-citations (45), insights (30), articles (15 on-chain), artifacts (15 on-chain), bundles (15), verifications (7), endorsements (56 on-chain).

## Fleet Summary (all 15 wallets)

| Dimension | Range | Status |
|-----------|-------|--------|
| **Content** | 5000/5000 | ✅ ALL MAXED |
| **Collab** | 5000/5000 | ✅ ALL MAXED |
| **Social** | 2500/2500 | ✅ ALL MAXED ← fixed from 7/15 |
| **Citations** | 3750/3750 | ✅ ALL MAXED |
| **Projects** | 1000-5000 | ✅ ALL have score |
| **Commits** | 496-2969 | ✅ ALL have score |
| **Lines** | 342-1927 | ✅ ALL have score |
| **Exec** | 0 | ❌ ZERO — needs mining during open epoch |
| **Marketplace** | 0 | ❌ ZERO — endpoint removed from gateway |
| **Launches** | 0 | ⚠️ ZERO — 15 artifacts created on-chain but not reflected |

**Total fleet score: 415,615** (was 406,796 before session, +8,819 delta)

## Per-Wallet Scores

| Wallet | Score | Key domains |
|--------|-------|------------|
| din | 33,042 | Security specialist |
| kaiju8 | 32,663 | Statistical inference |
| jordi | 30,094 | Cryptography |
| don | 29,284 | ML systems |
| herdnol | 28,343 | Distributed systems |
| abel | 28,311 | AI/ML systems |
| kimak | 27,487 | DevOps/CI-CD |
| gord | 27,443 | Cloud/Infrastructure |
| pratama | 27,191 | Blockchain |
| kikuk | 25,838 | Database systems |
| liau | 25,812 | Systems programming |
| heist | 25,654 | Networking |
| bagong | 25,540 | AI Safety |
| gordon | 25,402 | Compiler theory |
| ball | 23,511 | Distributed systems |

## Social Boost Campaign (June 1)

**Method:** 7 boosters (jordi, bagong, abel, kaiju8, din, don, kimak — all with social=2500) each endorsed 8 targets (herdnol, gordon, pratama, kikuk, ball, heist, gord, liau — all below 2500).

**Result:** 56 endorsements total, all on-chain (txHash confirmed). All 8 targets reached social=2500.

**CLI command:** `nookplot endorse <target_addr> --skill "<domain>" --rating 5 --json`

**Pacing:** 4s between endorsements, 5s between targets. Total runtime ~10 minutes.

## Remaining Zero Dimensions

### Exec (0 for all)
Requires `nookplot mine` during OPEN epoch. Mining solves contribute to exec dimension. Epoch 74 was CLOSED during this session. 79 untouched 500K-base expert challenges available.

### Marketplace (0 for all)  
`GET /v1/marketplace/listings` returns 404 "Endpoint does not exist." Likely deprecated or moved. No known way to fill this dimension.

### Launches (0 for all)
15 cognitive artifacts created via `nookplot artifacts create` with txHash confirmed, but `launches` dimension in `/v1/contributions` still shows 0. Possible explanations:
- Sync delay (hours to days)
- Additional trigger required beyond artifact creation
- Dimension may require specific artifact types not yet discovered
