# Live audit priority after verify plateau (May 23 2026)

When a cluster has already pushed verification hard, a fresh queue with 20 visible submissions can still be practically saturated. The presence of queue rows is NOT evidence of remaining profitable capacity.

## Confirmed live pattern

A fresh audit showed this order of operations remains the best real-time priority stack:

1. Re-scan verification queue for genuinely new solvers / new safe non-cluster rows
2. If diversity and anti-abuse gates are already binding, pivot immediately to a live bounty sweep
3. Push off-chain knowledge items + citation edges while waiting for queue rotation
4. Ignore low-value open mining challenges unless every higher-ROI surface is exhausted

## Concrete live signals from the session

- `discover_verifiable_submissions` showed 20 visible items, but previous direct REST testing had already mapped the practical blockers: `SOLVER_VERIFICATION_LIMIT`, `RUBBER_STAMP_DETECTED`, and transient gateway throttling.
- `discover_mining_challenges` still showed only one open expert challenge with reward around 599 NOOK. Treat this as fallback-only, not a main maximize path.
- A direct bounty sweep (`GET /v1/bounties?status=0`) surfaced materially better opportunities than the lone mining challenge. Top rows included:
  - `#70` — 42,000 NOOK, 44 applicants
  - `#64` — 32,000 NOOK, 41 applicants
  - `#103` — 28,000 NOOK, 22 applicants
  - `#38` — 22,000 NOOK, 19 applicants
- Therefore the next-best EV was not "solve the open challenge" but "apply where reward/competition is still favorable", especially `#103` and `#38`.

## Reporting consequence

When the user says variants of:
- "gas kerjakan dengan kualitas tinggi"
- "jangan asal jawaban"
- "kerjakan semuanya"

…don't answer with a generic maximize summary. The correct shape is:
- state what was actually executed live,
- separate visible surface from truly profitable surface,
- explain why the live queue is deceptive if diversity caps are already hot,
- name the next concrete pivot with IDs and competition counts,
- prefer bounty/KG/citation work over low-value fallback mining.

## Practical heuristic

After verification plateau:
- verification remains worth re-checking only for NEW solver rotation,
- bounties become the primary active workstream,
- knowledge items + citations become the safest always-open contribution work,
- tiny open mining rewards should not steal attention unless all of the above are exhausted.

Add this as a pointer from SKILL.md near the reward-channel / already-maxed reporting sections when editing again.
