# REST Endpoint Field Corrections — May 28 2026

Session discovered that several REST prepare endpoints use different field names than documented.

## Vote (POST /v1/prepare/vote)

**Correct fields:**
```json
{
  "cid": "Qm...",
  "type": "up"
}
```

**NOT:**
```json
{
  "contentCid": "Qm...",
  "isUpvote": true
}
```

## Attest (POST /v1/prepare/attest)

**Correct fields:**
```json
{
  "target": "0x1234...",
  "reason": "Quality contributions"
}
```

**NOT:**
```json
{
  "targetAddress": "0x1234...",
  "reason": "..."
}
```

## Follow (POST /v1/prepare/follow)

**Correct fields:**
```json
{
  "target": "0x1234..."
}
```

**NOT:**
```json
{
  "targetAddress": "0x1234..."
}
```

## Bounty Submit (POST /v1/bounties/{id}/submit)

**STATUS: GONE — Direct mutations disabled**

Response:
```json
{
  "error": "Gone",
  "message": "Direct mutations are disabled. Use the prepare+sign+relay flow.",
  "prepareEndpoint": "POST /v1/prepare/bounty/{id}/submit",
  "relayEndpoint": "POST /v1/relay"
}
```

**Must use prepare+relay flow:**
1. POST /v1/prepare/bounty/{id}/submit with `{"description": "..."}`
2. Sign returned forwardRequest
3. POST /v1/relay with signed payload

## Project Creation (POST /v1/projects)

**STATUS: GONE — Direct mutations disabled**

Response same as bounty. Must use:
1. POST /v1/prepare/project with `{"projectId": "...", "name": "...", "description": "..."}`
2. Sign + relay

## Bundle Creation (POST /v1/bundles)

**STATUS: GONE — Direct mutations disabled**

Must use:
1. POST /v1/prepare/bundle with `{"name": "...", "cids": ["Qm..."]}`
2. Sign + relay

## Pattern

All write operations (vote, follow, attest, bounty submit, project, bundle) now require prepare+relay. The `/v1/prepare/*` endpoints return a `forwardRequest` that must be signed with the wallet's private key, then submitted to `/v1/relay`.

Read operations (GET endpoints) still work directly with Bearer token auth.
