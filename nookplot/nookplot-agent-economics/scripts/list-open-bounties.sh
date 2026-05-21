#!/bin/bash
# Filter `nookplot bounties list` for Open entries.
# The `--json` mode returns concatenated objects that don't parse as a single
# array, and the friendly text mode has no --status filter. This wrapper
# parses the friendly text reliably with a regex.
#
# Usage:
#   bash scripts/list-open-bounties.sh           # default limit 50
#   bash scripts/list-open-bounties.sh 100       # custom limit

LIMIT="${1:-50}"

nookplot bounties list --limit "$LIMIT" 2>&1 | python3 - <<'PY'
import sys, re
out = sys.stdin.read()
records = re.findall(
    r"#(\d+)\s+(\w+)\s+([\d.]+)\s+(\w+)\s*\n\s*Community:\s+(\w+)\s*\|\s*Deadline:\s+([^\n]+)",
    out,
)
open_ones = [r for r in records if r[1] == "Open"]
print(f"Total parsed: {len(records)}, Open: {len(open_ones)}")
for rid, status, amount, token, community, deadline in open_ones:
    print(f"#{rid} | {amount} {token} | community={community} | deadline={deadline.strip()}")
PY
