"""
ProductHuntScraperClient — synchronous wrapper around the Apify
``apivault_labs/producthunt-scraper`` actor.

The actor handles all heavy work (Thunderbit scraping, PH API calls,
derived signal computation, competitor analysis) on Apify infrastructure.
This client forwards inputs, polls until the run finishes, then downloads
the dataset.

Usage:

    from producthunt_scraper import ProductHuntScraperClient

    client = ProductHuntScraperClient(
        api_token="apify_api_xxxxxx",
        ph_client_id="your_ph_client_id",       # optional
        ph_client_secret="your_ph_client_secret", # optional
    )

    # Specific products (no PH credentials needed)
    products = client.analyze(["https://www.producthunt.com/posts/chatgpt"])

    # Today's leaderboard (requires PH credentials)
    top50 = client.leaderboard(limit=50)

    # Maker portfolio (requires PH credentials)
    portfolio = client.maker_products("rrhoover")
"""

from __future__ import annotations

import os
import time
from typing import Any, Iterable

import requests

from .exceptions import (
    ActorRunError,
    ActorTimeoutError,
    AuthenticationError,
    ProductHuntScraperError,
)


ACTOR_ID = "apivault_labs~producthunt-scraper"
APIFY_API_BASE = "https://api.apify.com/v2"

TERMINAL_OK = {"SUCCEEDED"}
TERMINAL_FAIL = {"FAILED", "TIMED-OUT", "ABORTED"}

VALID_MODES = {"urls", "leaderboard", "search", "maker", "topic"}
VALID_TOPIC_ORDERS = {"VOTES", "NEWEST", "FEATURED"}


