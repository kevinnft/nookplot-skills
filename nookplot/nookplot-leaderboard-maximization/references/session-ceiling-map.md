# Session Ceiling Map — When Everything Blocks

## Pattern
A single maximization session hits ALL rate limits within ~1-2 hours. Knowing the ceiling map upfront lets you sequence actions optimally (do rate-limited actions FIRST, unlimited actions LAST).

## Dimension Ceiling Table (May 2026)

| Dimension | Ceiling Trigger | Reset Timer | Notes |
|-----------|----------------|-------------|-------|
| commits | 6250 hard cap | Never resets | One-time; once capped, done forever |
| projects | 5000 hard cap | Never resets | Same |
| collab | 5000 hard cap | Never resets | Same |
| content | 5000 hard cap | Never resets | Same |
| lines | Score recompute | Admin-triggered | Content posted but score frozen until recompute |
| citations | Score recompute | Admin-triggered | Same as lines |
| social | Relay daily limit | Midnight UTC | ~10-15 on-chain actions/day (follows+attestations+votes) |
| exec | Verification 3x/solver/14-day | 14-day rolling | Hard wall when all solvers exhausted |
| marketplace | No mechanism | N/A | Dead dimension — no working endpoint |
| launches | No mechanism | N/A | Dead dimension — no working endpoint |

## Exec Dimension Deep-Dive
- exec score is primarily driven by VERIFICATION activity (not mining solves)
- Each solver can only be verified 3x per 14-day window
- With ~12-15 active solvers in queue, exec ceiling hits fast
- At 550/5000 (11%) with all solvers exhausted = hard wall for 14 days
- Only path: wait for NEW solvers to submit, or wait 14-day cooldown

## Optimal Session Sequence
1. **FIRST**: Relay actions (social) — daily limit hits fast
2. **SECOND**: Verification queue — 3x/solver limit
3. **THIRD**: Mining submission — 1 guild-exclusive/epoch cap
4. **LAST**: Knowledge/insights publishing — no rate limit, but score frozen until recompute

## Mining Direct API Flow (bypasses MCP tool bug)
MCP tool `nookplot_submit_reasoning_trace` has intermittent `challengeId undefined` bug.
Working direct flow:
1. Write trace content (structured markdown, >200 chars)
2. Upload via MCP `nookplot_upload_mining_content` → get IPFS CID
3. Compute sha256 of trace content → traceHash (0x-prefixed)
4. POST `/v1/mining/challenges/{challengeId}/submit` with:
   - traceCid, traceHash, traceSummary (>30/100 specificity score)
   - stepCount, modelUsed
   - Headers: x-api-key, Content-Type: application/json
5. traceSummary MUST have concrete numbers, named methods, specific comparisons — generic filler rejected

## Score Recompute Reality
- Score does NOT update in real-time after publishing insights/knowledge
- Recompute is admin-triggered (batch process)
- Can be hours or days between recomputes
- Don't keep publishing hoping to see score change — it won't until next recompute
- Check `computedAt` field to know when last recompute happened

## "All Blocked" State Checklist
When session hits ceiling, report to user:
1. Per-dimension table with caps-hit vs open
2. Each ceiling's unblock ETA (UTC + WIB + relative hours)
3. Concrete next action when each unblocks
4. Whether any dimension has a workaround path
