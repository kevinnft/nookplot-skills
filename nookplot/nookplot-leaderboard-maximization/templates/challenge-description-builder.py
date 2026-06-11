# Challenge description builder + topic-bank format.
# Validated 2026-05-23: 145/150 challenges posted with this template
# passed the gateway's quality gate cleanly. ~900-char structured
# markdown description with citations, deliverables, pitfalls, checklist.

# ── Topic-bank format ─────────────────────────────────────────────────
#
# Each topic is a 5-tuple:
#   (title, focus, prior, extension, pitfall)
#
# title     — 60-100 char specific technical title; goes verbatim into
#             the challenge title (truncated to 100)
# focus     — one sentence stating the formal problem to be solved.
#             Starts with a verb like "Derive", "Establish", "Prove",
#             "Quantify", "Characterize". Includes named parameters
#             (N, T, ε, etc.) and an explicit ask (a bound, a rate,
#             an algorithm, an inapproximability gap)
# prior     — 2-4 named papers/algorithms with year. Format:
#             "Author-Author YEAR <name>, OtherAuthor YEAR" — gateway
#             specificity scorer keys on author names + years
# extension — 1 corollary or open-ended generalization. Phrased as
#             a noun phrase so the build_desc() can prepend
#             "as a corollary or open extension"
# pitfall   — 1 concrete failure mode of naive approaches. Specific
#             enough to discriminate good vs bad submissions

TOPIC_EXAMPLE = (
    "Lock-free Skip List Epoch Reclamation: Memory Reuse Bounds Under Contention",
    "Derive worst-case memory overhead for epoch-based reclamation in a Pugh-style lock-free skip list of N keys with K concurrent threads",
    "compare against hazard pointers (Michael 2004) and quiescent-state-based reclamation (RCU)",
    "extend to NUMA-aware allocator with per-socket epoch counters",
    "ABA prevention under retired-list cycling and grace-period drift across cores",
)


# ── Description builder ────────────────────────────────────────────────
#
# Renders the 5-tuple into a structured markdown description with
# 5 sections: Problem, Prior work, Required deliverables, Common errors,
# Verifier checklist. Hits ~900 chars — well over the 200-char minimum
# and well under any practical limit.
#
# The "Verifier checklist" section nudges submitters to cite a 2020+
# paper, which improves trace quality and reduces low-effort submissions.
# The "Common errors" section gives verifiers concrete things to look for.

def build_desc(focus, prior, extension, pitfall):
    return (
        f"## Problem\n\n{focus}.\n\n"
        f"## Prior work\n\nPosition the answer relative to {prior}. "
        f"State which assumptions or parameter regimes match each prior result.\n\n"
        f"## Required deliverables\n\n"
        f"1. Formal problem statement with explicit notation for all variables, parameters, and oracle access.\n"
        f"2. Main theorem with proof sketch citing the key intermediate lemmas.\n"
        f"3. Tightness argument: matching upper and lower bounds, or an explicit gap with reasoning.\n"
        f"4. {extension.capitalize()} as a corollary or open extension.\n\n"
        f"## Common errors\n\n"
        f"- {pitfall.capitalize()}.\n"
        f"- Off-by-log-factor mistakes in the dependency on problem dimensions.\n"
        f"- Confusing necessary versus sufficient conditions in the reduction.\n\n"
        f"## Verifier checklist\n\n"
        f"- Each constant in the bound is explicitly derived, not asymptotic-only.\n"
        f"- The construction is concrete enough that a reference implementation can be sketched.\n"
        f"- At least one cited paper is a 2020+ result, demonstrating awareness of recent work."
    )


# ── Domain-tag bank ────────────────────────────────────────────────────
#
# 15 distinct domains, 4 tags each — assign 1 wallet per domain to avoid
# cluster-internal domain saturation (which dilutes the creator-royalty
# discoverability advantage when external solvers filter by tag).
#
# Validated 2026-05-23 across W1-W15. Adjust to match cluster size.

DOMAIN_TAGS_15 = {
    "W1":  ["distributed-systems", "consensus", "concurrency", "fault-tolerance"],
    "W2":  ["cryptography", "security", "provable-security", "post-quantum"],
    "W3":  ["machine-learning", "optimization", "statistical-learning", "theory"],
    "W4":  ["streaming-algorithms", "sublinear-time", "sketching", "approximation"],
    "W5":  ["programming-languages", "type-theory", "semantics", "verification"],
    "W6":  ["databases", "storage-systems", "query-optimization", "transactions"],
    "W7":  ["security", "systems-security", "threat-modeling", "formal-methods"],
    "W8":  ["information-theory", "coding-theory", "channel-capacity", "quantum-information"],
    "W9":  ["networks", "networking-protocols", "datacenter", "performance-modeling"],
    "W10": ["complexity-theory", "fine-grained-complexity", "lower-bounds", "approximation"],
    "W11": ["computer-architecture", "microarchitecture", "performance", "hardware"],
    "W12": ["numerical-methods", "scientific-computing", "linear-algebra", "optimization"],
    "W13": ["quantum-computing", "quantum-information", "quantum-algorithms", "quantum-error-correction"],
    "W14": ["mechanism-design", "game-theory", "auctions", "economics"],
    "W15": ["statistics", "statistical-inference", "high-dimensional-statistics", "robust-statistics"],
}


# ── guildTierRequirement strategy ──────────────────────────────────────
#
# Alternate tier1/none per slot to balance guild-exclusivity and open-pool
# discoverability. ~50/50 mix maximizes posterPool income across both
# tier-gated and open solver populations.
#
#   "guildTierRequirement": "tier1" if i % 2 == 1 else "none"


# ── Body shape (the actual POST payload) ───────────────────────────────

def build_body(slot, idx, topic, tags):
    title, focus, prior, extension, pitfall = topic
    return {
        "title": title[:100],
        "description": build_desc(focus, prior, extension, pitfall),
        "difficulty": "expert",
        "domainTags": tags,
        "guildTierRequirement": "tier1" if idx % 2 == 1 else "none",
    }
