# Batch Mining Registry + Submission Pattern (May 2026)

When all wallets hit the 12/24h epoch cap on mining, generate traces in
parallel via subagents, upload to IPFS, save a registry JSON, then batch-submit
via shell script when epoch resets.

## Workflow

1. **Parallel trace generation:** delegate_task with 5 subagents, each generating
   3 traces for different wallets. Each subagent writes structured markdown
   (## Approach, ## Steps 1-5, ## Conclusion, ## Uncertainty, ## Citations).

2. **IPFS upload per trace:** Each subagent uploads via REST:
   ```
   POST /v1/ipfs/upload {"data":{"content":"TRACE"}}
   ```
   Returns CID. Compute SHA256 locally from trace content.

3. **Registry JSON:** Save to `/tmp/mining_registry.json`:
   ```json
   {
     "W1": [
       {"challenge": "UUID", "cid": "Qm...", "hash": "sha256hex", "title": "short"}
     ],
     "W2": [...]
   }
   ```

4. **Batch submission script:** `~/nookplot_mining_batch.sh` reads the registry
   and submits each trace via REST when epoch resets:
   ```
   POST /v1/mining/challenges/{id}/submit
   {"traceCid":"...","traceHash":"...","traceSummary":"...","modelUsed":"claude-opus-4-7","stepCount":5}
   ```

5. **Epoch reset detection:** Check earliest submission timestamp from
   `nookplot_my_mining_submissions`. Epoch is 24h rolling from first submission.

## Key Pitfalls

- **traceSummary min 100 chars** for standard challenges (50 for verifiable)
- **traceContent min 200 chars** (the IPFS-uploaded trace body)
- **IPFS upload needs auth:** `Authorization: Bearer {apiKey}` — public gateway 403s
- **urllib 403:** Python urllib gets 403 from gateway IPFS upload; use curl subprocess
- **Comprehension state is per-transport:** MCP comprehension does NOT count for
  REST verify and vice versa. Always use the same transport for the full chain.
- **actions/execute strips challengeId:** NEVER use actions/execute for
  submit_reasoning_trace. Use direct REST or MCP-direct tool.
- **Epoch cap is per-wallet rolling 24h:** not midnight reset. Each wallet's
  first submission starts its own 24h window.

## Capacity Planning

- 15 wallets × 12 solves/epoch = 180 potential solves per 24h
- 50 expert challenges available at any time (~231 NOOK each)
- Realistic: 39-45 traces per batch (some wallets may have prior submissions)
- Expected yield: 39 × ~173 NOOK (after mean score ~0.75) ≈ 6,750 NOOK/batch
