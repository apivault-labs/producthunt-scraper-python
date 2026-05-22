"""
Quickstart: analyze one ProductHunt product and print all signals.

    pip install -r requirements.txt
    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/quickstart.py
"""

from producthunt_scraper import ProductHuntScraperClient


def main() -> None:
    client = ProductHuntScraperClient()

    url = "https://www.producthunt.com/posts/midjourney"
    rec = client.analyze_one(url)

    print(f"\n=== {rec['productName']} ===")
    print(f"  Tagline:          {rec.get('tagline')}")
    print(f"  Website:          {rec.get('website')}")
    print(f"  Upvotes:          {rec.get('upvotes')}")
    print(f"  Comments:         {rec.get('commentsCount')}")
    print(f"  Reviews:          {rec.get('reviewsCount')}")
    print(f"  Rating:           {rec.get('rating')}")
    print(f"  Pricing:          {rec.get('pricing')} ({rec.get('pricingTier')})")
    print(f"  Topics:           {rec.get('topicsStr')}")
    print(f"  Makers:           {rec.get('makersStr')}")
    print(f"  Hunter:           @{rec.get('hunter', {}).get('username')}")
    print(f"  Badges:           {rec.get('badges')}")
    print(f"  Launch date:      {rec.get('launchDate')}")
    print(f"  Daily rank:       #{rec.get('dailyRank')}")
    print()
    print(f"  Popularity score: {rec.get('popularityScore')}/100")
    print(f"  Maturity tier:    {rec.get('maturityTier')}")
    print(f"  Days since launch:{rec.get('daysSinceLaunch')}")
    print(f"  Is new product:   {rec.get('isNewProduct')}")
    print(f"  Upvote velocity:  {rec.get('upvoteVelocity')}/day")
    print(f"  Engagement rate:  {rec.get('engagementRate')}")
    print(f"  Tech stack:       {rec.get('techStackSignals')}")
    print(f"  Sentiment:        {rec.get('sentimentScore')}")
    print(f"  Has social proof: {rec.get('hasSocialProof')}")
    print(f"  Data source:      {rec.get('dataSource')}")


if __name__ == "__main__":
    main()
