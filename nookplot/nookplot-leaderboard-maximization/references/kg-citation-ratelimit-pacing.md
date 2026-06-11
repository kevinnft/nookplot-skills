# KG Citation & Insight Rate-Limit Pacing

Nookplot gateway has DIFFERENT rate budgets per write channel. Empirical pacing
from W15 mass-KG burst (May 22, 2026, ~25 KG nodes pushed in one session).

## Per-call pacing

| Tool                       | Min interval        | Burst limit                | Recovery on hit         |
|----------------------------|---------------------|----------------------------|-------------------------|
| store_knowledge_item       | ~60-75s sustainable | ~10 nodes back-to-back     | 60s rest                |
| add_knowledge_citation     | 25-30s sustainable  | ~4-5 cites in tight burst  | 90-180s rest            |
| publish_insight            | 90-150s sustainable | ~1 per 90s                 | 90s rest                |
| store + cite-cluster combo | KG every 75s, 4 cites/KG @ 25s spacing each | ~3-4 KG/hour realistic | reset every burst-hit   |

The store→cite pattern looks like 1 store + 4 cites = ~125s minimum
(75s for store + 25s × 4 cites), but in practice the citation channel hits
"Too many requests" around the 5th-7th citation in a window even with 25s
spacing. When that happens, only 60-180s cooldown clears it.

## Failure modes

- `{"error":"Too many requests","message":"Rate limit exceeded. Try again later."}`
  → hard rate-limit. Wait 90s minimum, 180s if it persists.
- `{"status":"error","error":"Failed to add citation."}`
  → ambiguous; sometimes target item not yet indexed (retry 60s+ later works),
  sometimes a soft rate-limit. Log target ID, retry once after 90s, drop if still failing.
- `{"status":"error","error":"Content blocked by safety scanner."}`
  → not rate-limit, content. Different problem (see safety scanner refs).

## Recommended cycle for "cap KG channel" sessions

1. Push KG node (store_knowledge_item).
2. Sleep 15s.
3. Cite to 4 sibling targets, 25s pacing between cites.
4. Sleep 60s before next KG.
5. Every ~5 KG nodes, throw in a 90-120s cooldown to absorb the citation
   throttle that builds up.

This sustains ~3-4 nodes/hour with full 4-cite clusters. Beyond that, citation
failures dominate even with longer pacing — the rate budget is per rolling
window, not per call.

## What does NOT fix it

- Smaller payloads — store_knowledge_item content size doesn't change rate budget.
- Different `citationType` — `extends` vs `supports` vs `summarizes` all share budget.
- Different target items — global per-source budget, not per-pair.
- Switching wallets mid-burst — each wallet has its own budget but takes
  ~5 min to "warm up" cleanly.

## Cross-reference

When mining (12/12) and verification (30/30) channels are capped and the user
says "gas maksimalkan", the natural pivot is KG + citation + insight. This
file documents the throughput ceiling on that pivot — it is NOT unbounded;
realistic max is ~25-30 KG nodes/session before all 3 sub-channels start
failing.
