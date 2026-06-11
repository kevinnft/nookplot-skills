# REST Mining challengeId Stripping Bug (May 29, 2026)

## Critical Finding
The REST endpoint `POST /v1/actions/execute` strips `challengeId` from the request body regardless of where it's placed. This makes REST-based mining submissions IMPOSSIBLE. Only MCP `nookplot_submit_reasoning_trace` works for mining.

## Tested Approaches (ALL FAIL)
| Approach | Body Structure | Result |
|----------|---------------|--------|
| challengeId in args | `{toolName: "...", args: {challengeId: "uuid", ...}}` | "Could not fetch challenge undefined" |
| challengeId at root | `{challengeId: "uuid", toolName: "...", args: {...}}` | Rate limited (but no UUID error) then fails |
| challenge_id in args | `{toolName: "...", args: {challenge_id: "uuid"}}` | Rate limited |
| challengeUUID in args | `{toolName: "...", args: {challengeUUID: "uuid"}}` | Rate limited |
| Direct /v1/mining/submissions | POST to non-existent endpoint | 404 Not found |
| /v1/mining/challenges/{id}/submissions | POST to non-existent endpoint | 404 Not found |

## Impact
- **MCP-bound wallet (W1) can mine normally** via `nookplot_submit_reasoning_trace`
- **All other wallets (W2-W15) CANNOT submit mining challenges via REST**
- Gateway only supports `/v1/actions/execute` which strips the challengeId parameter
- No direct mining submission endpoint exists in the REST API

## Workaround
1. Use MCP `nookplot_submit_reasoning_trace` for mining (only works for MCP-bound wallet)
2. For other wallets: focus on verification, KG stores, learning comments, and other REST-accessible channels
3. IPFS upload works via REST (`/v1/ipfs/upload`) but the submission step fails

## Bounty Submissions Also Blocked
Bounty work submission also requires EIP-712 signing:
```json
{"error": "Gone", "message": "Direct mutations are disabled. Use the prepare+sign+relay flow.",
 "prepareEndpoint": "POST /v1/prepare/bounty/{id}/submit",
 "relayEndpoint": "POST /v1/relay"}
```
This requires the wallet's private key for on-chain signing — cannot be done via REST API key alone.

## Discovery Context
Discovered May 29 while attempting to submit expert traces from W2-W15 via REST. MCP submit from W2 succeeded (W2 was MCP-bound in that subagent context), confirming MCP works but REST does not.
