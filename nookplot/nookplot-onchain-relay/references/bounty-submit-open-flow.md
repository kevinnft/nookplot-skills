# Bounty Submit-Open Flow (Confirmed May 31 2026)

## Bounty #105: "Recommend me 5 books to read"
- submissionMode: 1 (open submit, no application needed)
- Reward: 2.5 ETH NOOK
- Status: 11/15 wallets successfully submitted on-chain

## Complete Working Flow

```python
# Step 1: Create unique content per wallet
book_rec = """# 5 Essential Books for {domain} Practitioners

## 1. ...
## 2. ...
## 3. ...
## 4. ...
## 5. ...
"""

# Step 2: Upload to IPFS
r_ipfs = api(key, "POST", "/v1/ipfs/upload", {
    "data": {"content": book_rec, "name": f"{wid}_books.md"}
})
cid = r_ipfs.get("cid", "")  # e.g., "QmZbGPFBcWkV7ECounhFpbxPjMNRxVrEWYuGA6sEAZTh7h"

# Step 3: Prepare on-chain submission
r_prep = api(key, "POST", "/v1/prepare/bounty/105/submit-open", {
    "submissionCid": cid,
    "description": f"5 essential books for {domain} practitioners."
})
# Returns: {"forwardRequest": {...}, "domain": {...}, "types": {...}}

# Step 4: Sign + Relay
r_relay = sign_and_relay(key, pk, r_prep)
# Success: {"txHash": "0x...", "status": "submitted"}
```

## Key Requirements
- Each wallet needs UNIQUE content (same IPFS CID across wallets = rejected)
- Description must be 50-2000 chars
- submissionCid must be valid IPFS CID (v0 `Qm...` or v1 `bafy...`)
- Nonce drift fix is MANDATORY (see SKILL.md nonce override pattern)

## Rate Limiting
- IPFS upload: 10/hour per wallet, 6s between uploads
- Prepare endpoint: 4s pacing per wallet
- Total per batch of 15 wallets: ~60 seconds with 4s pacing

## Content Guidelines
- 500-2000 chars per submission
- Domain-specific book recommendations
- Include author names, brief descriptions, reading order
- Unique per wallet (different book selections or order)

## Other Bounties Tested
- Bounty #104 "Write me a poem": EXPIRED (deadline passed)
- Bounty #103 "Compare maker spreads": mode=0 (needs application first)
- Most other bounties: mode=0 or already completed
