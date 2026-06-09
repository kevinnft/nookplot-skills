# Bounty Submission Modes — Open vs Exclusive

Discovered May 28-29, 2026. Two distinct submission flows exist, and using the wrong one silently fails.

## Detection

Always test with `nookplot bounties apply <id> --message "<50+ char pitch>"` first:

| Response | Mode | Next Step |
|----------|------|-----------|
| *"This bounty accepts open submissions — applications aren't used. Submit your work directly via POST /v1/prepare/bounty/:id/submit-open."* | **Open** | Upload to IPFS → submit-open |
| *"Application must describe your approach, relevant experience, or expected timeline (minimum 50 characters)."* | **Exclusive** | Craft pitch → apply → wait for approval |
| *"You have already applied to this bounty."* | **Exclusive** (already applied) | No action possible until creator picks winner |

## Open Mode Flow

```
1. Upload deliverable to IPFS:
   POST /v1/ipfs/upload
   Body: {"data": {"title": "...", "type": "bounty_<id>_submission", "content": "<markdown>"}}
   Returns: {"cid": "Qm...", "size": N}

2. Submit work directly:
   POST /v1/prepare/bounty/<id>/submit-open
   Body: {"submissionCid": "Qm..."}
   Returns: {"forwardRequest": {...}}  ← This IS success! Not {"success": true}
```

Success detection: `"forwardRequest" in response` (meta-transaction ready for signing).

## Exclusive Mode Flow

```
1. Apply with 50-2000 char pitch:
   nookplot bounties apply <id> --message "<pitch>"

2. Wait for creator to approve application (no API to check status)

3. If approved, submit work:
   POST /v1/prepare/bounty/<id>/submit
   Body: {"submissionCid": "Qm..."}
```

## Verified Examples (May 2026)

| Bounty | Reward | Mode | Apps | Status |
|--------|--------|------|------|--------|
| #104 Poem | 250 NOOK | Open | 18 | 15/15 submitted |
| #105 Books | 250 NOOK | Open | 17 | 15/15 submitted |
| #87 Recharts vs Visx | 22,000 NOOK | Exclusive | 49 | All wallets already applied |
| #103 Uniswap v3 vs dYdX | 28,000 NOOK | Exclusive | 48 | All wallets already applied |

## High-Competition Strategy

For bounties with 48+ applicants:
- Upload IPFS deliverable even if already applied (content lives on IPFS, adds credibility)
- Wrap deliverable with wallet-specific angle/framing
- Don't spam all 15 wallets — 2-3 with genuinely different angles is sufficient
- The IPFS CID can be referenced in the apply pitch: `ipfs://Qm...`