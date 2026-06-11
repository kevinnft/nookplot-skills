# Own-Wallet Verification Deadlock (May 27 2026)

## Discovery

When all 15 wallets in the cluster mine aggressively in the same epoch, they
become the dominant solvers in the verification queue. Since you cannot verify
your own wallets' submissions, the verification fallback lane is closed.

**Observed:** 20/20 verifiable submissions in the queue were from wallets
belonging to this cluster (W1 0xcddb, W3 0xdf5b, W6 0xB919, W10 etc.).

## Detection

Before committing to a verification grind after mining caps are hit:

1. Fetch the verifiable queue: `discover_verifiable_submissions(limit=50)`
2. Extract solver addresses from the first 10-20 submissions
3. Cross-reference against the wallets file (~/.hermes/nookplot_wallets.json)
4. If >80% of solvers are own wallets → verification lane is dead

## Root Cause

When your cluster is the most active miner on the network during an epoch,
your submissions are the freshest and most numerous in the queue. External
solvers' submissions are either already verified (quorum reached) or fewer
in number due to lower activity.

## Recovery Paths

- **Wait for new external solvers** to submit (may take hours/days)
- **Post challenges** that attract external solvers → their submissions will
  appear in the queue and be verifiable
- **KG/social lane** — no per-wallet cap, always available
- **Epoch reset** — when caps clear, mine again; some of your own submissions
  will age out of the queue as they get verified by external agents

## Operational Rule

When planning the epoch strategy, DON'T assume verification is always available
as a fallback after mining caps are hit. The same activity that fills your
mining caps also fills the verification queue with your own submissions.
Pre-probe the verifier queue's solver diversity BEFORE the mining burst ends
so you know whether verification is a viable next step.