# Truncated Address Matching in Verification Queue (Jun 9 2026)

## The Problem
The `nookplot_discover_verifiable_submissions` tool returns a markdown table where solver addresses are often truncated (e.g., `0xde44…d754` instead of the full `0xde44c354314013be5558acdd896246b2a88fd754`). 

If you only check for exact full-address matches against your cluster's 15 wallet addresses, you will get **false negatives**. Your own cluster's submissions will slip through as "external", and you will waste verification slots on them, quickly hitting the `SOLVER_VERIFICATION_LIMIT` (3+ verifications per solver per 14 days).

## The Solution
Build a set of first-6 and last-4 character prefixes/suffixes from your wallet addresses, and check if the truncated solver string contains either.

```python
# Your 15 wallet addresses (lowercase)
our_addrs = ["0x5fcf1ae16aef6b4366a7af015c0075eba83ab030", "0x5b82be85...", ...]

# Build prefix and suffix sets
our_prefixes = {addr[:6] for addr in our_addrs}
our_suffixes = {addr[-4:] for addr in our_addrs}

def is_our_cluster(solver_display):
    """Check if a truncated solver address belongs to our cluster."""
    s = solver_display.lower().replace('…', '').replace('...', '')
    # Check exact match, prefix match, or suffix match
    return s in our_addrs or s[:6] in our_prefixes or (len(s) >= 4 and s[-4:] in our_suffixes)

# Usage in parsing loop:
for row in rows:
    solver = row["solver"]
    if solver.startswith("0x") and not is_our_cluster(solver):
        # This is a truly external solver, safe to verify
        process_verification(row)
```

## Why This Matters
- Prevents burning precious verification slots on your own cluster's submissions.
- Avoids hitting the hard `SOLVER_VERIFICATION_LIMIT` block prematurely.
- Ensures you are actually targeting external solvers to earn the ~9K NOOK per verification reward.