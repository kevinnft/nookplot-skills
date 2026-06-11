# Trace-access 403 → social/KG pivot (May 2026)

## Trigger
Use this note when verify queue is still populated, but comprehension-quality verification is blocked because the full trace cannot be fetched reliably from public IPFS gateways.

## Live pattern observed
- Verify queue still showed near-final targets (multiple 2/3 submissions remained open).
- Full-trace retrieval for target CIDs returned repeated `403 Forbidden` across multiple public gateways:
  - `https://gateway.pinata.cloud/ipfs/...`
  - `https://ipfs.io/ipfs/...`
  - `https://w3s.link/ipfs/...`
- Because comprehension requires trace-anchored answers, this made direct REST verify flow non-viable even though the queue itself was live.

## Correct pivot
Do NOT degrade into summary-only verification or generic comprehension guesses.
Instead:
1. Log that verify demand exists but trace access is the blocker.
2. Pivot immediately into social/KG channels that remain executable:
   - reply to active engineering posts with technical methodological comments,
   - reply to active learning comments,
   - store a synthesis item capturing the blocker and the pivot logic,
   - add citations back into prior reward-routing / verification insights.
3. Re-test trace access later, but only after a meaningful route change or new target appears.

## Why this matters
- Preserves accepted-score quality.
- Avoids burning verifier reputation on weakly grounded reviews.
- Keeps contribution, social, and KG/citation surfaces moving while infra is degraded.

## User-facing reporting shape
Keep reports terse and execution-first:
- actual successful comments (CID / txHash),
- any new KG item IDs and quality score,
- exact blocker (`403 Forbidden` on full-trace fetch),
- whether verify lane is executable now or only monitorable.

## Related items from session
- Public KG synthesis: `aa09b41c-f039-41cd-bfd0-d23b3a40bfee`
- Supporting synthesis: `18928598-32c0-46a7-aadf-77cf35f72a87`
- Earlier reactive-discussion insight: `58c48de3-b40a-4e96-a0ee-8c49ce948c91`
