# Mining submit IPFS prerequisite and eligibility split (May 23 2026)

## Durable lesson

When the user says to "gas semua" on the mining lane, do not report the lane as open from challenge discovery alone. Perform a real submit attempt on the highest-ROI eligible wallets.

For the current standard reasoning-trace challenge submit path, direct `POST /v1/mining/challenges/<id>/submit` with only `traceContent` / `traceSummary` in the body is insufficient. The gateway returns:

```json
{"error":"traceCid and traceHash are required"}
```

So the actual required flow is:

1. Write the full markdown trace locally.
2. Upload it to IPFS (gateway upload path) to obtain `traceCid` and `traceHash`.
3. Submit to `/v1/mining/challenges/<id>/submit` using those fields plus summary/model metadata.

## Session evidence

Real submit attempts were executed against open challenge:
- `bb5186da-b752-494f-9e46-d28e3dd2a3f5`

Wallets tested:
- W6
- W7
- W8
- W2
- W3

All returned the same error requiring `traceCid` and `traceHash`.

## Operational implication

Classify the lane as:
- open at challenge-discovery layer
- open at eligibility layer for tier1+/boosted wallets
- blocked at execution layer until IPFS pre-upload is done

Do NOT say "all wallets can submit" when the challenge is guild-tier-gated. Split the cluster into:

- eligible / high-ROI submitters: wallets in tier1+ or stronger guilds (session proof: W6/W7/W8/W2/W3)
- low-ROI / ineligible wallets: tier-none or weaker wallets (session proof: W1/W4/W5)
- unknown until re-probe: wallets hidden behind rate-limit

## Reporting shape for the user

Use concise action-first output:
- which wallets were actually attempted
- exact gateway blocker string
- which wallets are worth continuing with after fixing the blocker
- avoid saying the reward is "high" if the only open challenge is low reward (~599 NOOK)

## Why this belongs under leaderboard maximization

This is a lane-selection and execution-truth lesson: challenge inventory alone overstates available mining ROI. The real value comes from proving the execution path, then downgrading or continuing the lane accordingly.
