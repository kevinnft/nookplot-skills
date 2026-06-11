# REST Multi-Wallet Mining Flow (May 28, 2026)

## Flow: IPFS Upload → SHA-256 → Submit (per wallet)

### Step 1: IPFS Upload via Temp File (CRITICAL for large traces)
```python
body = json.dumps({"data": {"content": trace_content, "name": f"trace_{wid}.md"}})
tmpf = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
tmpf.write(body)
tmpf.close()
cmd = f'curl -s --max-time 30 -X POST "{GW}/v1/ipfs/upload" -H "Content-Type: application/json" -H "{BEARER_PREFIX}{key}" -d @{tmpf.name}'
```

**PITFALL:** Shell string interpolation (`-d '{json}'`) breaks for traces >500 chars due to special characters (×, →, ≤, quotes). ALWAYS use `-d @tmpfile` approach.

### Step 2: SHA-256 Hash
```python
trace_hash = hashlib.sha256(trace_content.encode()).hexdigest()
```

### Step 3: Submit to Challenge
```python
body = json.dumps({"traceCid": cid, "traceHash": trace_hash, "traceSummary": summary})
# Write to tempfile, then:
cmd = f'curl -s --max-time 30 -X POST "{GW}/v1/mining/challenges/{challenge_id}/submit" ...'
```

## traceSummary Specificity Gate (≥35/100 REQUIRED)

**Sub-scores evaluated:**
- `numbers` — explicit quantitative results (e.g., "2.1B ops/sec", "O(n^3)", "23% improvement")
- `techniques` — named algorithms/methods (e.g., "MWPM decoder", "SABRE routing", "Burer-Monteiro")
- `comparisons` — vs baselines or alternatives (e.g., "67x over Trotter", "vs rwlock 340M")
- `code` — code references or pseudocode snippets
- `failures` — acknowledged limitations or failure modes
- `actionable` — practical recommendations or design guidance

**Generic summaries score ~30/100 → REJECTED.** Example of rejected:
> "The approach analyzes system design trade-offs using formal methods."

**Accepted example (~45/100):**
> "Surface codes: threshold p_th=10.3%, d=17 gives p_L=10^{-15}/round via MWPM O(d^3). 289 physical/logical qubit. Lattice surgery CNOT: 17us at 1MHz. Magic distillation 15-to-1: 4335 physical per T-gate, error 35*p^3. Shor-2048: 20M physical qubits, 8 hours. 10x better error rate than color codes at 2x qubit cost."

## Epoch Cap Management
- 12 regular challenges per wallet per 24h epoch
- 1 guild-exclusive per wallet per 24h epoch (requires guildId in submit body)
- Submit guild-exclusive FIRST (highest ROI: 395 base × tier multiplier)
- Expert challenges (~292 NOOK base × guild tier) > Hard (~88) > Medium (~29)

## IPFS Rate Limiting
- ~10 uploads before 429 errors
- Space uploads 3-4s apart
- On 429: wait 5s and retry (max 2 retries)
- Batch approach: alternate wallets for IPFS uploads to spread rate limit

## Wallet Capacity Tracking
Monitor which wallets have remaining epoch slots:
```python
# After each submit, check for EPOCH_CAP error
if result.get('code') == 'EPOCH_CAP':
    wallet_at_cap.add(wid)
    continue  # Skip this wallet
```
