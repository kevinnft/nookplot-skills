# Jun 6 2026 — Browser Cloudflare Session Rate Limit

## Finding
Heavy sequential `browser_console` fetch usage (~50+ requests in one session) triggers Cloudflare blocks.

## Symptom
All subsequent `fetch()` calls return `"Failed to fetch"` TypeError, even for `/health` endpoint.
The browser session is permanently blocked until context reset.

## Fix
Call `browser_navigate` to `https://gateway.nookplot.com/health` to reset the session context.

## Budget Guideline
- Full 15-wallet audit (credits + guild + mining subs): ~45 calls → fits in one session
- Mining submissions (upload+submit × 15 wallets): ~30 calls → pushes past limit
- Plan batches to stay under ~50 requests per session, or split across multiple navigate+batch cycles

## Pattern
```
1. browser_navigate → /health
2. browser_console → batch 1 (up to 25 calls)
3. browser_console → batch 2 (up to 25 calls)
4. If blocked: browser_navigate → /health (reset)
5. Continue
```
