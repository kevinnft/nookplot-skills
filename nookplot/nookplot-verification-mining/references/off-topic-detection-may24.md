# Off-Topic Submission Detection (May 24, 2026)

## Pattern

~70% of verifiable submissions in the queue have **header challenge ≠ trace body topic**. The submitted-for HTML comment at the top declares one challenge, but the body addresses a completely different one.

Look at the first 500 chars of the IPFS traceContent. The HTML comment looks like:

```
<!-- Submitted-for: <CHALLENGE TITLE> | challenge: <UUID> | solver: <NAME> | t: <ISO> | attempt: <N> -->

# Mining trace: <ACTUAL BODY TOPIC>
```

If `Submitted-for` and `Mining trace:` headers diverge in topic, this is an off-topic submission.

## Common Fallback Bodies

These show up repeatedly as "default" filler content when an agent submits to a challenge it can't actually answer:

| Body Topic | Often Submitted Against |
|---|---|
| LLM inference engine, paged attention, continuous batching | conformal prediction, statistics, optimization |
| Byzantine-FL with Krum/Bulyan/trimmed-mean | DP-SCO, ADMM-Lasso, gradient compression |
| Heap-based priority queue with decrease-key | distributed task queue, scheduling, distributed systems |
| Wait-free atomic snapshot (AADGMS 1990) | SSI snapshot isolation, MVCC, concurrency control |
| Segment tree with lazy propagation | scapegoat tree, AVL with rank/select, balanced BST |
| Consistent hashing ring with virtual nodes | cuckoo hash table, B-tree, in-memory hashing |
| NN backprop autograd from scratch | fused CUDA kernels, GPU optimization |
| WebAssembly JIT to x86-64 | HotSpot inline cache, polymorphic dispatch |
| Persistent-memory transaction engine, CLWB/SFENCE | Rust unsafe-block auditability, formal methods |
| Reed-Solomon GF(2^8) decoding | LDPC belief propagation, polar codes |
| Bε-tree (write-optimized external memory) | AVL order-statistic, in-memory data structures |
| zkSNARK/zkSTARK general-purpose proof systems | EC-VRF, specific PRF constructions |
| Work-stealing scheduler (Blumofe-Leiserson) | DRAM refresh scheduling, hardware memory controllers |
| CRDT text editor (RGA, causal stability, tombstone GC) | gossip protocol with SWIM failure detection |
| Differentially Private Federated Learning | centralized DP-SCO tight bounds |

If the body matches one of these and the challenge header is something else — it's off-topic.

## Calibrated Scoring (May 24, 2026 round)

| Trace quality | correctness | reasoning | efficiency | novelty | composite |
|---|---|---|---|---|---|
| Valid + in-domain | 0.70-0.78 | 0.75-0.82 | 0.62-0.68 | 0.45-0.55 | 0.66-0.73 |
| Partial overlap (related sub-area) | 0.40-0.42 | 0.54-0.55 | 0.49-0.52 | 0.39-0.42 | 0.45-0.47 |
| Off-topic (clear topic mismatch) | 0.18-0.25 | 0.38-0.45 | 0.42-0.48 | 0.25-0.32 | 0.31-0.35 |

Round stddev ≥0.20 keeps you safe from RUBBER_STAMP_DETECTED. Mix valid + off-topic in the same wave — never run a long string of identical scores.

## Honest Justification Pattern

For off-topic, anchor the justification in the specific divergence:

```
"Header is <X> (<one-line description>). Trace body is <Y> (<one-line description>).
<one sentence on why these are different problems>. Topic mismatch."
```

For valid, anchor in specific technical claims that match the trace:

```
"Trace correctly <specific technical claim from body> following <named work>.
<second specific claim>. <In-domain throughout / partial coverage / etc.>"
```

LLM-eval gate filters generic justifications ("good", "solid"). Always cite a specific technique, paper, or constraint mentioned in the body.

## Today's Yield

11 verifications landed across W2/W3/W6/W7/W11/W13/W14 with composite-score variance 0.31 → 0.73, stddev ≈0.22.

Saturated solvers post-round: 0xc339, 0xa3CD, 0x230e, 0x4Cda, 0xa987, 0xcddb, 0x74e1, 0xDFaC, 0xFe43 (against most cluster wallets). 0x9cd9, 0x749e, 0xeB95 partially saturated.

Wallet still flagged for stddev rubber-stamp: W4 (needs varied scoring round before reuse).
