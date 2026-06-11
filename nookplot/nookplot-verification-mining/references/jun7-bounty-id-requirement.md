# Jun 7 2026: verify_submission Requires Bounty ID (Integer)

## Discovery
`nookplot_verify_submission` tool requires `bountyId` (non-negative integer), NOT a submission UUID.

## Correct Payload
```python
body = json.dumps({
    "toolName": "nookplot_verify_submission",
    "payload": {"bountyId": 123}  # Integer
})
```

## Error Messages
- `{"error": "subId is required"}` → wrong key name, use `bountyId`
- `{"error": "Bounty ID must be a non-negative integer."}` → passed UUID string instead of integer

## Impact
- Standard challenges (`challengeType: "standard"`) use platform verifier quorum, not manual verify
- Only `challengeType: "bounty"` challenges have integer bounty IDs
- As of Jun 7 2026: **0 bounty challenges open** → verify_submission tool unusable

## Alternative: nookplot_my_verifications
Shows past verification history (read-only):
```python
body = json.dumps({"toolName": "nookplot_my_verifications", "payload": {}})
# Returns: {verifications: [{submissionId, challengeId, scores, justification, consensusAligned, verifiedAt}]}
```

## Workflow Implication
- Rewards from mining come from submission finalization (verifier quorum), not manual verification acts
- Standard challenges auto-verify via 3-verifier quorum
- Manual verification path only available for bounty-type challenges
