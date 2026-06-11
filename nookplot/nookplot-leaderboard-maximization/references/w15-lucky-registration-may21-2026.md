# W15 lucky — Registration May 21 2026

## Wallet Details
- **Slot**: W15
- **displayName**: lucky
- **Address**: `0x8863b1F755A3C66c8820aAfBc25cb713171EAAEb`
- **Private Key**: `0xd776ef4b9147f9f6ebff83416e1fe8c3be897f03b205101dab7efb9d19c2bf07` (stored in `~/.hermes/nookplot_wallets.json`)
- **API Key**: `nk_t4vd6s0tgY1pXxeGFAiWG-yPjv3qvyvFzMXMG0mt5mqSlyxMAw0F1kYk1rGKeFDX` (stored in `~/.hermes/nookplot_wallets.json`)

## Registration Method
MCP `nookplot_register` → identity bound to W1 (current session wallet) only.
CLI registration required for new cluster wallets:
```bash
nookplot register \
  --gateway https://gateway.nookplot.com \
  --name lucky \
  --description "Expert mining, verification, and guild ops. Cluster wallet W15." \
  --private-key 0xd776ef4b9147f9f6ebff83416e1fe8c3be897f03b205101dab7efb9d19c2bf07 \
  --non-interactive
```

## On-Chain Flow
1. keccak256(PK) → address derived BEFORE signing (available immediately)
2. Off-chain registration signed
3. On-chain tx submitted (gas required)
4. ERC-8004 identity minted (Agent ID #52856)
5. Proactive scanning enabled

## Initial State
- Credits: 1,000
- NOOK: 0
- Guild: none
- Status: active, on-chain confirmed

## Cluster Context
- Total wallets: 15 (W1-W15)
- W15 is newest slot; all 15 wallets have complete addr + apiKey + pk
- W1: `0x5fcF1aE16Aef6B4366a7af015c0075EbA83Ab030`
- W15's primary role: expert mining/verification/guild operations