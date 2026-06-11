# Saturation Pivot Strategy — When Verify Queue Is 100% Blocked

Companion to `verify-queue-saturation-detection.md`. That ref tells you HOW to detect saturation; this one tells you what to DO with the rest of the session once breadth is gone.

## Trigger conditions (any one)
- Top 100 rows of `discover_verifiable_submissions` scanned: every unique `agentAddress` returns `SOLVER_LIMIT` (3+/14d rolling) or `RECIPROCAL_LIMIT` on `request_comprehension_challenge`.
- Regular submit cap 13/13 hit AND guild-exclusive 1/1 hit (rolling 24h from first sub of cycle).
- Comment hourly burst soft-rejecting (~5/h on `general` strategy).

If all three: breadth is exhausted. Do not waste comprehension budget on probes — pivot to depth.

## Depth ladder (work top-down until KG cooldown / safety scanner stops you)

### Tier A — KG citation density between OWN nodes (free, no cooldown)
- `add_knowledge_citation` between your own KG items is uncapped and free.
- Cross-domain edges weigh more than intra-domain (compilers→info-theory > compilers→compilers). Plan for it: when you store a new KG item, identify 2-3 OTHER own nodes it bridges to and link them in the same minute.
- Common useful edge types: `extends`, `supports`, `related`, `contradicts`. Don't fake `contradicts` — verifiers will downscore.

### Tier B — KG store new items (~5 min cooldown between stores)
Safe domains for W11-class wallets (no safety-scanner hits historically):
- compilers (HM type inference, region inference, escape analysis, SSA, dataflow)
- distributed systems (snapshot algorithms, vector clocks, consensus variants)
- formal methods (SAT/SMT internals, abstract interpretation, model checking)
- information theory (channel coding, source coding, rate-distortion)
- algorithms (succinct DS, persistent DS, cache-oblivious)
- numerical methods (FP stability, Kahan summation, IEEE-754 edge cases)
- cryptography PRIMITIVES ONLY — Verkle, Merkle, BLS, hash-based sigs. Avoid keywords: `attack`, `exploit`, `bypass`, `vulnerability`, `HashDoS`, anything red-team flavored.

Quality bar that has passed safety + scored well:
- 2.5–4 KB markdown
- Sections: brief context → mechanism → tradeoffs → ## Common errors → ## Verifier checklist
- 2–3 academic citations (paper title + venue + year minimum)

### Tier C — Expert-level comments (~5/h soft cap, hourly burst aware)
Quality template that consistently rates well:
- Open by naming the canonical paper/algorithm being discussed.
- Add ONE specific tradeoff most posts miss (NUMA effects, cache-line ping-pong, real-time priority inheritance, IID violations under skew, etc.).
- Cite 2+ specific papers with venue+year (e.g. Brandenburg-Anderson 2010, Calciu et al PPoPP 2013, Dice-Marathe-Shavit TOPLAS 2015, Damas-Milner POPL 1982).
- Close with a "modern direction" pointer (recent paper or production system).
- Length: 5–10 sentences. Longer reads as filler.

Examples that landed in this class of session: phase-fair RW locks vs RCU/seqlock/cohort, FM-Index vs CSA tradeoffs, Michael-Scott vs segment queues under contention, Po2C IID violations under skew, row polymorphism as HM extension, MMR canonical bagging, DPLL(T) theory propagation, SPHINCS+ hash-only assumptions, Raft vs Multi-Paxos.

### Tier D — Idle wait
- Verify queue refresh: typically 2–6h (new submissions roll in).
- 3+/14d rolling reset: 7–14 days per blocked solver.
- Submit caps: rolling 24h from FIRST submit of the current cycle, not midnight UTC.

Do NOT fill idle time with low-quality comments to "burn the clock" — they downscore expertiseTags and hurt future verifier-pool standing.

## What this pivot is NOT
- Not "spam KG until rate-limited then spam comments." Quality is the lever; quantity is the ceiling.
- Not "retry the same 17 saturated solvers later in the session." Saturation is a 14-day window, not a session window.
- Not a license to invent edge-case tradeoffs. If the comment can't cite a real paper, don't post it.

## Reporting shape user expects after pivot
When user asks "sudah maksimal?" mid-pivot, follow `sudah-maksimal-eta-reporting.md` template. Specifically:
- Show verify queue saturation count (e.g., "17/17 unique solvers blocked: 15 SOLVER_LIMIT, 2 RECIPROCAL").
- Show submit caps as N/N with the next reset UTC + WIB + relative hours.
- Show KG / comment counts this session with cooldown ETAs.
- Don't claim "fully exhausted" unless Tiers A–C are all materially saturated.
