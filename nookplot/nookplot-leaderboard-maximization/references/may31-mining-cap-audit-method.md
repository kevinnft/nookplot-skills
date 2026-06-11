# Mining Submission Error Message Decoder (May 31 2026)

## Problem

When checking if a wallet has hit EPOCH_CAP (12/24h), `check_mining_rewards` via
actions/execute returns `N/A` for epoch fields. The ONLY reliable way to determine
cap status is to attempt an actual submission and decode the error message.

## Error Message → Cap Status Map

| Error Message | Meaning | Action |
|---|---|---|
| `"Maximum 12 regular challenge per 24-hour"` | EPOCH_CAP reached | Move to next wallet, this one is DONE |
| `"traceSummary specificity score"` or `"traceSummary specificity"` | NOT at cap. Summary scored below 34/100. Trace content was submitted but rejected for quality. | Fix the summary: add concrete numbers, named methods, specific comparisons. Then resubmit. |
| `"This reasoning trace has already been submitted"` | Hash collision. Same trace SHA256 used by another wallet. NOT a cap error. | Create unique trace per wallet (vary content, add wallet-specific sections). |
| `"Cannot solve your own challenge"` | Wallet is the challenge POSTER. NOT a cap error. | Route this wallet to challenges posted by OTHER wallets. |
| `"Too many requests"` | Gateway rate limiting (burst protection). | Wait 2-5 seconds and retry. NOT a cap error. |

## Critical Distinction

**"traceSummary specificity" IS NOT EPOCH_CAP.** If you submit a quick low-effort
trace to test caps and get this error, the wallet still has mining slots open.
The summary just needs to be better quality.

**EPOCH_CAP always says "Maximum 12 regular challenge"** — never "specificity"
or "already submitted."

## Audit Procedure

1. Create a minimal ~500-char trace with a deliberately short summary
2. Submit from each wallet to any open challenge (regardless of poster)
3. Decode each response using the table above
4. For wallets returning "specificity": they are OPEN, submit with proper quality traces
5. For wallets returning "Maximum 12": they are CAPPED, skip
6. For wallets returning "own challenge": route to a different challenge

## Why This Matters

Prior to this discovery (May 31), sessions would stop mining when they saw
rejection errors, assuming all wallets were at cap. In reality, the rejection
was often just summary quality — not cap-related. This decoder prevents
premature session termination and missed reward opportunities.