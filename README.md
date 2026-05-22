# ProductHunt Scraper — Python SDK

> **Scrape ProductHunt products, daily leaderboard, maker portfolios, topic rankings and keyword search — with upvote velocity, tech stack detection, sentiment score and competitor analysis.**

Python client for the [ProductHunt Scraper Apify Actor](https://apify.com/apivault_labs/producthunt-scraper) — get **40+ intelligence fields** for any ProductHunt product using public data.

[![Apify Actor](https://img.shields.io/badge/Apify-Actor-blue?logo=apify)](https://apify.com/apivault_labs/producthunt-scraper)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![PyPI-friendly](https://img.shields.io/badge/install-pip-success)](#installation)

---

## What it does

Five modes, one client:

```python
from producthunt_scraper import ProductHuntScraperClient

client = ProductHuntScraperClient(api_token="apify_api_xxxxxx")

# 1. Specific products
products = client.analyze(["https://www.producthunt.com/posts/chatgpt"])

# 2. Today's leaderboard (requires PH API key)
top50 = client.leaderboard(limit=50)

# 3. Keyword search (requires PH API key)
ai_tools = client.search("AI writing tool", limit=20)

# 4. All products by a maker (requires PH API key)
portfolio = client.maker_products("rrhoover", limit=100)

# 5. Top products in a topic (requires PH API key)
ai_products = client.topic_products("artificial-intelligence", limit=50)
```

**Pricing:** $0.005 per product. No subscriptions.

---

## Quick start

```python
from producthunt_scraper import ProductHuntScraperClient

client = ProductHuntScraperClient(api_token="apify_api_xxxxxx")
rec = client.analyze_one("https://www.producthunt.com/posts/midjourney")

print(f"Name:             {rec['productName']}")
print(f"Upvotes:          {rec['upvotes']}")
print(f"Upvote velocity:  {rec['upvoteVelocity']}/day")
print(f"Maturity:         {rec['maturityTier']}")
print(f"Tech stack:       {rec['techStackSignals']}")
print(f"Sentiment:        {rec['sentimentScore']}")
print(f"Popularity score: {rec['popularityScore']}/100")
```

Output:
```
Name:             Midjourney
Upvotes:          3500
Upvote velocity:  2.8/day
Maturity:         viral
Tech stack:       ['AI/ML', 'Design']
Sentiment:        0.5
Popularity score: 90/100
```

---

## Installation

```bash
pip install git+https://github.com/apivault-labs/producthunt-scraper-python.git
```

Or clone and use directly:

```bash
git clone https://github.com/apivault-labs/producthunt-scraper-python.git
cd producthunt-scraper-python
pip install -r requirements.txt
```

---

## Get your API token (free)

1. Sign up at [apify.com](https://apify.com) — free tier includes $5 monthly credits
2. Go to [Account → Integrations](https://console.apify.com/account/integrations)
3. Copy your Personal API token

```bash
export APIFY_API_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxxxxx
```

### Optional: ProductHunt API credentials (for leaderboard/search/maker/topic)

1. Go to [producthunt.com/v2/oauth/applications](https://www.producthunt.com/v2/oauth/applications)
2. Create a new application (free, instant)
3. Copy `client_id` and `client_secret`

```python
client = ProductHuntScraperClient(
    api_token="apify_api_xxx",
    ph_client_id="your_ph_client_id",
    ph_client_secret="your_ph_client_secret",
)
```

---

## What you get (40+ fields)

### Core fields
- `productName`, `tagline`, `description`, `website`
- `upvotes`, `commentsCount`, `reviewsCount`, `rating`, `followers`
- `topics[]`, `topicsStr`, `makers[]`, `makersStr`
- `hunter` — `{name, username}` who posted it
- `image`, `gallery[]` — thumbnail + screenshots
- `pricing`, `pricingType`
- `badges[]` — Product of the Day, Product of the Week, etc.
- `isFeatured`, `featuredAt`, `launchDate`, `createdAt`
- `dailyRank`, `weeklyRank`
- `productId`, `slug`

### 🧠 Derived intelligence (always computed)
| Field | Description | Example |
|---|---|---|
| `popularityScore` | 0-100 composite (upvotes × rating) | 90 |
| `daysSinceLaunch` | Age in days | 1247 |
| `isNewProduct` | Launched in last 30 days | false |
| `upvoteVelocity` | Upvotes per day since launch | 2.8 |
| `engagementRate` | (comments + reviews) / upvotes | 0.023 |
| `techStackSignals[]` | Detected tech from description | `["AI/ML", "Design"]` |
| `sentimentScore` | -1.0 to 1.0 from description | 0.5 |
| `maturityTier` | new/early/growing/popular/viral | "viral" |
| `hasSocialProof` | ≥5 reviews AND ≥4.0 rating | true |
| `pricingTier` | free/freemium/subscription/paid | "freemium" |

### 📊 Competitor analysis (optional)
Set `include_competitor_analysis=True` to get one extra summary record:
- `avgUpvotes`, `avgRating`, `avgPopularityScore`, `avgUpvoteVelocity`
- `topByUpvotes[]`, `topByRating[]`, `fastestGrowing[]`
- `commonTechStack[]`, `pricingDistribution`
- `newProducts`, `featuredProducts`, `withSocialProof` counts

---

## Examples

See [`examples/`](examples) for full code:

| File | What it does |
|---|---|
| [`quickstart.py`](examples/quickstart.py) | Analyze one product, print all signals |
| [`daily_digest.py`](examples/daily_digest.py) | Today's top 50 products with velocity ranking |
| [`maker_portfolio.py`](examples/maker_portfolio.py) | All products by a PH maker |
| [`topic_research.py`](examples/topic_research.py) | Top products in a topic with tech stack analysis |
| [`competitor_analysis.py`](examples/competitor_analysis.py) | Side-by-side comparison of competing products |
| [`trend_monitor.py`](examples/trend_monitor.py) | Track new launches and detect fast-growing products |
| [`export_to_csv.py`](examples/export_to_csv.py) | Export results to CSV |

---

## API reference

### `ProductHuntScraperClient(api_token, ph_client_id=None, ph_client_secret=None, timeout=600)`

| Param | Description |
|---|---|
| `api_token` | Apify API token. Falls back to `APIFY_API_TOKEN` env var. |
| `ph_client_id` | Optional PH API client_id (unlocks leaderboard/search/maker/topic) |
| `ph_client_secret` | Optional PH API client_secret |
| `timeout` | Max seconds to wait for actor run. Default 600. |

### `client.analyze(product_urls, include_competitor_analysis=False, **kwargs)`
Analyze specific product URLs. Returns `list[dict]`.

### `client.analyze_one(product_url, **kwargs)`
Analyze one product. Returns `dict`.

### `client.leaderboard(date=None, limit=50, include_competitor_analysis=False, **kwargs)`
Today's (or any date's) top products. Requires PH API credentials.

### `client.search(query, limit=20, include_competitor_analysis=False, **kwargs)`
Search by keyword. Requires PH API credentials.

### `client.maker_products(username, limit=50, **kwargs)`
All products by a PH username. Requires PH API credentials.

### `client.topic_products(topic_slug, limit=50, order="VOTES", include_competitor_analysis=False, **kwargs)`
Top products in a topic. Requires PH API credentials.
`order`: `"VOTES"` / `"NEWEST"` / `"FEATURED"`

### `client.estimate_cost(product_count)`
Returns estimated USD cost (`product_count × $0.005`).

---

## Sample output

```json
{
  "productName": "Midjourney",
  "tagline": "An independent research lab exploring new mediums of thought",
  "upvotes": 3500,
  "commentsCount": 81,
  "reviewsCount": 156,
  "rating": 4.7,
  "topics": ["Artificial Intelligence", "Design Tools", "Image Generation"],
  "makers": [{"name": "David Holz", "username": "davidholz"}],
  "hunter": {"name": "Fabian Maume", "username": "fabian_maume"},
  "badges": ["Product of the Day", "Product of the Week"],
  "isFeatured": true,
  "dailyRank": 1,
  "weeklyRank": 1,
  "pricing": "Paid",
  "popularityScore": 90,
  "daysSinceLaunch": 1247,
  "isNewProduct": false,
  "upvoteVelocity": 2.8,
  "engagementRate": 0.023,
  "techStackSignals": ["AI/ML", "Design"],
  "sentimentScore": 0.5,
  "maturityTier": "viral",
  "hasSocialProof": true,
  "pricingTier": "paid",
  "dataSource": "thunderbit"
}
```

---

## Use cases

### 🥇 Startup research
Track what's launching in your niche. Use `leaderboard()` daily to catch new products before they go viral.

### 🥈 Competitor monitoring
Use `analyze()` with `include_competitor_analysis=True` to get a side-by-side comparison of competing products — upvote velocity, tech stack, engagement rate.

### 🥉 Maker research
Use `maker_products()` to see a founder's full portfolio — how many products they've launched, which ones succeeded, what tech they use.

### 🎯 Topic intelligence
Use `topic_products("artificial-intelligence")` to see the top AI tools on PH — sorted by votes, newest, or featured.

### 📊 Trend detection
Filter by `isNewProduct=True` + `upvoteVelocity > 50` to find products gaining traction fast.

### 🔍 Tech stack research
Aggregate `techStackSignals` across 100 products in a niche to see which technologies dominate.

---

## Pricing

| Volume | Cost |
|---|---|
| 1 product | $0.005 |
| 100 products | $0.50 |
| 1,000 products | $5.00 |
| 10,000 products | $50.00 |

Free Apify tier includes ~$5 monthly credit — analyze ~1,000 products per month for free.

---

## How it works

1. **ProductHunt Official API v2** (when PH credentials provided) — GraphQL, 30+ fields
2. **Thunderbit** (no credentials needed, Apify infra only) — 13 fields
3. **Direct HTML scrape** (last resort) — ~10 fields

---

## Related Apify actors

- [YC Companies Scraper](https://apify.com/apivault_labs/yc-companies-scraper) — Y Combinator startups
- [Crunchbase Scraper](https://apify.com/apivault_labs/crunchbase-scraper) — startup funding data
- [LinkedIn Profile Scraper](https://apify.com/apivault_labs/linkedin-profile-scraper) — founder profiles
- [Domain Intelligence Scraper](https://apify.com/apivault_labs/domain-intelligence-scraper) — WHOIS, DNS, SSL

See [all actors by apivault_labs](https://apify.com/apivault_labs).

---

## License

MIT — see [LICENSE](LICENSE).

---

## Keywords

`producthunt` `product-hunt` `producthunt-scraper` `producthunt-api` `producthunt-leaderboard` `producthunt-search` `producthunt-maker` `startup-research` `startup-intelligence` `product-launch-tracker` `upvote-tracker` `tech-stack-detection` `competitor-analysis` `trend-monitoring` `launch-monitoring` `maker-portfolio` `web-scraping` `apify` `apify-actor` `python-sdk` `daily-digest` `topic-research`
