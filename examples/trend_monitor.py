"""
Trend monitor: detect fast-growing new products.

Run daily (cron/GitHub Actions) to catch products gaining traction early.
Saves a snapshot and diffs against previous run.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    export PH_CLIENT_ID=your_ph_client_id
    export PH_CLIENT_SECRET=your_ph_client_secret
    python examples/trend_monitor.py
"""

import json
from pathlib import Path

from producthunt_scraper import ProductHuntScraperClient


SNAPSHOT_FILE = Path("trend_snapshot.json")
MIN_VELOCITY = 10.0   # upvotes/day threshold for "trending"
MIN_UPVOTES = 50      # minimum upvotes to consider


def main() -> None:
    client = ProductHuntScraperClient()

    print("Fetching today's leaderboard...")
    products = client.leaderboard(limit=100)
    products = [p for p in products if p.get("success")]

    # Load previous snapshot
    prev = {}
    if SNAPSHOT_FILE.exists():
        prev_list = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
        prev = {p["slug"]: p for p in prev_list if p.get("slug")}

    # Find trending products
    trending = [
        p for p in products
        if (p.get("upvoteVelocity") or 0) >= MIN_VELOCITY
        and (p.get("upvotes") or 0) >= MIN_UPVOTES
    ]
    trending.sort(key=lambda p: p.get("upvoteVelocity") or 0, reverse=True)

    print(f"\n🔥 Trending products (velocity ≥ {MIN_VELOCITY}/day):\n")
    for p in trending[:10]:
        slug = p.get("slug", "")
        prev_p = prev.get(slug)
        upvote_delta = ""
        if prev_p:
            delta = (p.get("upvotes") or 0) - (prev_p.get("upvotes") or 0)
            if delta > 0:
                upvote_delta = f" (+{delta} since last check)"

        print(f"  {p.get('productName', '?'):<35} "
              f"{p.get('upvoteVelocity'):.1f}/day  "
              f"{p.get('upvotes'):,} upvotes{upvote_delta}")
        print(f"    {p.get('tagline', '')[:70]}")
        print(f"    Tech: {', '.join((p.get('techStackSignals') or [])[:3])}")
        print()

    # New products not in previous snapshot
    new_slugs = {p["slug"] for p in products if p.get("slug")} - set(prev.keys())
    if new_slugs:
        new_products = [p for p in products if p.get("slug") in new_slugs]
        print(f"\n🆕 New products since last check: {len(new_products)}")
        for p in sorted(new_products, key=lambda x: x.get("upvotes") or 0, reverse=True)[:5]:
            print(f"  - {p.get('productName')} ({p.get('upvotes')} upvotes)")

    # Save snapshot
    SNAPSHOT_FILE.write_text(json.dumps(products, indent=2), encoding="utf-8")
    print(f"\nSnapshot saved → {SNAPSHOT_FILE}")


if __name__ == "__main__":
    main()
