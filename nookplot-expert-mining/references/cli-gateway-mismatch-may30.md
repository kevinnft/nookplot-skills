# Gateway v0.5.32 CLI Compatibility Issues (May 30 2026)

## Submission Endpoint Mismatch

**CLI v0.7.30-0.7.32 sends:**
```
POST /v1/mining/submissions/{challengeId}
Body: {traceContent: "...", guildId: "..."}
```
**Gateway response:** `404: "Endpoint does not exist."`

**Correct endpoint:**
```
POST /v1/mining/challenges/{id}/submit
Body: {traceCid: "Qm...", traceHash: "..."}
```

The CLI uses raw trace content; gateway v0.5.32 requires IPFS CID + hash.
This breaks the entire mining pipeline after inference succeeds.

## Root Cause
- CLI was built for gateway pre-v0.5.32 which accepted raw traceContent
- Gateway v0.5.32 changed to IPFS-based submission flow
- CLI v0.7.32 was NOT updated to match

## Workaround Status (May 30)
- Inference: ✅ Patched (local MiniMax calls)
- Submission: ❌ Needs IPFS upload integration in the patched runtime
- No known workaround for submission yet — need to add IPFS upload to mining.js patch