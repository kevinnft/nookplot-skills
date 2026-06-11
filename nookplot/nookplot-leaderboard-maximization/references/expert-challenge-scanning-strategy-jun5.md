# External Expert Challenge Scanning Strategy (Jun 5 2026)

## CRITICAL PITFALL
The first page (offset=0, limit=50) of `GET /v1/mining/challenges?difficulty=expert&status=open` returns **100% our cluster challenges** (posted by W15/0x8863b1f755a3c66c8820aafbc25cb713171eaaeb).

Attempting to mine these returns "Cannot solve your own challenge" and **wastes EPOCH_CAP slots**.

## Correct Scanning Pattern
1. **SKIP page 1** (offset=0) — it contains only self-dealing challenges
2. **Scan pages 2-4** (offset=50, 100, 150) for external expert challenges
3. Filter out any challenge where `posterAddress` starts with our wallet prefixes
4. Prioritize challenges with 0-3 submissions (first-mover advantage)

## External Standard Challenges
Standard hard challenges (`challengeType: "standard"`) follow the same pattern — first page is cluster-dominated, external ones appear at higher offsets.

## Our Wallet Prefixes (for filtering)
```
0x5fcf1ae1 (W1/hermes)
0x5b82be85 (W2/9dragon)
0xdf5bc41e (W3/kevinft)
0xdbafe90b (W4/aboylabs)
0xd01767c9 (W5/reborn)
0xde44c354 (W6/satoshi)
0xa987be54 (W7/badboys)
0xfb671453 (W8/rebirth)
0x8b0b4d69 (W9/john)
0x5a1876a5 (W10/joni)
0xcddb0f53 (W11/WhiteAgent)
0xc339a172 (W12/PanuMan)
0x073e127e (W13/hemi)
0x13490d89 (W14/kicau)
0x8863b1f7 (W15/lucky)
```

## Confirmed External Challenge Topics (Jun 5)
Quantum Communication, Quantum Advantage, Quantum ML, Grover Algorithm, Shor Algorithm, and more on pages 2-4. ~30 external expert challenges total across pages 2-4.

## Impact
Wasting EPOCH_CAP slots on own challenges is the #1 cause of "0 external expert mined" sessions. Always scan offset 50+ first.
