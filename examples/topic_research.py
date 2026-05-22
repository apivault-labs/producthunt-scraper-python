"""
Topic research: top products in a category with tech stack analysis.

Useful for:
- Understanding what tools dominate a niche
- Finding gaps in the market
- Competitive landscape mapping

Requires ProductHunt API credentials.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    export PH_CLIENT_ID=your_ph_client_id
    export PH_CLIENT_SECRET=your_ph_client_secret
    python examples/topic_research.py
"""

from collections import Counter

from producthunt_scraper import ProductHuntScraperClient


TOPIC = "artificial-intelligence"  # Try: developer-tools, productivity, design-tools


def main() -> None:
    client = ProductHuntScraperClient()

    print(f"Fetching top 50 products in topic: {TOPIC}")
    products = client.topic_products(
        TOPIC,
        limit=50,
        order="VOTES",
        include_competitor_analysis=True,
    )

    # Separate analysis record
    analysis = next((p for p in products if p.get("dataType") == "competitor_analysis"), None)
    products = [p for p in products if p.get("success")]

    print(f"\n=== Topic: {TOPIC} ({len(products)} products) ===\n")

    # Tech stack distribution
    tech_counter = Counter()
    for p in products:
        for t in (p.get("techStackSignals") or []):
            tech_counter[t] += 1

    print("Tech stack distribution:")
    for tech, count in tech_counter.most_common(10):
        pct = count / len(products) * 100
        bar = "█" * int(pct / 5)
        print(f"  {tech:<25} {bar:<20} {count}/{len(products)} ({pct:.0f}%)")

    # Pricing distribution
    pricing_counter = Counter(p.get("pricingTier", "unknown") for p in products)
    print(f"\nPricing distribution:")
    for tier, count in pricing_counter.most_common():
        print(f"  {tier:<15} {count}")

    # Top 5 by upvotes
    top5 = sorted(products, key=lambda p: p.get("upvotes") or 0, reverse=True)[:5]
    print(f"\nTop 5 by upvotes:")
    for i, p in enumerate(top5, 1):
        print(f"  {i}. {p.get('productName', '?'):<35} "
              f"{p.get('upvotes') or 0:>6,} upvotes  "
              f"score={p.get('popularityScore')}")

    if analysis:
        print(f"\nCompetitor analysis summary:")
        print(f"  Avg upvotes:     {analysis.get('avgUpvotes')}")
        print(f"  Avg rating:      {analysis.get('avgRating')}")
        print(f"  New products:    {analysis.get('newProducts')}")
        print(f"  Featured:        {analysis.get('featuredProducts')}")


if __name__ == "__main__":
    main()
