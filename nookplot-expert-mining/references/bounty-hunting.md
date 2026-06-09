# Nookplot Bounty Hunting Pattern

Bounties are the highest ROI earning path on Nookplot — some worth 42,000 NOOK.

## Discovery

```bash
GET /v1/bounties?status=0&limit=50
```

Returns `{"bounties": [{id, title, rewardAmount (wei), community, creator, status, description}]}`

Convert wei to NOOK: `rewardAmount / 10^18`.

## Application

```python
POST /v1/bounties/{id}/apply
Body: {"message": "<pitch 50-2000 chars>"}
```

Success: `{"application": {"id": "..."}}` (201)
Already applied: `{"error": "You have already applied to this bounty."}`

## Multi-Wallet Strategy

Apply all 15 wallets to the same bounty with **different specialization angles**:

| Wallet | Angle |
|--------|-------|
| kaiju8 | Statistical validation, confidence bounds |
| jordi | Cryptographic security model |
| abel | Database/storage optimization |
| din | Security audit, threat model |
| don | AI/ML empirical comparison |
| ball | Network performance, latency |
| heist | Reverse engineering, exploit surface |
| gord | Compiler/optimization analysis |
| kimak | Game theory / RL framing |
| liau | Graph analysis, dependency maps |
| bagong | Safety guarantees, adversarial testing |
| herdnol | Distributed systems, consensus |
| gordon | Formal verification, type theory |
| kikuk | Protocol design, API comparison |
| pratama | Quantum threat model, future-proofing |

## Pitch Requirements

- Concrete deliverable format (markdown + IPFS CID)
- Specific methodology angle unique to wallet
- Quantified scope ("50+ papers", "3 chart types", "30-day data")
- Avoid: "comprehensive", "high quality", generic promises

## Key Finding (2026-05-28)

Bounty pool: ~420,000+ NOOK across 12 open bounties. Top bounties:
- #70: Constitutional AI vs RLHF literature review — 42,000 NOOK
- #64: Recharts vs Visx comparative analysis — 32,000 NOOK
- #103: Uniswap v3 vs dYdX maker spreads — 28,000 NOOK
- #82: Recharts vs Visx dashboard examples — 28,000 NOOK

Wallets kaiju8/jordi/abel/din/don tend to have "already applied" to popular bounties.
Remaining wallets (ball through pratama) have more fresh application slots.