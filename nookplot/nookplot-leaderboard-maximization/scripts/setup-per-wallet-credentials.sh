#!/usr/bin/env bash
# Setup per-wallet MCP credentials for multi-subagent parallel execution.
# Run ONCE after adding new wallet slots.
# Creates ~/.nookplot/agents/w{n}/credentials.json for each wallet in nookplot_wallets.json.
#
# Usage: bash setup-per-wallet-credentials.sh

set -euo pipefail

WALLETS_JSON="${WALLETS_JSON:-$HOME/.hermes/nookplot_wallets.json}"
NOOKPLOT_DIR="$HOME/.nookplot"
AGENTS_DIR="$NOOKPLOT_DIR/agents"

mkdir -p "$AGENTS_DIR"

# W1 uses global credentials.json (from MCP initial setup) — skip
jq -r 'to_entries[] | select(.key | test("^W[0-9]+$")) | select(.key != "W1") | "\(.key)=\(.value | @json)"' "$WALLETS_JSON" | while IFS='=' read -r slot json; do
    idx=$(echo "$slot" | tr '[:upper:]' '[:lower:]')
    addr=$(echo "$json" | jq -r '.addr')
    pk=$(echo "$json" | jq -r '.pk // empty')
    apiKey=$(echo "$json" | jq -r '.apiKey')

    out_dir="$AGENTS_DIR/$idx"
    mkdir -p "$out_dir"

    creds=$(jq -n \
        --arg addr "$addr" \
        --arg pk "$pk" \
        --arg apiKey "$apiKey" \
        '{address: $addr, privateKey: $pk, apiKey: $apiKey, gatewayUrl: "https://gateway.nookplot.com"}')

    echo "$creds" > "$out_dir/credentials.json"
    chmod 600 "$out_dir/credentials.json"
    echo "Created $out_dir/credentials.json for $slot"
done

echo "Done. To use: NOOKPLOT_PROFILE=w2 npx -y @nookplot/mcp@latest"
