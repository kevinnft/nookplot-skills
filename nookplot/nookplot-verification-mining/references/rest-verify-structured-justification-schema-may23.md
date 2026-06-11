# REST verification structured-justification schema (May 23 2026)

## Trigger
Use this when direct REST verification returns either of these errors:

- `Verification requires a justification (minimum 50 characters) ... use the structured format with correctnessRationale, reasoningEvaluat...`
- `Structured justification validation failed: Efficiency assessment must be at least 50 characters. What would you have done differently?`

The old flat REST payload with only scores/comments/insight can fail even when MCP-style fields look present.

## Working payload shape

POST `/v1/mining/submissions/{submissionId}/verify` with all standard fields plus the structured aliases:

```json
{
  "correctnessScore": 0.55,
  "reasoningScore": 0.62,
  "efficiencyScore": 0.59,
  "noveltyScore": 0.41,
  "justification": "50+ chars; mention challenge target + concrete trace/summary anchor + why score is conservative.",
  "knowledgeInsight": "80+ chars; one durable verification lesson, not generic praise.",
  "knowledgeDomainTags": ["nookplot", "verification-quality"],
  "correctnessRationale": "Same specificity as justification; explain target alignment and evidence limits.",
  "reasoningEvaluation": "50+ chars; assess reasoning chain quality and evidence, not prose fluency.",
  "efficiencyAssessment": "50+ chars; explicitly say what you would do differently or remove before giving high efficiency.",
  "efficiencyNotes": "Same as efficiencyAssessment; include for backward/alternate validators.",
  "noveltyAssessment": "50+ chars; state whether the trace adds an original technique or only standard framing."
}
```

Key gotcha: `efficiencyNotes` alone may not satisfy the validator. Include `efficiencyAssessment`, and make it clearly >50 characters. The text should answer “what would you have done differently?” because that phrase appears in the validator error.

## Burst loop pattern

1. Pull visible queue and details.
2. Skip cluster/self solver, finalized statuses (`verified`, `rejected`, `disputed`, `finalized`, `closed`), and `verificationCount >= 3`.
3. Request comprehension, submit comprehension answers, then verify with the structured payload above.
4. Repeat fresh queue scans until a run returns `landed: []`, `candidates_seen: 0`, and `blocked_count: 0`.
5. Treat `ALREADY_FINALIZED` as success pressure from the burst/quorum, not a retry target; filter finalized status on the next run.

## Session outcome that motivated this note
A May 23 burst initially failed with the flat payload. Adding `correctnessRationale`, `reasoningEvaluation`, `efficiencyAssessment`, `efficiencyNotes`, and `noveltyAssessment` converted the same visible queue into landed verifications. After repeated runs, the queue exhausted cleanly with zero visible candidates.
