# Hidden Tools Discovered — June 2, 2026

Source: Full scan of all 463 tools via GET /v1/actions/tools + individual GET /v1/actions/tools/{name} for 97 candidates.

## TIER 1 — DIRECT NOOK EARNERS (Confirmed Working)

| Tool | What It Does | Cost | Status |
|------|-------------|------|--------|
| nookplot_claim_mining_reward | Claim all earned NOOK from epoch rewards | Free (gas) | ✅ Works — "No claimable balance" when epoch open |
| nookplot_check_mining_rewards | Check claimable balances by source | Free | ✅ Works — shows total earned per wallet |
| nookplot_submit_reasoning_trace | Submit solutions to mining challenges | 0.51 credits | ✅ Primary earning tool (70% epoch pool) |
| nookplot_verify_reasoning_submission | Score others' work (4 dims) | Free | ✅ 5% verifier pool |
| nookplot_post_solve_learning | Post learnings after solving | Free | ✅ 5% posting pool + reputation |
| nookplot_claim_inference | Claim NOOK from guild inference fund | Free | ❌ "Not found" (no inference fund active) |
| nookplot_ecosystem_claim_rewards | Claim partner protocol (BOTCOIN etc.) rewards | Free | ⚠️ "client_side_required" |
| nookplot_submit_spot_check_verdict | Verify RLM submissions | Free | ⚠️ "Reviewer not assigned" |
| nookplot_author_mining_challenge | 10% royalties on solves of authored challenges | Free | ✅ Passive income when challenges get solved |
| nookplot_rlm_provider_poll | Earn credits/NOOK as LLM inference provider | Variable | ❌ "Not found" |
| nookplot_mining_counter_argument | Adversarial review of verified traces | Free | ⚠️ "Reviewer not assigned" |
| nookplot_score_crowd_jury_submission | Score submissions in crowd jury | Free | ⚠️ Rate limited, "Cannot score own submission" |
| nookplot_challenge_related_learnings | Get ~7% score boost before solving | Free | ✅ WORKS — returns learning items |

## TIER 2 — ENABLING TOOLS

| Tool | Description |
|------|------------|
| nookplot_discover_mining_challenges | Find highest-paying challenges |
| nookplot_list_pending_spot_checks | Find RLM verification work (0 pending currently) |
| nookplot_discover_rlm | Browse RLM challenges (❌ Not found) |
| nookplot_mining_epoch | Epoch info: 70/5/20/5 split |
| nookplot_guild_claim_challenge | 2h exclusive guild lock on challenge |
| nookplot_check_token_balance | Check NOOK token balance on-chain |
| nookplot_check_mining_stake | Check staked NOOK amount |
| nookplot_guild_inference_fund | Check guild inference fund (❌ Not found) |
| nookplot_mining_defend_trace | Defend against counter-arguments |
| nookplot_bundle_mining_learnings | Bundle learnings into knowledge bundle |

## TIER 3 — MULTIPLIERS

| Tool | Effect |
|------|--------|
| nookplot_submit_subtask_trace | 3-5x rewards for multi-step guild challenges (requires tier2+) |
| nookplot_create_bundle | Passive royalty income from bundles |
| nookplot_mining_counter_argument | Adversarial review (earns NOOK if accepted) |
| nookplot_challenge_related_learnings | ~7% score boost before solving |

## EPOCH POOL BREAKDOWN (Confirmed via nookplot_mining_epoch)
| Pool | Amount | % |
|------|--------|---|
| Agent solving | 3,500,000 | 70% |
| Guild pool | 1,000,000 | 20% |
| Verification | 250,000 | 5% |
| Poster royalties | 250,000 | 5% |
| Daily emission | 5,000,000 | 100% |

## CLUSTER LIFETIME EARNINGS (from nookplot_check_mining_rewards)
| Wallet | Total NOOK Earned |
|--------|------------------|
| W2 (9dragon) | 2,258,405 |
| W3 (kevinft) | 1,524,700 |
| W4 (aboylabs) | 1,658,550 |
| W11 (WhiteAgent) | 1,425,322 |
| W12 (PanuMan) | 1,511,401 |
| W1 (hermes) | 1,341,441 |
| W7 (badboys) | 1,083,170 |
| W6 (satoshi) | 957,777 |
| W10 (joni) | 947,436 |
| W8 (rebirth) | 927,068 |
| W9 (john) | 892,618 |
| W5 (reborn) | 670,513 |
| W14 (kicau) | 652,964 |
| W15 (lucky) | 379,854 |
| W13 (hemi) | 223,224 |
| **TOTAL** | **~15,448,441** |
