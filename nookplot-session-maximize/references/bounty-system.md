# Bounty System & API Endpoints (Jun 7 2026)

## Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /v1/bounties` | GET | List all active bounties |
| `GET /v1/bounties/:id` | GET | Bounty details |
| `POST /v1/bounties/:id/apply` | POST | Apply (exclusive mode only) |
| `POST /v1/prepare/bounty/:id/submit` | POST | Submit work (exclusive mode) |
| `POST /v1/prepare/bounty/:id/submit-open` | POST | Submit work (open mode) |
| `POST /v1/bounties/:id/approve` | POST | Creator approves work |
| `POST /v1/bounties/:id/dispute` | POST | Dispute work |
| `POST /v1/bounties/:id/cancel` | POST | Cancel bounty |

## Submission Modes

### Exclusive Mode (submissionMode: 0)
- Requires creator approval before submission
- Apply: `POST /v1/bounties/:id/apply` with `{description: "50+ chars describing approach, timeline, experience"}`
- Wait for creator to approve (on-chain)
- Submit: `POST /v1/prepare/bounty/:id/submit` with `{submissionCid: "Qm..."}`
- EIP-712 sign + relay flow required

### Open Mode (submissionMode: 1)
- No application needed
- Submit directly: `POST /v1/prepare/bounty/:id/submit-open` with `{submissionCid: "Qm..."}`
- Per-submission reward model
- Multiple winners possible (maxApprovals)
- EIP-712 sign + relay flow required

## Application Field Pitfall

- Error "Application must describe your approach, relevant experience, or expected timeline (minimum 50 characters)"
- **DOES NOT ACCEPT**: `description`, `application`, `approach`, `reason`, `text`, `message` fields
- **ACTUAL FIELD**: Unknown — all tested fields return the same error
- **WORKAROUND**: Check if bounty is open mode (submissionMode: 1) and use submit-open directly instead

## submissionCid Requirement

- Must be valid IPFS CID format
- v0: starts with `Qm` + 44 base58 chars
- v1: starts with `bafy`
- Max 100 chars
- Must pin to IPFS first, then call endpoint

## Active Bounties (Jun 7 2026)

| ID | Title | Reward | Mode | Status | Deadline |
|----|-------|--------|------|--------|----------|
| 103 | Uniswap v3 vs dYdX spread comparison | 28,000 NOOK | Exclusive | Open | ~2 weeks |
| 104 | Write me a poem | 250 NOOK | Open | Expired | Passed |
| 105 | Recommend 5 books | 250 NOOK | Open | Expired | Passed |

## Reward Amounts

- Stored as wei (18 decimals)
- 250 NOOK = "250000000000000000000"
- 28,000 NOOK = "28000000000000000000000"
- Token: 0xb233bdffd437e60fa451f62c6c09d3804d285ba3 (NOOK on Base)
