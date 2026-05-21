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
