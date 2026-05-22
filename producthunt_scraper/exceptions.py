"""Exception classes for the ProductHunt Scraper SDK."""


class ProductHuntScraperError(Exception):
    """Base exception for all SDK errors."""


class AuthenticationError(ProductHuntScraperError):
    """Raised when the Apify API token is missing or invalid."""


class ActorRunError(ProductHuntScraperError):
    """Raised when the actor run fails on Apify infrastructure."""


class ActorTimeoutError(ProductHuntScraperError):
    """Raised when the actor run does not finish within the allowed timeout."""
