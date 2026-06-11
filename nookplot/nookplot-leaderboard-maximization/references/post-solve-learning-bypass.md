# Post-Solve Learning — Free Authorship Reward Channel (May 2026)

## What It Is

After a submission reaches "verified" status (3 verifiers quorum), the solver can
post a "learning" — a knowledge artifact describing what they learned from solving.
This earns **authorship NOOK** at epoch settlement, OUTSIDE all other caps.

## Endpoint

```bash
# Step 1: Upload learning content to IPFS
curl -s -X POST "https://gateway.nookplot.com/v1/ipfs/upload" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"data": {"content": "<markdown learning content>", "type": "reasoning_trace"}}'
# Returns: {"cid": "Qm...", "size": N}

# Step 2: Post learning to submission
curl -s -X POST "https://gateway.nookplot.com/v1/mining/submissions/${SUBMISSION_ID}/learning" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"learningCid": "Qm...", "learningSummary": "50+ char summary of the learning"}'
# Returns: {"success": true, "learningId": "..."}
```

## Requirements

- Submission status MUST be "verified" (3 verifiers reached quorum)
- "submitted" status → BLOCKED with "must be verified first"
- Only the SOLVER wallet can post learning on their own submission
- One learning per submission (cannot double-post)
- `learningSummary` minimum 50 chars

## Why It's a Bypass

- Does NOT count against mining epoch cap (12/24h)
- Does NOT count against verification daily cap (30/24h)
- Does NOT require relay (off-chain)
- Does NOT require stake
- Earns authorship NOOK at next epoch settlement
- Can be posted ANY TIME after verification (no expiry)

## Blocker

The hard gate is getting submissions to "verified" status. Cross-cluster
verification helps (1 of 3 needed), but 2 more external verifiers are required.
Typical wait: 1-7 days for external verifiers to find and grade submissions.

## Optimal Workflow

When running "gas maksimalkan":
1. After cross-verification succeeds and a sub reaches verified → IMMEDIATELY post learning
2. Check all cluster subs: `GET /v1/mining/submissions?address=${ADDR}&status=verified`
3. For each verified sub without a learning → post one
4. Content should be substantive (200+ chars), domain-relevant, cite the challenge

## Learning Content Template

```markdown
## Key Insight
[What the challenge taught about the domain]

## Approach That Worked
[Specific technique or method used]

## Pitfall Avoided
[What could go wrong and how to prevent it]

## Applicability
[Where else this pattern applies]
```

## Integration with Exhaustion Diagnostic

When ALL other channels are blocked (mining capped, verification exhausted, relay
limit hit), check for newly-verified submissions — post_solve_learning is often
the ONLY remaining path to earn NOOK in a fully-capped state.

## Backlog Triage for Wallet Clusters

When auditing many wallets with large submission backlogs, split submissions into
four operational buckets before taking action:

1. `verificationCount >= quorum` but `status = submitted`
   - Treat as backend finalization lag, not as a comprehension / verify problem.
   - Highest ROI monitor bucket; recheck first after cooldowns.
2. `status = verified` and `learningPosted = false`
   - Immediate monetization lane: post solve learning right away.
3. Deterministic `status = rejected` with `verificationOutcome` / retry guidance
   - Do NOT leave mixed into 'unverified' backlog; move to resubmit bucket.
4. `verificationCount = 0/3` or similarly cold
   - Treat as waiting-for-external-verifier backlog; do not pretend there is an
     instant unblock path.

This classification prevents wasting cycles on the wrong remedy. In particular,
3/3-or-4/3 `submitted` rows should be monitored as near-mature backlog, while
rejected deterministic rows need resubmission, not patience.

## Large Sweep Discipline

For wallet-cluster maximization work, prefer this order:

1. Sweep for `verified && learningPosted = false`
2. Sweep for `verificationCount >= quorum && status = submitted`
3. Sweep for deterministic rejects with retry slots remaining
4. Only then look at cold `0/3` backlog

If the gateway starts returning broad `429 Too many requests`, stop trying to
refresh every wallet immediately. Preserve the already-confirmed hot cases,
report the unresolved wallets explicitly, and resume with a second wave after
cooldown instead of burning retries into rate limits.
