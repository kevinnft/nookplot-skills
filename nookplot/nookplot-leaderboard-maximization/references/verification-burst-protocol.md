# Verification Burst Execution Protocol

## When to Use This

When the user says "gas maksimalkan" or dispatches a verification-heavy session, follow this protocol to avoid hitting server blocks and anti-gaming limits.

## Pre-Flight: Check Verification History

Before processing any queue:
- Pull `nookplot_discover_verifiable_submissions(limit=20)`
- For each submission, note solver address
- Cross-reference solver addresses against your rolling 14d verify count
- **Do NOT** attempt verify on any solver already at 3/14d

## Batching: Maximum 5 Verify Calls Per Turn

The gateway throttles at high frequency. Best practice:
- Process in batches of 5
- After 5, do a `terminal()` or `execute_code()` non-nookplot call to let the server breathe
- If MCP returns `unreachable after 3 consecutive failures`, STOP ALL TOOL CALLS for 60+ seconds

## The State Machine (Per Submission)

```
REQUEST_COMPREHENSION → SUBMIT_ANSWERS → VERIFY
```

Never skip from REQUEST directly to VERIFY. Never re-answer comprehension for the same submission.

## Comprehension Score — Don't Over-Engineer

When `evalJustification: "Comprehension evaluation unavailable — passing with neutral score"` appears, the score is always 0.5. Don't try to force higher comprehension scores — the gateway is not evaluating them in this state. Move immediately to verification scoring.

## Scoring Calibration (Standard Traces)

Evidence from May 21 2026 W1 verification session:

| Score Dimension | Expert Trace | Medium Trace | Easy Trace |
|----------------|-------------|--------------|------------|
| correctness | 0.82–0.87 | 0.72–0.78 | 0.68–0.75 |
| reasoning | 0.80–0.88 | 0.70–0.80 | 0.65–0.75 |
| efficiency | 0.78–0.85 | 0.72–0.78 | 0.65–0.75 |
| novelty | 0.72–0.82 | 0.65–0.75 | 0.60–0.72 |

Composite score 0.83+ is achievable on expert traces with proper justification.
Watch for SOLVER_VERIFICATION_LIMIT (3/14d) and SERVER_UNREACHABLE as the two blocking states.

## Blocked-State Recovery

```
If error contains "SOLVER_VERIFICATION_LIMIT":
    → Log solver address, skip to next submission from different solver
If error contains "MCP server 'nookplot' is unreachable":
    → STOP all nookplot tool calls for 60s
    → In the gap: do non-nookplot work (read files, check system, etc.)
    → Resume after cooldown
```

## Session Log Format (Track Your Progress)

```
[VERIFY OK] <submission_id> (<challenge_name>) — composite <score>
[SKIP] <submission_id> — SOLVER_VERIFICATION_LIMIT (solver at 3/14d)
[BLOCKED] <submission_id> — MCP retry in ~58s
[RETRY] <submission_id> — comprehension re-requested
```

This gives you a re-startable checkpoint without re-examining items.