"""
Maker portfolio: all products by a specific ProductHunt maker.

Useful for:
- Researching a founder's track record
- Finding serial makers in your niche
- Due diligence on potential partners

Requires ProductHunt API credentials.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    export PH_CLIENT_ID=your_ph_client_id
    export PH_CLIENT_SECRET=your_ph_client_secret
    python examples/maker_portfolio.py
"""

from producthunt_scraper import ProductHuntScraperClient


MAKER_USERNAME = "rrhoover"  # Ryan Hoover, PH founder


def main() -> None:
    client = ProductHuntScraperClient()

    print(f"Fetching portfolio for @{MAKER_USERNAME}...")
    products = client.maker_products(MAKER_USERNAME, limit=100)
    products = [p for p in products if p.get("success")]

    if not products:
        print("No products found.")
        return

    # Sort by upvotes
    products.sort(key=lambda p: p.get("upvotes") or 0, reverse=True)

    # Maker info from first product
    maker_info = products[0].get("makerProfile") or {}
    print(f"\n=== @{MAKER_USERNAME} — {maker_info.get('name', '')} ===")
    print(f"  Headline: {maker_info.get('headline', '')}")
    print(f"  Total products: {len(products)}")

    total_upvotes = sum(p.get("upvotes") or 0 for p in products)
    avg_upvotes = total_upvotes // len(products) if products else 0
    viral = sum(1 for p in products if p.get("maturityTier") == "viral")
    featured = sum(1 for p in products if p.get("isFeatured"))

    print(f"  Total upvotes:  {total_upvotes:,}")
    print(f"  Avg upvotes:    {avg_upvotes:,}")
    print(f"  Viral products: {viral}")
    print(f"  Featured:       {featured}")

    print(f"\n  Top 10 products:")
    for i, p in enumerate(products[:10], 1):
        badges = " 🏆" if p.get("badges") else ""
        print(f"  {i:>2}. {p.get('productName', '?'):<35} "
              f"{p.get('upvotes') or 0:>6,} upvotes{badges}")


if __name__ == "__main__":
    main()
