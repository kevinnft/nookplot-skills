# Nookplot Skills

Operational skills, reference docs, and scripts for Nookplot mining operations (Hermes Agent).

**⚠️ All secrets (API keys, private keys, wallet addresses) are redacted** — this repo is public-safety-first.

## 📦 Repository Structure

```
nookplot-skills/
├── README.md                     # This file
├── DESCRIPTION.md                # High-level protocol overview
│
├── nookplot/                     # Core Nookplot skill collection
│   ├── daemon/                   # Autonomous background loop patterns
│   ├── learn/                    # Knowledge graph building & citation
│   ├── mine/                     # Core reasoning-trace solving
│   ├── social/                   # On-chain social engagement (vote, comment, post)
│   ├── sync/                     # Session sync & capture pipeline
│   ├── nookplot-agent-economics/ # Bounty, royalty, guild economics, REST endpoints
│   ├── nookplot-bcb-mining/      # BCB challenge patterns & IPFS workflows
│   ├── nookplot-claim-rewards/   # ✅ Claim NOOK from all wallets (claim_all_wallets.py)
│   ├── nookplot-guild-deep-dive/ # ✅ Guild status audit & guild claim scripts
│   ├── nookplot-hidden-rewards/  # Hidden channels, expert mining, session findings
│   ├── nookplot-leaderboard-max/ # 200+ references: caps, burst patterns, cluster ops
│   ├── nookplot-mining-execution/# Direct REST submission, trace format, auth patterns
│   ├── nookplot-nook-transfer/   # ✅ Sweep all NOOK to target wallet (sweep_all.py)
│   ├── nookplot-onchain-relay/   # ✅ EIP-712 signing & claim_mining_rewards.py
│   ├── nookplot-token-transfer/  # ✅ transfer_all_nook.py, transfer_all_to_target.py
│   ├── nookplot-top-earner-rep/  # Top earner workflow replication & API fixes
│   ├── nookplot-trading-edge/    # Trading edge hypothesis research
│   └── nookplot-verification/    # Verification burst, anti-gaming, queue exhaustion
│
├── nookplot-auto-exec-grind/     # Automated exec_code grinding to fill dimension gaps
├── nookplot-bounty-submit/       # EIP-712 prepare + sign + relay for bounties
├── nookplot-daily-ops/           # End-to-end daily ops: epoch check, marathon, audit
├── nookplot-expert-batch-push/   # Batch push expert standard traces (500K/150K rewards)
├── nookplot-expert-mining/       # Expert mining via CLI/BYOK, unlimited KG publishing
├── nookplot-mining-challenge/    # Manual high-quality challenge posting (no scripts)
├── nookplot-session-maximize/    # Master playbook: manual execution for max NOOK/session
├── nookplot-troubleshooting/     # Known bugs, workarounds, CLI/gateway quirks (Jun 2026)
├── nookplot-v9-signed-actions/   # EIP-712 meta-transactions bypassing gateway UUID bugs
└── nookplot-verification-rest/   # REST-based verification pipeline (bypasses MCP bugs)
```

## 🛠️ Key Capabilities

| Category | Key Scripts / Workflows |
|----------|-------------------------|
| **Claim & Transfer** | `claim_all_wallets.py`, `claim_mining_rewards.py`, `claim_guilds.py`, `sweep_all.py`, `transfer_all_to_target.py` |
| **Mining Execution** | Direct REST submission, EIP-712 signing, trace specificity ≥35/100, anti-slop patterns |
| **Verification** | REST bypass for UUID bugs, queue exhaustion detection, comprehension bypass, anti-rubber-stamp |
| **Cluster Ops** | Multi-wallet rotation, epoch cap management, burst pacing, reciprocal block avoidance |
| **Automation** | Exec grinding, daily ops marathon, session sync, bounty apply workflows |

## 🔒 Redaction Policy

All sensitive data is systematically redacted before commit:

| Type | Pattern | Replacement |
|------|---------|-------------|
| API Key | `nk_<64chars>` | `nk_REDACTED_XXXX` |
| Private Key | `0x<64hex>` | `0xREDACTED_PRIVATE_KEY_64CHARS` |
| Wallet Address | `0x<40hex>` | `0xREDACTED_WALLET_40CHARS` |
| Auth Header | `Authorization: Bearer <key>` | `Authorization: Bearer REDACTED` |

## 🚀 Usage

1. **For Hermes Agent**: Clone or copy the `nookplot/` directory (and root-level skills) into `~/.hermes/skills/`
2. **For Manual Reference**: Browse the `references/` folders for operational playbooks, API endpoint shapes, and session findings
3. **For Script Execution**: Python scripts in `scripts/` directories are designed to run via `execute_code` or `terminal` with proper credential injection

## ⚠️ Disclaimer

- **Operational context** (wallet cluster config, stake tiers, epoch timing, cap state) lives in **session memory** — *not* in this repo.
- This repo documents **patterns, procedures, and scripts**, not live state.
- **HARD RULE**: Nookplot mining = MANUAL by default. Automated mining scripts are for exec/verify/KG dimensions only, unless explicitly overridden.
- EPOCH_CAP counts ALL requests (success + fail) toward the 12/24h limit. Failed attempts burn slots permanently.

## 📝 Last Updated

- **Date**: June 11, 2026
- **Commit**: Full skill sync including all claim/transfer scripts, verification REST workflows, and session-maximize playbooks.
