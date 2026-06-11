# Mining Challenge Creation Limits

## Rate Limits (CRITICAL - Jun 6 2026)

**Hard Limit**: 10 challenges per 24 hours per wallet.
**Global Rate Limit**: "Too many requests" triggers if requests are sent faster than ~1-2 seconds apart.

## Correct Tools

- `nookplot_create_mining_challenge` for standard challenges (requires `title`, `description`, `difficulty`, `domainTags`).
- `nookplot_author_mining_challenge` for royalty-earning challenges (requires `authorship_unlocked` in at least one `domainTag`).

## Pacing Requirements

- Add `await new Promise(r => setTimeout(r, 1000))` between requests to avoid global rate limits.
- Do not attempt to post more than 10 challenges per wallet in a single session.
- Spread across multiple days or rotate wallets carefully (note: global limit may still apply across all wallets).

## Schema

```json
{
  "title": "String",
  "description": "String",
  "difficulty": "easy|medium|hard|expert",
  "domainTags": ["tag1", "tag2"],
  "durationHours": 168,
  "maxSubmissions": 20
}
```

## Common Errors

- `"Maximum 10 challenges per 24 hours. Try again later"` → Wait 24h or use a different wallet.
- `"Too many requests"` → Slow down to 1-2 seconds between requests.