class ProductHuntScraperClient:
    """Synchronous client for the ProductHunt Scraper Apify actor.

    Parameters
    ----------
    api_token : str, optional
        Apify Personal API token. Falls back to ``APIFY_API_TOKEN`` env var.
    ph_client_id : str, optional
        ProductHunt API client_id. Unlocks leaderboard, search, maker, topic modes.
        Get free at https://www.producthunt.com/v2/oauth/applications
    ph_client_secret : str, optional
        ProductHunt API client_secret. Required together with ph_client_id.
    timeout : int, optional
        Maximum seconds to wait for an actor run. Default 600.
    poll_interval : float, optional
        Seconds between status polls. Default 3.
    """

    def __init__(
        self,
        api_token: str | None = None,
        ph_client_id: str | None = None,
        ph_client_secret: str | None = None,
        timeout: int = 600,
        poll_interval: float = 3.0,
        base_url: str = APIFY_API_BASE,
    ):
        token = api_token or os.environ.get("APIFY_API_TOKEN")
        if not token:
            raise AuthenticationError(
                "Apify API token is required. Pass api_token='apify_api_...' "
                "or set the APIFY_API_TOKEN environment variable. "
                "Get a token at https://console.apify.com/account/integrations"
            )
        self._token = token
        self._ph_client_id = ph_client_id or os.environ.get("PH_CLIENT_ID", "")
        self._ph_client_secret = ph_client_secret or os.environ.get("PH_CLIENT_SECRET", "")
        self._timeout = int(timeout)
        self._poll_interval = float(poll_interval)
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "User-Agent": "producthunt-scraper-python/0.1.0",
        })

    # ------------------------------------------------------------------ public

    def analyze(
        self,
        product_urls: Iterable[str],
        *,
        include_competitor_analysis: bool = False,
        max_concurrency: int = 3,
        actor_timeout_secs: int = 300,
    ) -> list[dict[str, Any]]:
        """Analyze specific ProductHunt product URLs.

        No PH API credentials needed — uses Thunderbit as fallback.

        Returns list of product records. If `include_competitor_analysis=True`,
        the last record will have `dataType='competitor_analysis'`.
        """
        urls = [u for u in product_urls if u]
        if not urls:
            raise ValueError("product_urls must contain at least one non-empty URL")

        payload = {
            "mode": "urls",
            "productUrls": list(urls),
            "maxConcurrency": int(max_concurrency),
            "includeCompetitorAnalysis": include_competitor_analysis,
            "phClientId": self._ph_client_id,
            "phClientSecret": self._ph_client_secret,
        }
        return self._run(payload, actor_timeout_secs=actor_timeout_secs)

    def analyze_one(self, product_url: str, **kwargs: Any) -> dict[str, Any]:
        """Analyze a single ProductHunt product URL. Returns one dict."""
        results = self.analyze([product_url], **kwargs)
        products = [r for r in results if r.get("dataType") != "competitor_analysis"]
        if not products:
            raise ActorRunError(
                f"Actor returned no records for {product_url!r} — "
                "the URL might not be a valid ProductHunt product page."
            )
        return products[0]

    def leaderboard(
        self,
        date: str | None = None,
        limit: int = 50,
        include_competitor_analysis: bool = False,
        actor_timeout_secs: int = 300,
    ) -> list[dict[str, Any]]:
        """Fetch top products for a date (default: today).

        Requires ProductHunt API credentials (ph_client_id + ph_client_secret).

        Parameters
        ----------
        date : str, optional
            Date in YYYY-MM-DD format. None = today.
        limit : int
            Max products to return (1-500). Default 50.
        """
        self._require_ph_credentials("leaderboard")
        payload = {
            "mode": "leaderboard",
            "date": date or "",
            "limit": int(limit),
            "includeCompetitorAnalysis": include_competitor_analysis,
            "phClientId": self._ph_client_id,
            "phClientSecret": self._ph_client_secret,
        }
        return self._run(payload, actor_timeout_secs=actor_timeout_secs)

    def search(
        self,
        query: str,
        limit: int = 20,
        include_competitor_analysis: bool = False,
        actor_timeout_secs: int = 300,
    ) -> list[dict[str, Any]]:
        """Search ProductHunt by keyword.

        Requires ProductHunt API credentials.
        """
        self._require_ph_credentials("search")
        if not query.strip():
            raise ValueError("query must not be empty")
        payload = {
            "mode": "search",
            "searchQuery": query.strip(),
            "limit": int(limit),
            "includeCompetitorAnalysis": include_competitor_analysis,
            "phClientId": self._ph_client_id,
            "phClientSecret": self._ph_client_secret,
        }
        return self._run(payload, actor_timeout_secs=actor_timeout_secs)

    def maker_products(
        self,
        username: str,
        limit: int = 50,
        actor_timeout_secs: int = 300,
    ) -> list[dict[str, Any]]:
        """Fetch all products made by a specific PH username.

        Requires ProductHunt API credentials.

        Parameters
        ----------
        username : str
            ProductHunt username (e.g. 'rrhoover' for Ryan Hoover).
        """
        self._require_ph_credentials("maker")
        if not username.strip():
            raise ValueError("username must not be empty")
        payload = {
            "mode": "maker",
            "makerUsername": username.strip(),
            "limit": int(limit),
            "phClientId": self._ph_client_id,
            "phClientSecret": self._ph_client_secret,
        }
        return self._run(payload, actor_timeout_secs=actor_timeout_secs)

    def topic_products(
        self,
        topic_slug: str,
        limit: int = 50,
        order: str = "VOTES",
        include_competitor_analysis: bool = False,
        actor_timeout_secs: int = 300,
    ) -> list[dict[str, Any]]:
        """Fetch top products in a ProductHunt topic/category.

        Requires ProductHunt API credentials.

        Parameters
        ----------
        topic_slug : str
            PH topic slug, e.g. 'artificial-intelligence', 'developer-tools',
            'productivity', 'design-tools', 'marketing', 'no-code'.
        order : str
            Sort order: 'VOTES' (default), 'NEWEST', or 'FEATURED'.
        """
        self._require_ph_credentials("topic")
        if not topic_slug.strip():
            raise ValueError("topic_slug must not be empty")
        order = order.upper()
        if order not in VALID_TOPIC_ORDERS:
            raise ValueError(f"order must be one of {VALID_TOPIC_ORDERS}")
        payload = {
            "mode": "topic",
            "topicSlug": topic_slug.strip(),
            "topicOrder": order,
            "limit": int(limit),
            "includeCompetitorAnalysis": include_competitor_analysis,
            "phClientId": self._ph_client_id,
            "phClientSecret": self._ph_client_secret,
        }
        return self._run(payload, actor_timeout_secs=actor_timeout_secs)

    def estimate_cost(self, product_count: int) -> float:
        """Return estimated USD cost for `product_count × $0.005`."""
        return round(product_count * 0.005, 4)

    # ------------------------------------------------------------------ private

    def _require_ph_credentials(self, mode: str) -> None:
        if not self._ph_client_id or not self._ph_client_secret:
            raise AuthenticationError(
                f"Mode '{mode}' requires ProductHunt API credentials. "
                "Pass ph_client_id and ph_client_secret to the client constructor. "
                "Get them free at https://www.producthunt.com/v2/oauth/applications"
            )

    def _run(self, payload: dict[str, Any], actor_timeout_secs: int) -> list[dict[str, Any]]:
        run_id = self._start_run(payload, actor_timeout_secs=actor_timeout_secs)
        run = self._wait_for_run(run_id)
        return self._fetch_dataset(run["defaultDatasetId"])

    def _start_run(self, payload: dict[str, Any], actor_timeout_secs: int) -> str:
        url = f"{self._base_url}/acts/{ACTOR_ID}/runs"
        params = {"timeout": int(actor_timeout_secs)}
        try:
            r = self._session.post(url, params=params, json=payload, timeout=30)
        except requests.RequestException as e:
            raise ProductHuntScraperError(f"Failed to start actor run: {e}") from e

        if r.status_code == 401:
            raise AuthenticationError(
                "Apify rejected the API token. Generate a new one at "
                "https://console.apify.com/account/integrations"
            )
        if r.status_code >= 400:
            raise ActorRunError(
                f"Apify returned HTTP {r.status_code} when starting run: {r.text[:300]}"
            )

        data = r.json().get("data") or {}
        run_id = data.get("id")
        if not run_id:
            raise ActorRunError(f"Apify response missing run id: {r.text[:300]}")
        return run_id

    def _wait_for_run(self, run_id: str) -> dict[str, Any]:
        url = f"{self._base_url}/actor-runs/{run_id}"
        deadline = time.time() + self._timeout
        while True:
            try:
                r = self._session.get(url, timeout=30)
            except requests.RequestException as e:
                raise ProductHuntScraperError(f"Failed to poll run status: {e}") from e

            if r.status_code >= 400:
                raise ActorRunError(
                    f"Apify returned HTTP {r.status_code} when polling run: {r.text[:300]}"
                )

            run = r.json().get("data") or {}
            status = run.get("status")
            if status in TERMINAL_OK:
                return run
            if status in TERMINAL_FAIL:
                raise ActorRunError(
                    f"Actor run {run_id} ended with status={status}: "
                    f"{run.get('statusMessage') or '(no message)'}"
                )

            if time.time() > deadline:
                raise ActorTimeoutError(
                    f"Actor run {run_id} did not finish within {self._timeout}s "
                    f"(last status={status}). Increase `timeout=` or fetch the dataset manually."
                )

            time.sleep(self._poll_interval)

    def _fetch_dataset(self, dataset_id: str) -> list[dict[str, Any]]:
        url = f"{self._base_url}/datasets/{dataset_id}/items"
        params = {"clean": "true", "format": "json"}
        try:
            r = self._session.get(url, params=params, timeout=120)
        except requests.RequestException as e:
            raise ProductHuntScraperError(f"Failed to download dataset: {e}") from e

        if r.status_code >= 400:
            raise ActorRunError(
                f"Apify returned HTTP {r.status_code} when fetching dataset: "
                f"{r.text[:300]}"
            )

        try:
            data = r.json()
        except ValueError as e:
            raise ActorRunError(f"Apify dataset is not valid JSON: {e}") from e

        if not isinstance(data, list):
            raise ActorRunError(
                f"Unexpected dataset payload (not a list): {type(data).__name__}"
            )
        return data
