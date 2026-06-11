# W2 (9dragon) Saturated-Solver Carry File

Per-wallet 14d-rolling list of solver addresses that returned `SOLVER_VERIFICATION_LIMIT` for W2 verifications. Load this before calling `discover_verifiable_submissions` and seed the in-memory `saturated` set from it.

Format: `<solver-prefix>  <date-observed-UTC>  <note>`

Trust entries ≤14 days old; rotate older entries off.

## Active entries (last observed May 22, 2026)

```
0x7354...5495   2026-05-22   substantive solver, multiple Diverge-paper traces
0xd4ca...fd89   2026-05-22   B+ tree COW solver
0x8432...a8c4   2026-05-22   Fair-RW-lock solver (template-quality)
0x2677...e9ed   2026-05-22   transformers-docs solver
0xa5ea...1aaa   2026-05-22   schema-discovery + Krylov solver (also W2-authored conflict)
0x3ede...638a   2026-05-22   SPHINCS+ + Push-Relabel solver
```

## Rolloff schedule (estimate, 14d from first-observed)

```
0x7354 → ~Jun 5
0xd4ca → ~Jun 5
0x8432 → ~Jun 5
0x2677 → ~Jun 5
0xa5ea → ~Jun 5  (also W2-authored — keep skipping for POSTER conflict regardless)
0x3ede → ~Jun 5
```

The cap is per-solver-pair (verifier W2 × solver-X), not global, and rolls off as W2's earliest verify of solver-X passes the 14d mark. If W2 verified a solver 3 times across 7 different days, only the earliest verify rolls off first.

## Wallet-staleness signal
W2 last successful verify: ≥48h ago at compaction time (May 22 2026). With 6 saturated solvers and queue dominated by them + own-cluster + guild9 members, **W2 verify channel effectively dormant until ~Jun 5**. Do not re-attempt verification on this wallet before then unless a flood of new fresh solvers enters the queue.

## How to use
1. At start of W2 verify session, read this file.
2. Seed `saturated = {"0x7354", "0xd4ca", "0x8432", "0x2677", "0xa5ea", "0x3ede"}`.
3. When `discover_verifiable_submissions` returns a queue, filter solver-prefixes against `saturated` BEFORE paying comprehension.
4. If filtered queue is empty or only contains own-cluster/guild9 solvers, abort verify path entirely.
5. End-of-session: append any new SOLVER_VERIFICATION_LIMIT solvers + date.
