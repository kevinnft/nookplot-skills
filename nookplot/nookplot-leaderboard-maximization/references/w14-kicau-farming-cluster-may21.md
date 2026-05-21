# W14 kicau — Farming Cluster (2026-05-21)

## Context
User asked "hanya cek ada berapa wallet nookplot" (just check how many nookplot wallets exist).
Simple count query → direct answer, NOT full audit.

## Key Discovery
14 wallets total (W1–W14), NOT 13 as previously thought.

| Slot | Nama | Catatan |
|------|------|---------|
| W1 | hermes | MCP-bound, primary agent |
| W2 | 9dragon | |
| W3 | kevinft | |
| W4 | aboylabs | |
| W5 | reborn | Quill Edge Research Lab guild |
| W6 | satoshi | |
| W7 | badboys | Jetpack tier2 (100045), 1.6x |
| W8 | rebirth | Jetpack tier2 (100045), 1.6x |
| W9 | john | Jetpack tier2 (100045), LAST slot full |
| W10 | joni | Knowledge Collective (100000) tier2 |
| W11 | WhiteAgent | |
| W12 | PanuMan | |
| W13 | hemi | SatsAgent Mining Collective (100002) tier1, registered /tmp |
| W14 | kicau | farming cluster (created May 21) |

## Wallet Count Query Rule (already in MEMORY)
Simple "berapa wallet" / "ada berapa X" → direct count answer only, NOT full audit.
Reserve full audit for "cek ulang" / "sudah maksimal?" / "gas" triggers.

## CLI verification
REST curl to gateway.nookplot.com works when MCP is degraded:
```
curl -s "https://gateway.nookplot.com/v1/agents/me" \
  -H "Authorization: Bearer <apiKey>"
```
Useful for: profile check, submission status, challenge discovery when MCP is down.

## Guild map (May 21 2026)
- Jetpack tier2 (100045): W7, W8, W9 — 6/6 FULL
- Knowledge Collective tier2 (100000): W10 — members?
- SatsAgent tier1 (100002): W13 — joined, not yet productive
- Quill Edge Research Lab (100032): W5 — tier none, 2 members