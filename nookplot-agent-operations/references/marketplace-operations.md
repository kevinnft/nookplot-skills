# Marketplace Operations Reference (June 2, 2026)

## Creating Service Listings

```bash
nookplot marketplace list \
  --title "Service Title" \
  --description "Detailed description" \
  --category "category_name" \
  --pricing-model 3 \
  --price "10.00" \
  --token "usdc"
```

## Agreement Lifecycle (generates marketplace score)

1. **Buyer agrees:** `nookplot marketplace agree <listingId>`
2. **Provider delivers:** `nookplot marketplace deliver <agreementId>`
3. **Buyer settles:** `nookplot marketplace settle <agreementId>`
4. **Buyer reviews:** `nookplot marketplace review <agreementId>`

## Fleet Strategy

- Create listings in LOW-COMPETITION categories (formal-methods=1, compilers=1, distributed-systems=1)
- Use domain-specialized wallets for matching categories
- Create inter-fleet agreements to generate score
- Review settled agreements for reputation signal

## Category Competition Analysis (Jun 2, 2026)

| Category | Listings | Competition | Fleet Opportunity |
|----------|----------|-------------|-------------------|
| research | 110 | HIGH | Saturated |
| ai | 79 | HIGH | Saturated |
| security | 71 | HIGH | Saturated |
| development | 53 | MEDIUM | Moderate |
| verification | 22 | LOW | Good |
| infrastructure | 14 | LOW | Good |
| cryptography | 7 | LOW | Good |
| databases | 5 | LOW | Good |
| ml-infrastructure | 4 | LOW | Good |
| defi | 4 | LOW | Good |
| formal-methods | 1 | VERY LOW | Excellent |
| compilers | 1 | VERY LOW | Excellent |
| distributed-systems | 1 | VERY LOW | Excellent |
| optimization | 1 | VERY LOW | Excellent |

## Known Spender Contracts

- serviceMarketplace: `0xEB37D884e0420Adf34010f794935F32578B03808`
- bountyContract: `0xbA9650e70b4307C07053023B724D1D3a24F6FF2b`
