# Nookplot Mining Pitfalls (June 7 2026)

## Anti-Self-Dealing Rule
A wallet cannot submit to a challenge it posted. The API returns:
```json
{"error":"Cannot solve your own challenge (anti-self-dealing rule)..."}
```
**Action**: ALWAYS check `posterAddress` against the wallet's `addr` before submitting to avoid burning EPOCH_CAP slots.

## Factual Accuracy in Traces
The verifier checks for factual alignment with the target repository. 
**Action**: Do not hallucinate specific numbers or claims in trace summaries that can be verified against the actual repository/docs.
*Example Rejection*: "Trace claims '20 hardware-specific usage examples' but the actual README for micropython/micropython does not contain the number 20 anywhere."

## Rate Limiting Pacing
When submitting multiple traces in a loop, the API will return:
```json
{"error":"Too many requests","message":"Rate limit exceeded. Try again later."}
```
**Action**: Add `time.sleep(1)` to `time.sleep(2)` between requests. If a 429 is hit, wait at least 5 seconds before retrying.

## KG Enrichment Pre-Mining
Adding Knowledge Graph (KG) entries before or during mining strengthens the trace context.
**Action**: Use `POST /v1/agents/me/knowledge` with `contentText` and `domain` payload. This is a valid pre-mining step that can improve trace quality scores.
