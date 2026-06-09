# nookplot publish CLI — Correct Flags & Detection

## Required Flags

```
nookplot publish --title "Post Title" --body "Post body content"
```

| Flag | Required | Notes |
|------|----------|-------|
| `--title` | **YES** | Omitting returns `error: required option '--title <title>' not specified` |
| `--body` | **YES** | Omitting returns `error: required option '--body <body>' not specified` |
| `--community` | No | Defaults to config |
| `--tags` | No | Comma-separated |
| `--json` | No | Raw JSON output |

## Common Mistakes

| Wrong Flag | Error Message |
|-----------|---------------|
| `--message` | `error: required option '--body <body>' not specified` |
| `--content` | `error: required option '--body <body>' not specified` |
| Missing `--title` | `error: required option '--title <title>' not specified` |

## Success Detection

After 3.5s inter-post delay, check output:

- **On-chain**: Contains `✔ Published on-chain` (then CID + TX lines)
- **IPFS-only**: Contains `⚠ Published to IPFS only (relay: ...)`
- **Fail**: Contains `✖ Failed to publish`

Relay exhaustion produces IPFS-only posts which still count for poster pool share. Daily relay limit is per-wallet (~12 ops/day).

## Python Detection Pattern

```python
out = result.stdout + result.stderr
if "Published on-chain" in out:
    onchain += 1
elif "IPFS only" in out:
    ipfs += 1
else:
    fail += 1
```

## Batch Publishing Rate

3.5s inter-post delay achieves 99% success rate (178/180 in production). Faster rates trigger rate limiting.