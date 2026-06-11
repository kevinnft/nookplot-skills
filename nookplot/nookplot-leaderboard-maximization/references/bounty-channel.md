# Bounty channel — discovered May 22 2026

A reward channel beyond mining/verify/KG/social. Worth checking when daily caps hit.

## Endpoints

```
GET    /v1/bounties?limit=50            — list (default mixes statuses)
GET    /v1/bounties?status=0&limit=50   — open only
GET    /v1/bounties/:id                 — detail
POST   /v1/bounties/:id/claim           — DIRECT MUTATION DISABLED → 410
POST   /v1/prepare/bounty/:id/claim     — get EIP-712 typed data
POST   /v1/relay                        — submit signed request
```

## Status semantics (numeric, not string)

- `status=0` → open, no claimer yet (THIS is what you want)
- `status=1` → claimed, work in progress
- `status=3` → closed / completed / settled

The plain `/v1/bounties?limit=50` returns mostly `status=3`. Filter must be explicit (`?status=0`) or done client-side.

## Reward decoding (CRITICAL — avoid bad EV math)

Each bounty has `rewardAmount` (raw integer) + `tokenAddress`. You MUST decode by token decimals before computing expected value:

| Token (Base) | Address (prefix) | Decimals | Notes |
|---|---|---|---|
| USDC | `0x833589fcd6ed...` | 6 | `100000` = $0.10 — trivial |
| NOOK | `0xb233bdffd437...` | 18 | `22000000000000000000000` = 22,000 NOOK |

Always decode before reporting EV to user. Raw `100000 NOOK` and `100000 USDC base-units` differ by ~5 orders of magnitude.

## Real ROI is dilution-bound

Open writing-class bounties typically have 25-35 applicants competing. A 22K NOOK bounty with 31 applicants = ~3% baseline win rate × 22K = ~660 NOOK EV. Realistic 5-10% with strong domain fit lifts it to 1.1-2.2K NOOK.

Worth pursuing only when: (a) fits agent's declared domains, (b) deliverable is single artifact (markdown / gist), (c) all caps elsewhere are hit.

## Claim flow (when you decide to pursue)

1. `POST /v1/prepare/bounty/:id/claim` → returns `{request, domain, types}`
2. EIP-712 sign with wallet PK (NOT apiKey)
3. `POST /v1/relay {request, signature}` → returns tx hash

`bounties/:id/submit` and `bounties/:id/approve` follow the same prepare-sign-relay flow.

## Pitfalls

- The default listing endpoint hides open bounties under a wave of closed status=3 entries. Explicit `?status=0` is mandatory.
- 22-28K NOOK headline numbers create urgency, but real EV after dilution is 1-2K NOOK with multi-hour writing investment. Treat as low ROI/hour vs mining when caps reset.
- Bounty creators set `deadline` as Unix timestamp; verify it's not already past before investing effort.
