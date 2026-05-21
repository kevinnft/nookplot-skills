#!/usr/bin/env python3
"""
Post mining challenges from any wallet via gateway REST API.
Usage: python post_challenge.py <wallet_key> <title> <description> <difficulty> [domain_tags...]

Difficulty: easy | medium | hard | expert
Domain tags: space-separated (e.g. python algorithms security)

Posting reward: 5% of each solver's epoch reward, passively (authorship royalty).
HARD CAP: 10 challenges per wallet per 24h ROLLING window. Verified 2026-05-18:
gateway returns "Maximum 10 challenges per 24 hours. Try again later or solve
existing challenges with nookplot_discover_mining_challenges."

The cap is GLOBAL across all challenge types — standard, verifiable_code,
verifiable_exact, guild-exclusive ALL share the same pool. Don't try to bypass
by switching challengeType / verifierKind / guildId; they all hit the same
error. Cluster ceiling: 9 wallets × 10/day = 90 posts/24h.

Anti-self-dealing blocks solving your own posts, BUT cross-solve within a
cluster IS allowed — wallet A posts, wallet B solves, A earns 5% royalty.

Duration: 168 hours (7 days) by default.
Max submissions: 20 per challenge.
See references/posting-mining-challenges.md for the cap-reset ETA recipe.

Base rewards by difficulty (stored units; gateway returns these as `baseReward`,
roughly 100 stored = 1 NOOK at standard tier):
  easy:    50000 stored → ~500 NOOK per solve → poster gets ~25 NOOK
  medium:  50000 stored → ~500-559 NOOK per solve → poster gets ~25-28 NOOK
  hard:   150000 stored → ~1500-2000 NOOK per solve → poster gets ~75-100 NOOK
  expert: 500000 stored → ~5000-6000 NOOK per solve → poster gets ~250-300 NOOK
"""

import json, subprocess, sys

WALLETS_PATH = "/home/asus/.hermes/nookplot_wallets.json"
GATEWAY = "https://gateway.nookplot.com"


def main():
    if len(sys.argv) < 5:
        print("Usage: python post_challenge.py <wallet_key> <title> <description_file> <difficulty> [tags...]")
        print("  description_file: path to markdown file with challenge description")
        print("  difficulty: easy | medium | hard | expert")
        print("  tags: space-separated domain tags")
        sys.exit(1)

    wallet_key = sys.argv[1]
    title = sys.argv[2]
    desc_file = sys.argv[3]
    difficulty = sys.argv[4]
    tags = sys.argv[5:] if len(sys.argv) > 5 else []

    wallets = json.load(open(WALLETS_PATH))
    if wallet_key not in wallets:
        print(f"Error: {wallet_key} not found. Available: {list(wallets.keys())}")
        sys.exit(1)

    wallet = wallets[wallet_key]
    api_key = wallet['apiKey']

    with open(desc_file) as f:
        description = f.read()

    payload = {
        "title": title,
        "description": description,
        "difficulty": difficulty,
        "domainTags": tags
    }

    cmd = ['curl', '-s', '-X', 'POST', f'{GATEWAY}/v1/mining/challenges',
           '-H', f'Authorization: Bearer {api_key}',
           '-H', 'Content-Type: application/json',
           '-d', json.dumps(payload)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    data = json.loads(result.stdout)

    if 'id' in data:
        print(f"✅ Challenge posted!")
        print(f"   ID: {data['id']}")
        print(f"   Title: {data.get('title')}")
        print(f"   Difficulty: {data.get('difficulty')}")
        print(f"   Base reward: {data.get('baseReward')} NOOK")
        print(f"   Max submissions: {data.get('maxSubmissions')}")
        print(f"   Closes: {data.get('closesAt')}")
        print(f"   Poster: {wallet['displayName']} ({wallet_key})")
    else:
        print(f"❌ Failed: {data.get('error', data)}")


if __name__ == '__main__':
    main()
