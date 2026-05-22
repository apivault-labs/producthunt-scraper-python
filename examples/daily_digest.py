"""
Daily digest: today's top 50 products ranked by upvote velocity.

Useful for:
- Morning briefing on what's trending
- Catching fast-growing products early
- Niche monitoring (filter by topic)

Requires ProductHunt API credentials.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    export PH_CLIENT_ID=your_ph_client_id
    export PH_CLIENT_SECRET=your_ph_client_secret
    python examples/daily_digest.py
"""

from producthunt_scraper import ProductHuntScraperClient


def main() -> None:
    client = ProductHuntScraperClient()

    print("Fetching today's top 50 products...")
    products = client.leaderboard(limit=50)
    products = [p for p in products if p.get("success")]

    # Sort by upvote velocity (fastest growing)
    by_velocity = sorted(
        products,
        key=lambda p: p.get("upvoteVelocity") or 0,
        reverse=True,
    )

    print(f"\n=== Today's Top Products by Velocity ({len(products)} total) ===\n")
    print(f"{'#':<4} {'Name':<35} {'Upvotes':>8} {'Velocity':>10} {'Tech Stack'}")
    print("-" * 90)

    for i, p in enumerate(by_velocity[:20], 1):
        name = (p.get("productName") or "?")[:33]
        upvotes = p.get("upvotes") or 0
        velocity = p.get("upvoteVelocity") or 0
        tech = ", ".join((p.get("techStackSignals") or [])[:3])
        print(f"{i:<4} {name:<35} {upvotes:>8,} {velocity:>10.1f}/day  {tech}")

    # New products (launched today)
    new_today = [p for p in products if p.get("isNewProduct")]
    if new_today:
        print(f"\n🆕 New products today: {len(new_today)}")
        for p in new_today[:5]:
            print(f"  - {p.get('productName')} ({p.get('upvotes')} upvotes)")


if __name__ == "__main__":
    main()
