"""
ProductHunt Scraper — Python SDK

Official Python client for the apivault_labs/producthunt-scraper Apify actor.
Scrape ProductHunt products, daily leaderboard, maker portfolios, topic rankings
and keyword search — with upvote velocity, tech stack detection, sentiment score
and competitor analysis.

Quick start:

    from producthunt_scraper import ProductHuntScraperClient

    client = ProductHuntScraperClient(api_token="apify_api_xxxxxx")
    rec = client.analyze_one("https://www.producthunt.com/posts/chatgpt")

    print(rec["upvotes"], rec["maturityTier"], rec["techStackSignals"])

See https://github.com/apivault-labs/producthunt-scraper-python for full docs.
"""

from .client import ProductHuntScraperClient
from .exceptions import (
    ProductHuntScraperError,
    AuthenticationError,
    ActorRunError,
    ActorTimeoutError,
)

__version__ = "0.1.0"
__all__ = [
    "ProductHuntScraperClient",
    "ProductHuntScraperError",
    "AuthenticationError",
    "ActorRunError",
    "ActorTimeoutError",
]
