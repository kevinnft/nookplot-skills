# Guild treasury claim execution attempt — May 23 2026

Use this when retrying `nookplot_claim_pending_guild_mining_treasury` after a prepare-only probe.

## What happened

A full sign + `/v1/relay` execution attempt was run for W1-W15 after the user explicitly said `gas semua`.

Observed outcomes:

- W1: skipped because the local wallet entry has no private key/API-key material for direct signing.
- W2, W3, W4, W5, W6, W8, W11, W13, W14, W15: prepare/sign succeeded after nonce resync, but relay reverted on-chain with `Contract reverted`, `errorName: FailedCall`.
- W7 and W10: relay blocked by `Daily relay limit exceeded` tier 1.
- W9: local private key material is malformed/short; even zero-left-padding produced a different address, so do not sign with it.
- W12: relay failed with `invalid BytesLike value`; likely malformed forwardRequest/signature/data shape from gateway or signer edge case. Retry separately with payload inspection before assuming payout.

No `txHash` was submitted for any wallet. Standard `check_mining_rewards` immediately after still showed all immediate claimable buckets at zero (`epoch_solving`, `epoch_verification`, `guild_inference_claim`).

## Interpretation

`status: sign_required` from prepare-only is only readiness, not proof of positive payout. The actual on-chain claim path can still revert via `FailedCall`, which is what happened for most wallets. Treat the guild-treasury hidden lane as currently blocked unless chain/contract state reveals a non-reverting wallet.

## Retry guidance

1. Do not retry W2/W3/W4/W5/W6/W8/W11/W13/W14/W15 blindly; repeated relay will likely burn daily relay quota and return the same inner revert.
2. For W7/W10, wait for daily relay reset before retrying, and preferably run read-only/callStatic first.
3. Fix W9 wallet credentials before any signing attempt; current private key does not match the recorded address.
4. Debug W12 separately by dumping the prepared forwardRequest fields and validating `data`/`signature` bytes before relay.
5. Best next technical step is read-only chain inspection of contract `0x4a727780aBef775c5846fFbaE16558778c71fe0f` selector `0x166b69a3`, or a callStatic simulation through the forwarder, before another relay wave.
