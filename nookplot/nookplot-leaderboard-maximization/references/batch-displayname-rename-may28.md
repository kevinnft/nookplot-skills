# Batch displayName Rename via REST (May 28 2026)

## Context
User requested reverting all 15 wallets from `[Domain]-Expert-W[N]` format back to original registration names (hermes, 9dragon, kevinft, aboylabs, reborn, satoshi, badboys, rebirth, john, joni, WhiteAgent, PanuMan, hemi, kicau, lucky).

## Endpoint
```
PATCH /v1/agents/me
Authorization: Bearer <apiKe...ype: application/json

{"display_name": "name"}   # SNAKE_CASE required — camelCase displayName returns 400
```

## Rate-Limit Behavior (Verified Live May 28)
- **1.5s between requests**: triggers 429 after ~2 requests (too aggressive)
- **3s between requests**: sustained batch of ~11 before 429 (sweet spot for first pass)
- **After 429**: 10-15s cooldown, then retry remaining with **5s delays** (all succeed)
- **Total for 15 wallets**: ~3 passes, ~3 minutes wall time

## Strategy (3-pass approach)
1. **Pass 1**: iterate all wallets with 3s delay, collect failures
2. **Pass 2**: wait 15s cooldown, retry only failed wallets with 5s delay
3. **Pass 3**: if any remain, wait 15s, retry with 5s delay (usually clears all)

## Backup Before Bulk Rename
```bash
cp ~/.hermes/nookplot_wallets.json ~/.hermes/backups/nookplot_wallets.json.pre-restore-names-$(date +%s).bak
```

## Finding Original Names
Original displayNames may be scattered across:
- `~/.hermes/nookplot_wallets.json.pre-w6` (W1-W5 originals)
- `~/.hermes/backups/nookplot_wallets.json.bak` (most wallets)
- `~/.hermes/backups/nookplot_wallets.json.pre-rename.bak` (W1-W7)
- `~/.hermes/backups/nookplot_wallets.json.bak.*` (timestamped snapshots)
- `~/.hermes/backups/nookplot_wallets_pre_w11_*.bak` (W1-W10)
- `~/.hermes/backups/nookplot_wallets_pre_w12fix_*.bak` (W1-W11 with PanuMan)
- Skill references in `references/w13-hemi-setup-may21-2026.md`, `w14-kicau-*.md`, `w15-lucky-*.md`

## W1 Special Case
W1 is MCP-bound (no `pk` field), but PATCH /v1/agents/me works with the MCP apiKey — confirmed live.

## Pitfalls
- **Snake_case `display_name` is mandatory** — camelCase `displayName` silently fails with 400
- **No validation on response**: check `resp.displayName == expected` to confirm success
- **Rate limit is per-IP, not per-wallet**: all 15 wallets share the same rate-limit bucket from same machine
- **W11 original name**: `WhiteAgent` (not `PanuMan` — PanuMan is W12)
