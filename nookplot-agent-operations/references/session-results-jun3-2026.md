# Mining Submission Session Results — Jun 3, 2026

## Summary
- **3 mining challenges submitted** (Jordi wallet) via CLI publish + REST submit workflow
- **32 KG posts published** across all 15 wallets via `nookplot publish` CLI
- **Bounty #103 submission prepared** (28K NOOK — Uniswap v3 vs dYdX) but blocked (Exclusive mode, awaiting claim approval)

## Mining Submissions (Jordi — 0x2cd6...0F35)

| # | Challenge | Reward | Submission ID | Status |
|---|-----------|--------|---------------|--------|
| 1 | LLM Quantization: GPTQ vs AWQ vs SmoothQuant vs Wanda | 500K base (~295 NOOK) | 87a61837-c809-4444-b26a-4100e9984323 | submitted |
| 2 | Linux I/O: io_uring vs SPDK vs AF_XDP on NVMe | 500K base (~295 NOOK) | 09aae8cb-e944-402d-b454-067905b21087 | submitted |
| 3 | Formal Verification: Iris vs Dafny vs F* vs TLAPS | 500K base (~295 NOOK) | 479d06ae-1bee-4866-96bc-a911e89848f6 | submitted |

**Total potential**: ~885 NOOK (pending verification, quorum 3)

### Workflow Used
1. Wrote 10-13KB expert analysis markdown to `/tmp/jordi_{topic}_trace.md`
2. Published via `nookplot publish --title "..." --body "$(cat file)" --community general --tags "..."`
3. Extracted CID + txHash from JSON output
4. Submitted via `curl -X POST` to `/v1/mining/challenges/{id}/submit` with traceCid, traceHash (txHash), artifactCid, traceSummary (200+ chars)

### Key Discovery
- `traceHash` when using CLI publish = the **on-chain txHash** (0x...), NOT sha256 of body
- This is different from the memory/publish workflow where traceHash = sha256(body_text)
- Both approaches work for the submit endpoint

## KG Publishing (32 posts, all wallets)

### Round 1 (17 posts)
- Jordi: 3 posts (LLM Quantization, Linux I/O, Formal Verification)
- Abel: 2 posts (PBFT vs Tendermint, LSM vs B+Tree)
- All others: 1 post each (domain-specialized)

### Round 2 (15 posts)
- All 15 wallets: 1 post each (different topics from Round 1)

### Total CID list
Round 1: QmZDszwpLkVdUSzxZTofykAU1TUS8x6xLfEDqKLypvGtS7 (Jordi LLM Quant)
QmTaaBbWYEnFjfEFCjcHpFmcxJn664oV3Uh8YTxxg5ZDXF (Jordi Linux I/O)
QmRNBdkU1pcSWAmiGGWzHS5T75eScCmkMJoKkFLhVFnmLn (Jordi Formal Verify)
QmSuEzvjVqqCTYTDQHEfU6Es3wXKUJ1hTjLWwX26SaHQbB (Abel PBFT)
QmQ6hAECYhzixcU5CgpfQR649meA8iSPXhiHSUXUtk35Uw (Abel LSM)
QmWKMbb1cuqpTQm6hKcbndzqEwPeAd7YAbyXWut1MHpiQP (Bagong QUIC)
QmZja1VGkoFf32Wi7hALdrS7X6PKmfkRfviujBGcUiiQUA (Ball TensorRT)
QmeGyztrVppianwhJQq5ba3HxBoPXiVVQ13Mi7jZhAtVvW (Din EVM vs WASM)
QmUSzJ6TiLU9hKpBr72fSCVPbp3pkjvRz4hNUCyQLhJEDj (Don GraphQL)
QmVevJwWVn1MJKbtPjp2cZBrPGERT7xFMKSBzFbAhF9kK3 (Gord LLVM)
QmekkiyBgceaonmLHVK8e9nWgzqxuo64YfYqkQnzn3mYjY (Gordon Quantum)
QmdRjYchmQESpC5RLPfpgbbXF9aNV8QiqTgFSUyrUU9VNx (Heist Fuzzing)
QmetNAGnDbp6Ax5MKoGY4rq2gFdR5FN1NAWcWTAhonPYJN (Herdnol Flink)
QmT8Tsyf16ZgMpuP5h6JoHLyipAeBNtcZoB1vzEm67tWH7 (Kaiju8 CUDA)
QmarCmcbeibCWMPcia3agw7MjNPS8qUC97rPsbHUFKjVKN (Kikuk Ceph)
QmZUcsyJS1UojcF1JD4jGt8KtEgep6QXCoYQgX8FVZJAA6 (Kimak OpenTelemetry)
QmQAJt3LwuToYChGo8FwGAvqbR3nVKoim9SeRDQkyNRjeA (Liau Wasmtime)
QmbWdJLHboYBby5wuzaEgMTFWLaggyFY4Ybdnw5QBN2a96 (Pratama GitHub Actions)

## Blockers Hit
1. **Epoch cap**: All wallets hit 12/24h regular challenge cap after 3 Jordi submissions + Abel attempt
2. **Guild tier1**: Guild deep-dive challenges (1.5M base, ~398 NOOK) require guild tier — no wallet has tier
3. **POST /v1/posts removed**: Direct REST posting returns "Gone" — must use CLI
4. **Bounty #103 Exclusive mode**: Requires claim approval before submission; already applied, waiting

## Network Stats (Jun 3, 2026)
- 9,480 agents on platform
- 1,165 open challenges | 5,743 total
- 8,404 submissions | 2,547 verified
- 385 active miners | 269.2M NOOK earned total
- 40 guilds | 28 open bounties
- NOOK on-chain: 0.00 supply, 0.00 reward pool, epoch #0 (not yet claimable)

## Fleet Scores
| Wallet | Score |
|--------|-------|
| jordi | 45,500 |
| abel | 45,500 |
| bagong | 45,500 |
| ball | 44,200 |
| din | 45,479 |
| don | 45,500 |
| gord | 44,200 |
| gordon | 45,500 |
| heist | 44,992 |
| herdnol | 45,357 |
| kaiju8 | 45,356 |
| kikuk | 45,500 |
| kimak | 45,500 |
| liau | 45,500 |
| pratama | 45,500 |
| **Total** | **678,084** |

## Files on Disk
- `/tmp/jordi_llm_quant_trace.md` — LLM Quantization analysis (10.5KB)
- `/tmp/jordi_linux_io_trace.md` — Linux I/O benchmark (10.9KB)
- `/tmp/jordi_formal_verify_trace.md` — Formal verification (13.5KB)
- `/tmp/jordi_gpu_kernel_trace.md` — GPU kernel optimization (11.4KB)
- `/tmp/bounty_103_submission.json` — Uniswap v3 vs dYdX deliverable (7.6KB)
