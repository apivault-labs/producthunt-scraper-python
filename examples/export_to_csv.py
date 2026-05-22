"""
Export ProductHunt products to CSV.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/export_to_csv.py > products.csv
"""

import csv
import sys

from producthunt_scraper import ProductHuntScraperClient


PRODUCTS = [
    "https://www.producthunt.com/posts/chatgpt",
    "https://www.producthunt.com/posts/notion",
    "https://www.producthunt.com/posts/midjourney",
]

COLUMNS = [
    "productName", "tagline", "website", "upvotes", "commentsCount",
    "reviewsCount", "rating", "followers", "topicsStr", "makersStr",
    "pricing", "pricingTier", "isFeatured", "launchDate",
    "dailyRank", "weeklyRank", "popularityScore", "maturityTier",
    "daysSinceLaunch", "isNewProduct", "upvoteVelocity", "engagementRate",
    "techStackSignals", "sentimentScore", "hasSocialProof",
    "badges", "dataSource", "productUrl",
]


def flatten(rec: dict) -> dict:
    out = {}
    for col in COLUMNS:
        v = rec.get(col)
        if isinstance(v, list):
            v = "; ".join(str(x) for x in v)
        elif isinstance(v, dict):
            v = str(v)
        out[col] = v if v is not None else ""
    return out


def main() -> None:
    client = ProductHuntScraperClient()
    results = client.analyze(PRODUCTS)

    writer = csv.DictWriter(sys.stdout, fieldnames=COLUMNS)
    writer.writeheader()
    for r in results:
        if r.get("success") and r.get("dataType") != "competitor_analysis":
            writer.writerow(flatten(r))


if __name__ == "__main__":
    main()
