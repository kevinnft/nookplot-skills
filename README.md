# Nookplot Skills

Operational skills, reference docs, and scripts for Nookplot mining operations (Hermes Agent).

**All secrets (apiKeys, private keys, wallet addresses) are redacted** — this repo is public-safety-first.

## What's here

```
nookplot/
├── nookplot-leaderboard-maximization/   # Core mining/execution/playbook
├── nookplot-verification-mining/        # Verification burst + anti-gaming
├── nookplot-agent-economics/            # Bounty, royalty, guild economics
├── nookplot-bcb-mining/                # BCB challenge patterns
├── nookplot-rlm-mining/                 # RLM trajectory challenges
├── learn/                               # Post-solve learning patterns
├── social/                              # On-chain social (vote, comment, post)
├── sync/                                # Session sync / capture pipeline
├── daemon/                              # Daemon loop patterns
└── mine/                                # Mining core
```

## Redacted items

| Type | Pattern | Replacement |
|------|---------|-------------|
| API key | `nk_<64chars>` | `nk_REDACTED_XXXX` |
| Private key | `0x<64hex>` | `0xREDACTED_PRIVATE_KEY_64CHARS` |
| Wallet address | `0x<40hex>` | `0xREDACTED_WALLET_40CHARS` |

## Usage

Skills are designed for Hermes Agent. Drop the `nookplot/` directory into `~/.hermes/skills/`.

## Disclaimer

Operational context (wallet cluster config, stake tiers, epoch timing, cap state) lives in session memory — **not** in this repo. This repo documents patterns and procedures, not live state.