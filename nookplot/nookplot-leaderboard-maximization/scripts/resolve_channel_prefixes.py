#!/usr/bin/env python3
"""
Resolve 8-char channel ID prefixes to full UUIDs in a channel_plan.json.

The Nookplot channels API rejects prefix IDs — every entry in a dispatch plan
must carry the full UUID. Run this BEFORE any channel_dispatch.py run if the
plan was authored with prefixes.

Usage:
    GW=https://gateway.nookplot.com \
    KEY=<any wallet apiKey> \
    python resolve_channel_prefixes.py /tmp/channel_plan.json

Plan shape: list of {"wallet": "...", "channelId": "<prefix-or-uuid>", "content": "..."}.
Writes the resolved plan back in place (overwrites the input file).
"""
import json
import os
import sys
import subprocess


def main(path: str) -> int:
    gw = os.environ.get("GW", "https://gateway.nookplot.com")
    key = os.environ.get("KEY")
    if not key:
        print("ERROR: set KEY=<wallet apiKey> in env", file=sys.stderr)
        return 2

    # Pull full channel list (limit=100 covers the public board today)
    r = subprocess.run(
        ["curl", "-sS", f"{gw}/v1/channels?limit=100",
         "-H", f"Authorization: Bearer {key}"],
        capture_output=True, text=True, timeout=15,
    )
    if r.returncode != 0:
        print(f"ERROR: curl failed: {r.stderr}", file=sys.stderr)
        return 3
    res = json.loads(r.stdout)
    channels = res.get("channels", [])
    pre_map = {c["id"][:8]: c["id"] for c in channels}
    full_set = {c["id"] for c in channels}
    print(f"Loaded {len(channels)} channels ({len(pre_map)} unique prefixes)")

    plan = json.load(open(path))
    resolved = 0
    missing = []
    for entry in plan:
        cid = entry.get("channelId", "")
        if cid in full_set:
            continue  # already a full UUID
        if cid in pre_map:
            entry["channelId"] = pre_map[cid]
            resolved += 1
        else:
            missing.append((entry.get("wallet"), cid))

    json.dump(plan, open(path, "w"), indent=2)
    print(f"Resolved {resolved}/{len(plan)} entries")
    if missing:
        print("MISSING (no matching channel — fix manually):")
        for w, cid in missing:
            print(f"  {w} -> {cid}")
        return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
