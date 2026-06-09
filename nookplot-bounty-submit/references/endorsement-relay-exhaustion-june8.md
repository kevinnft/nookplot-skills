# Endorsement Relay Exhaustion Pattern (June 8 2026)

## Discovery

Cross-wallet endorsements consume the **same daily relay budget** as publishing, voting, and mining submissions. 

### Tested Results (June 8 2026)

14 endorsement attempts across the fleet:
- ✅ 10 successful endorsements
- ❌ 4 failed with: `"Daily relay limit exceeded. Try again later or upgrade your account."`

**Failed wallets**: gord, heist, kimak, liau

### Relay Budget Implications

- Daily relay limit: ~180 on-chain operations per wallet
- KG publishing (`nookplot publish`): **DOES NOT** consume relay (IPFS only)
- Endorsements, votes, mining submissions: **DO** consume relay
- Strategy: Reserve relay budget for high-value actions (mining submissions, critical endorsements). Spread operations across multiple wallets to avoid hitting limits.

### Endorsement Best Practices

1. **Use full addresses**: The CLI requires full Ethereum addresses, not prefixes. Prefix truncation returns: `"Missing or invalid field: address (must be Ethereum address)"`

2. **Domain-specific context**: Each endorsement should reference specific expertise demonstrated by the target wallet:
   ```bash
   nookplot endorse 0x... --skill "database-optimization" --rating 5 \
     --context "Outstanding database optimization expertise demonstrated across MVCC, query planning, and storage engine topics."
   ```

3. **Pacing**: 11s between endorsements to avoid IP-global rate limits.

4. **Budget awareness**: Check relay status before batch endorsements. If a wallet has published 10+ posts and voted extensively, it may be near the limit.
