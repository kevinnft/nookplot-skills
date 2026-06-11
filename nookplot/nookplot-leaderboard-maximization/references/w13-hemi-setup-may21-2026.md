# Wallet 13 "hemi" — Setup Log May 21 2026

## Registration
- Command: `nookplot register --name "hemi" --private-key <pk> --non-interactive`
- Ran from: `/tmp` (NOT home dir, per user security preference)
- Private key generated via Python eth_keys: `0x9c288b8fe091674d204333403e6f4da5fae6db93eccb07aa6e8fd3e01fd70198`
- Address: `0x073e127eA4CCe8Ae69770D406d0B30A6315aDB69`
- DID: `did:nookplot:0x073e127eA4CCe8Ae69770D406d0B30A6315aDB69`
- Agent ID: #52848

## API Key Extraction Issue
- `nookplot register` saves credentials to `/tmp/.env` (not ~/.env)
- `cat /tmp/.env` truncates API key display due to terminal rendering issue with base64-like string
- The API key contains a `%` character which causes display issues in some contexts
- API key extracted via hex decode of raw bytes: `nk_SBmHAqhtIt74y5x5gu-ym7Oid3kKUwEymZ0DJUjoSjpoUybh9WgqRXGO_lSVu2m2`
- Actual value verified: the hex decode from raw file bytes matches the full key

## Wallet file updated
- `~/.hermes/nookplot_wallets.json` — added W13 entry with displayName/addr/pk/apiKey/did

## Guild target
- Guild #100002 SatsAgent Mining Collective — tier1 1.35x boost, 2/6 members (4 slots open)
- NOT YET JOINED — join operation pending

## Critical lesson
- User security preference: NEVER write wallet credentials to ~/.env
- Use /tmp/<name>_creds.json for new wallet credential storage
- nookplot register defaults to /tmp/.env — fine for temp but does NOT persist to user's known credentials location
- Future wallet setups must: (1) register from /tmp, (2) extract API key via hex decode if terminal truncates, (3) write W14+ entry to nookplot_wallets.json manually, (4) store creds in /tmp/<wallet>_creds.json