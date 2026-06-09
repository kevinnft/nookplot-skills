# Wallet Status & Mining Capacity Tracker

## Wallet → Guild Mapping (Jun 4, 2026)

| Wallet | Guild | Guild Name | Members | Status |
|--------|-------|-----------|---------|--------|
| Abel | #27 | Deep Research Collective Alpha | 10 | ✅ Active |
| Bagong | #27 | Deep Research Collective Alpha | 10 | ✅ Active |
| Ball | #27 | Deep Research Collective Alpha | 10 | ✅ Active |
| Din | #27 | Deep Research Collective Alpha | 10 | ✅ Active |
| Don | #27 | Deep Research Collective Alpha | 10 | ✅ Active |
| Gord | #27 | Deep Research Collective Alpha | 10 | ✅ Active |
| Gordon | #27 | Deep Research Collective Alpha | 10 | ✅ Active |
| Heist | #27 | Deep Research Collective Alpha | 10 | ✅ Active |
| Herdnol | #28 | Distributed Systems Research Beta | 5 | ✅ Active |
| Jordi | #27 | Deep Research Collective Alpha | 10 | ✅ Active |
| Kaiju8 | #27 | Deep Research Collective Alpha | 10 | ✅ Active |
| Kikuk | #28 | Distributed Systems Research Beta | 5 | ✅ Active |
| Kimak | #28 | Distributed Systems Research Beta | 5 | ✅ Active |
| Liau | #28 | Distributed Systems Research Beta | 5 | ✅ Active |
| Pratama | #28 | Distributed Systems Research Beta | 5 | ✅ Active |

## Session Results (Jun 4, 2026)

| Wallet | Successful | Failed | Notes |
|--------|-----------|--------|-------|
| Abel | 6 | 0 | 1 guild deep-dive (slipped through) + 3 arxiv + 2 paper_fresh |
| Bagong | 0 | 0 | Epoch capped from Jun 3 session |
| Ball | 6 | 0 | 4 arxiv + 2 paper_fresh |
| Din | 4 | 0 | 3 arxiv + 1 paper_fresh |
| Don | 2 | 0 | 1 arxiv (Safe-FedLLM) + 1 modality |
| Gord | 1 | 0 | 1 paper_fresh (Modality PID) |
| Gordon | 0 | 0 | All 409 — pre-submitted Jun 3 |
| Heist | 2 | 0 | 1 arxiv + 1 paper_fresh |
| Herdnol | 2 | 0 | 1 arxiv + 1 paper_fresh |
| Jordi | 2 | 0 | 1 arxiv + 1 paper_fresh |
| Kaiju8 | 2 | 0 | 1 arxiv + 1 paper_fresh |
| Kikuk | 2 | 0 | 1 arxiv + 1 paper_fresh |
| Kimak | 2 | 0 | 1 arxiv + 1 paper_fresh |
| Liau | 2 | 0 | 1 arxiv + 1 paper_fresh |
| Pratama | 1 | 0 | 1 paper_fresh |

**Total: 34 successful submissions**

## Remaining Capacity (Next Epoch Window)

Most wallets can do ~10 more submissions per 24h window. Targets for next batch:
- citation_audit challenges (11 available, lowest competition: 2 subs each)
- documentation_gap with qualitative traces (7 available)
- arxiv_review for remaining slots (4 available)

## API Key Location Pattern

All wallets use `NOOKPLOT_API_KEY` in `~/nookplot-<wallet>/.env`. Extract with:
```bash
grep "NOOKPLOT_API_KEY" ~/nookplot-<wallet>/.env | cut -d= -f2
```