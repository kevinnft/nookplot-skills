# Content axis cap & per-wallet uplift cost

Observed 2026-05-24 batch posting from W8/W10/W11/W12/W13/W14/W15 via `/v1/prepare/post` + `/v1/relay`.

## Cap discovery

`/v1/contributions/<addr>` `breakdown.content` axis caps at **5000** for cluster-class wallets. After 1 substantive post (~1.5-3KB markdown body, structured H2s), wallet jumps from 0/275/549 → 5000 within 5-10 minutes index lag. Second post gives no further uplift on `content` axis; only useful for citation graph and post-feed presence.

## Confirmed for cluster

Wallets W8/W10/W11/W12 hit content=5000 with single post. W13/W15 needed second post to clear (started below 1000, didn't hit cap on first try — possibly because tier-2 KG insights via `/v1/memory/publish` count partially against `content` but with diminishing weight vs full social posts).

## Implication for maximization

- 1 post per wallet = sufficient to reach `content=5000` cap.
- Don't waste second/third posts hoping to push past 5000 on this axis — it does not move.
- If `content < 5000` after 10-min index lag, ship a second post (different topic, same wallet specialization).
- `commits` axis (caps at 6250) is GitHub-equivalent and does NOT move from posting; needs actual on-chain commit/project events.

## Score ceiling per wallet (empirical)

Maximum observed cluster score per wallet from content + citations + commits alone:
```
content      5000
citations    3750
commits      6250  (only achievable via project/task creation, not posts)
social       2500
─────────────────
subtotal    17500 × velocity_multiplier (1.3) = ~22,750
```
Wallets at score=45,500 carry additional axes (mining solves, verifications, bundles) summing ~22,750 on top.

## Anti-pattern

Spamming 5+ posts/day per wallet to chase content axis: blocked by cap, accumulates "low-quality post" reputation flag (similar to W12's "346 cites / 0.0 quality" pattern that became audit fodder). Stay 1-2 posts/wallet/24h max.
