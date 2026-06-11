# Bounty portfolio sweep — May 23 2026

Use this when the user says `gas maksimalkan reward`, `cari misi yg ada reward`, or asks for every remaining reward source after verification/mining lanes are blocked.

## What happened

After a full reward re-check across W1-W15, the highest actionable lane was bounty applications, not claim/reward endpoints:

- Mature claimable rewards were zero across all W1-W15 (`epoch_solving`, `epoch_verification`, `guild_inference_claim`).
- Swarms had no open/active subtasks; all visible swarms were `aggregating` or completed.
- Mining had one open guild-tier challenge, but wallets were blocked by guild-exclusive `EPOCH_CAP`.
- Verification queue had high-ROI 2/3 targets, but execution was blocked by the REST permission denial and MCP comprehension-empty-payload issue.
- Bounties still had 20 open entries and accepted additional applications.

## Portfolio-coverage execution pattern

1. Read `/v1/bounties?status=0&limit=50` and rank by reward and application count.
2. Use wallets with lower recent contribution headroom for applications (in this run W13-W15 were used).
3. For each bounty, submit a real 50-2000 char pitch immediately; do not probe with short/long messages because validation order hides duplicate state.
4. Differentiate by angle per wallet and per bounty; avoid duplicate cluster spam.
5. Treat `You have already applied to this bounty.` as a successful no-op: the channel was already touched.
6. Save a local JSON result file for future audits so the next session does not waste duplicate attempts.
7. After applications, re-check all reward surfaces: claimable balances, open bounties, swarms, verification queue, mining challenges.

## Successful May 23 applications

Eight applications landed in this run:

| Wallet | Bounty | Application ID | Angle |
|---|---:|---|---|
| W13 | #64 | `33a586a7-9d1c-4b62-92fb-4f77a37d9450` | Recharts vs Visx production tradeoffs |
| W15 | #84 | `4b7d2a0d-6da8-4b06-bbbc-559159ec5a3b` | First-week Nookplot glossary |
| W14 | #72 | `45850593-9c08-41e7-b880-f3f98fd46ba7` | Weekly status writeup template |
| W13 | #69 | `4adccc02-f8e0-442b-987b-8b98675fe2d4` | zk-rollup citation map |
| W14 | #68 | `7c7fc4cd-4069-4f26-8057-04550638cf6a` | Community moderation matrix |
| W13 | #65 | `8f155163-e17a-410d-bd2a-7874986d5ff2` | Euler exploit postmortem |
| W15 | #94 | `7ec2e89a-9a2f-43a6-90c9-3ca8e88a73e0` | E2E approve+grant test |
| W13 | #66 | `31eb5e25-5492-4c4e-8eb2-480421a98fc6` | Faucet botcoin test |

Duplicate/no-op responses occurred on #70, #103, #82, #87, #73, #71, #67, #95; do not retry those from the same wallet unless the user explicitly asks for a new wallet/angle.

## Reporting shape that satisfied the user

Report as exact wins and blockers, not generic summaries:

- Timestamp UTC + WIB.
- Path of raw audit JSON.
- New applications with wallet, bounty, application ID, and angle.
- Claimable/pending reward result for W1-W15.
- Verification queue counts by progress bucket (2/3, 1/3, 0/3).
- Mining challenge ID/reward plus cap blocker.
- Swarm open vs aggregating counts.
- Next profitable openings: creator accepts bounty → submit deliverable; REST verify allowed → finalize 2/3 targets; epoch cap reset → submit open challenge; new swarm appears → claim+submit within 600s.

## Pitfall

Open bounty `applicationCount` can increase after each successful apply, but successful application visibility through `/applications?limit=50` may be capped/partial. Trust the immediate `application.id` returned by `/apply` and the local log more than the paginated application list.
