"""
Competitor analysis: side-by-side comparison of competing products.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/competitor_analysis.py
"""

from producthunt_scraper import ProductHuntScraperClient


COMPETITORS = [
    "https://www.producthunt.com/posts/chatgpt",
    "https://www.producthunt.com/posts/claude-ai",
    "https://www.producthunt.com/posts/gemini-by-google",
    "https://www.producthunt.com/posts/perplexity-ai",
]


def fmt(v) -> str:
    if v is None:
        return "—"
    return str(v)


def main() -> None:
    client = ProductHuntScraperClient()
    print(f"Analyzing {len(COMPETITORS)} competing products...")

    results = client.analyze(COMPETITORS, include_competitor_analysis=True)

    # Separate analysis record
    analysis = next((r for r in results if r.get("dataType") == "competitor_analysis"), None)
    products = [r for r in results if r.get("success")]

    col_w = 20
    rows = [
        ("Upvotes",          "upvotes"),
        ("Rating",           "rating"),
        ("Reviews",          "reviewsCount"),
        ("Popularity",       "popularityScore"),
        ("Velocity/day",     "upvoteVelocity"),
        ("Engagement rate",  "engagementRate"),
        ("Maturity",         "maturityTier"),
        ("Pricing",          "pricingTier"),
        ("Has social proof", "hasSocialProof"),
        ("Days since launch","daysSinceLaunch"),
        ("Featured",         "isFeatured"),
    ]

    print()
    header = f"{'Metric':<22} | " + " | ".join(
        f"{(p.get('productName') or '?')[:col_w]:<{col_w}}" for p in products
    )
    print(header)
    print("-" * len(header))
    for label, key in rows:
        line = f"{label:<22} | " + " | ".join(
            f"{fmt(p.get(key))[:col_w]:<{col_w}}" for p in products
        )
        print(line)

    if analysis:
        print(f"\n=== Summary ===")
        print(f"  Avg upvotes:     {analysis.get('avgUpvotes')}")
        print(f"  Avg rating:      {analysis.get('avgRating')}")
        print(f"  Avg velocity:    {analysis.get('avgUpvoteVelocity')}/day")
        print(f"  Common tech:     {[t[0] for t in (analysis.get('commonTechStack') or [])[:5]]}")
        fastest = analysis.get("fastestGrowing") or []
        if fastest:
            print(f"  Fastest growing: {fastest[0].get('name')} "
                  f"({fastest[0].get('upvoteVelocity')}/day)")


if __name__ == "__main__":
    main()
