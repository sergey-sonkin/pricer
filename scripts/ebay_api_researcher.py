#!/usr/bin/env python3
"""
eBay API Researcher - Use official eBay APIs for pricing research

Uses eBay's Finding API and Browse API to get real market data including
sold listings, current prices, and market trends.
"""

import json
import os
import sys
import time
from dataclasses import dataclass

try:
    import requests
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: uv add requests python-dotenv")
    sys.exit(1)


@dataclass
class eBayListing:
    """eBay listing data"""

    title: str
    price: float
    currency: str
    condition: str
    listing_type: str  # auction, fixed_price
    end_time: str | None
    sold_date: str | None
    shipping_cost: float | None
    item_url: str
    image_url: str | None
    seller_feedback: int | None


@dataclass
class eBayPriceAnalysis:
    """eBay price analysis results"""

    search_terms: str
    total_sold: int
    total_active: int
    sold_listings: list[eBayListing]
    active_listings: list[eBayListing]
    price_statistics: dict[str, float | int]
    market_insights: list[str]
    confidence_score: float


class eBayAPIResearcher:
    """Research prices using official eBay APIs"""

    def __init__(self):
        """Initialize with eBay API credentials"""
        load_dotenv()

        # eBay API credentials
        self.use_sandbox = os.getenv("EBAY_USE_SANDBOX", "true").lower() == "true"

        if self.use_sandbox:
            self.app_id = os.getenv("EBAY_SANDBOX_APP_ID")
            self.cert_id = os.getenv("EBAY_SANDBOX_CERT_ID")
            self.dev_id = os.getenv("EBAY_SANDBOX_DEV_ID")
            self.client_secret = os.getenv("EBAY_SANDBOX_CLIENT_SECRET")
        else:
            self.app_id = os.getenv("EBAY_PROD_APP_ID")
            self.cert_id = os.getenv("EBAY_PROD_CERT_ID")
            self.dev_id = os.getenv("EBAY_PROD_DEV_ID")
            self.client_secret = os.getenv("EBAY_PROD_CLIENT_SECRET")

        if not self.app_id:
            env_type = "SANDBOX" if self.use_sandbox else "PROD"
            print(f"❌ eBay {env_type} API credentials not found!")
            print("You need to:")
            print("1. Sign up at: https://developer.ebay.com/")
            print("2. Create an app to get App ID (Client ID)")
            print("3. Set environment variables:")
            if self.use_sandbox:
                print("   export EBAY_SANDBOX_APP_ID='your_sandbox_app_id'")
                print(
                    "   export EBAY_SANDBOX_CLIENT_SECRET='your_sandbox_client_secret'"
                )
                print("   export EBAY_SANDBOX_CERT_ID='your_sandbox_cert_id'")
                print("   export EBAY_SANDBOX_DEV_ID='your_sandbox_dev_id'")
            else:
                print("   export EBAY_PROD_APP_ID='your_prod_app_id'")
                print("   export EBAY_PROD_CLIENT_SECRET='your_prod_client_secret'")
                print("   export EBAY_PROD_CERT_ID='your_prod_cert_id'")
                print("   export EBAY_PROD_DEV_ID='your_prod_dev_id'")
            sys.exit(1)

        # API endpoints (sandbox or production) - Using Browse API (Finding API deprecated Feb 2025)
        if self.use_sandbox:
            self.browse_api_url = "https://api.sandbox.ebay.com/buy/browse/v1"
            self.oauth_url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
            print(
                f"🧪 Using eBay Sandbox Browse API with App ID: {self.app_id[:10]}..."
            )
        else:
            self.browse_api_url = "https://api.ebay.com/buy/browse/v1"
            self.oauth_url = "https://api.ebay.com/identity/v1/oauth2/token"
            print(
                f"🚀 Using eBay Production Browse API with App ID: {self.app_id[:10]}..."
            )

        # Get OAuth token for Browse API
        self.access_token = self._get_oauth_token()

        # Headers for Browse API requests
        self.browse_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        }

    def _get_oauth_token(self) -> str:
        """Get OAuth 2.0 access token for Browse API"""
        try:
            import base64

            # Create basic auth header
            credentials = f"{self.app_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {encoded_credentials}",
            }

            data = {
                "grant_type": "client_credentials",
                "scope": "https://api.ebay.com/oauth/api_scope",
            }

            response = requests.post(
                self.oauth_url, headers=headers, data=data, timeout=30
            )
            response.raise_for_status()

            token_data = response.json()
            print("    🔑 OAuth token obtained successfully")
            return token_data["access_token"]

        except Exception as e:
            print(f"❌ Failed to get OAuth token: {e}")
            sys.exit(1)

    def research_product(
        self, product_description: str, category_id: str | None = None
    ) -> eBayPriceAnalysis:
        """
        Research a product using eBay APIs

        Args:
            product_description: Product description/search terms
            category_id: Optional eBay category ID for better results

        Returns:
            eBayPriceAnalysis with comprehensive market data
        """
        print(f"🔍 Researching '{product_description}' on eBay...")

        # 1. Get current active listings (Browse API doesn't provide sold listings directly)
        print("  🛒 Fetching active listings...")
        active_listings = self._get_active_listings_browse(
            product_description, category_id
        )

        # Note: Browse API doesn't provide sold listings - would need different eBay API for historical data
        print(
            "  📦 Sold listings not available via Browse API (requires different endpoint)"
        )
        sold_listings = []

        # 3. Analyze the data
        analysis = self._analyze_ebay_data(
            product_description, sold_listings, active_listings
        )

        return analysis

    def _get_active_listings_browse(
        self, keywords: str, category_id: str | None = None, max_results: int = 50
    ) -> list[eBayListing]:
        """Get active listings using Browse API"""
        listings = []

        try:
            # Build search URL
            search_url = f"{self.browse_api_url}/item_summary/search"

            # Build query parameters
            params = {
                "q": keywords,
                "limit": min(max_results, 200),  # Browse API max is 200
                "sort": "price",
                "filter": "conditionIds:{1000|3000}",  # New and Used
            }

            if category_id:
                params["category_ids"] = category_id

            # Make API request
            response = requests.get(
                search_url,
                headers=self.browse_headers,
                params=params,
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()

            # Debug: Print API status
            total_items = data.get("total", 0)
            print(f"    📊 API returned {total_items} active items")

            # Parse results
            items = data.get("itemSummaries", [])

            for item in items:
                try:
                    listing = self._parse_browse_item(item)
                    if listing:
                        listings.append(listing)
                        print(
                            f"    🛒 Active: ${listing.price:.2f} - {listing.title[:50]}..."
                        )
                except Exception as e:
                    print(f"    ⚠️ Failed to parse item: {e}")
                    continue

            print(f"    ✅ Found {len(listings)} active listings")

        except requests.exceptions.RequestException as e:
            print(f"    ❌ Error fetching active listings: {e}")
        except Exception as e:
            print(f"    ❌ Unexpected error: {e}")

        return listings

    def _parse_browse_item(self, item: dict) -> eBayListing | None:
        """Parse Browse API item response into eBayListing"""
        try:
            # Extract basic info from Browse API format
            title = item.get("title", "")

            # Extract price info
            price_info = item.get("price", {})
            price = float(price_info.get("value", "0"))
            currency = price_info.get("currency", "USD")

            # Extract condition
            condition_info = item.get("condition", "")
            condition = condition_info if condition_info else "Unknown"

            # Browse API items are always active listings
            listing_type = "FixedPrice"  # Browse API primarily shows Buy It Now items

            # Extract shipping
            shipping_info = item.get("shippingOptions", [])
            shipping_cost = None
            if shipping_info and len(shipping_info) > 0:
                shipping_cost_info = shipping_info[0].get("shippingCost", {})
                if shipping_cost_info:
                    shipping_cost = float(shipping_cost_info.get("value", "0"))

            # URLs and image
            item_url = item.get("itemWebUrl", "")
            image_url = item.get("image", {}).get("imageUrl", "")

            # Seller info
            seller_info = item.get("seller", {})
            seller_feedback = None
            if seller_info.get("feedbackPercentage"):
                seller_feedback = int(float(seller_info["feedbackPercentage"]))

            return eBayListing(
                title=title,
                price=price,
                currency=currency,
                condition=condition,
                listing_type=listing_type,
                end_time=None,  # Browse API doesn't provide end time for active listings
                sold_date=None,
                shipping_cost=shipping_cost,
                item_url=item_url,
                image_url=image_url,
                seller_feedback=seller_feedback,
            )

        except (KeyError, ValueError, TypeError) as e:
            print(f"    🔍 Parse error details: {e}")
            return None

    def _analyze_ebay_data(
        self,
        search_terms: str,
        sold_listings: list[eBayListing],
        active_listings: list[eBayListing],
    ) -> eBayPriceAnalysis:
        """Analyze eBay data and generate insights"""

        # Calculate price statistics from sold listings
        sold_prices = [listing.price for listing in sold_listings if listing.price > 0]
        active_prices = [
            listing.price for listing in active_listings if listing.price > 0
        ]

        if sold_prices:
            sold_prices.sort()
            price_stats = {
                "sold_min": min(sold_prices),
                "sold_max": max(sold_prices),
                "sold_avg": sum(sold_prices) / len(sold_prices),
                "sold_median": sold_prices[len(sold_prices) // 2],
                "sold_count": len(sold_prices),
            }
        else:
            price_stats = {
                "sold_min": 0,
                "sold_max": 0,
                "sold_avg": 0,
                "sold_median": 0,
                "sold_count": 0,
            }

        if active_prices:
            active_prices.sort()
            price_stats.update(
                {
                    "active_min": min(active_prices),
                    "active_max": max(active_prices),
                    "active_avg": sum(active_prices) / len(active_prices),
                    "active_median": active_prices[len(active_prices) // 2],
                    "active_count": len(active_prices),
                }
            )
        else:
            price_stats.update(
                {
                    "active_min": 0,
                    "active_max": 0,
                    "active_avg": 0,
                    "active_median": 0,
                    "active_count": 0,
                }
            )

        # Generate market insights
        insights = self._generate_market_insights(
            price_stats, sold_listings, active_listings
        )

        # Calculate confidence score
        confidence = self._calculate_confidence(
            len(sold_listings), len(active_listings)
        )

        return eBayPriceAnalysis(
            search_terms=search_terms,
            total_sold=len(sold_listings),
            total_active=len(active_listings),
            sold_listings=sold_listings,
            active_listings=active_listings,
            price_statistics=price_stats,
            market_insights=insights,
            confidence_score=confidence,
        )

    def _generate_market_insights(
        self,
        stats: dict[str, float | int],
        sold_listings: list[eBayListing],
        active_listings: list[eBayListing],
    ) -> list[str]:
        """Generate actionable market insights"""
        insights = []

        if stats["sold_count"] > 0:
            insights.append(f"Market data based on {stats['sold_count']} recent sales")
            insights.append(f"Typical selling price: ${stats['sold_avg']:.2f}")

            if stats["active_count"] > 0:
                # Compare sold vs active pricing
                if stats["active_avg"] > stats["sold_avg"] * 1.2:
                    insights.append(
                        "Current listings are priced high compared to recent sales"
                    )
                elif stats["active_avg"] < stats["sold_avg"] * 0.8:
                    insights.append(
                        "Current market may be soft - competitive pricing opportunity"
                    )
                else:
                    insights.append("Current pricing aligns well with recent sales")

        # Condition analysis
        conditions = {}
        for listing in sold_listings:
            conditions[listing.condition] = conditions.get(listing.condition, 0) + 1

        if conditions:
            top_condition = max(conditions.keys(), key=lambda k: conditions[k])
            insights.append(f"Most common condition sold: {top_condition}")

        # Listing type analysis
        auction_count = len(
            [
                listing
                for listing in sold_listings
                if "auction" in listing.listing_type.lower()
            ]
        )
        if auction_count > 0 and len(sold_listings) > 0:
            auction_pct = (auction_count / len(sold_listings)) * 100
            if auction_pct > 30:
                insights.append(
                    f"{auction_pct:.0f}% of sales were auctions - consider auction format"
                )

        return insights

    def _calculate_confidence(self, sold_count: int, active_count: int) -> float:
        """Calculate confidence score based on data availability"""
        confidence = 0.0

        # Sold listings are most valuable
        confidence += min(sold_count * 0.02, 0.7)  # Up to 0.7 for 35+ sold items

        # Active listings provide market context
        confidence += min(active_count * 0.01, 0.2)  # Up to 0.2 for 20+ active items

        # Bonus for having both types of data
        if sold_count > 0 and active_count > 0:
            confidence += 0.1

        return min(confidence, 1.0)

    def print_analysis(self, analysis: eBayPriceAnalysis):
        """Print formatted eBay analysis"""
        print(f"\n📊 eBay Analysis for: {analysis.search_terms}")
        print("=" * 60)

        print(f"🎯 Confidence Score: {analysis.confidence_score:.2f}")
        print(f"📈 Data: {analysis.total_sold} sold, {analysis.total_active} active")

        stats = analysis.price_statistics
        if stats["sold_count"] > 0:
            print("\n💰 Sold Listings Price Analysis:")
            print(f"   • Range: ${stats['sold_min']:.2f} - ${stats['sold_max']:.2f}")
            print(f"   • Average: ${stats['sold_avg']:.2f}")
            print(f"   • Median: ${stats['sold_median']:.2f}")

        if stats["active_count"] > 0:
            print("\n🛒 Active Listings Price Analysis:")
            print(
                f"   • Range: ${stats['active_min']:.2f} - ${stats['active_max']:.2f}"
            )
            print(f"   • Average: ${stats['active_avg']:.2f}")
            print(f"   • Median: ${stats['active_median']:.2f}")

        if analysis.market_insights:
            print("\n💡 Market Insights:")
            for insight in analysis.market_insights:
                print(f"   • {insight}")

        if analysis.sold_listings:
            print("\n🏷️ Recent Sales (showing top 5):")
            for i, listing in enumerate(analysis.sold_listings[:5]):
                print(f"   {i + 1}. ${listing.price:.2f} - {listing.title[:50]}...")


def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print(
            "Usage: python ebay_api_researcher.py <product_description> [category_id]"
        )
        print('Example: python ebay_api_researcher.py "cat litter box"')
        print('Example: python ebay_api_researcher.py "iphone 12" "9355"')
        sys.exit(1)

    product_description = sys.argv[1]
    category_id = sys.argv[2] if len(sys.argv) > 2 else None

    # Initialize researcher
    researcher = eBayAPIResearcher()

    try:
        # Research product
        analysis = researcher.research_product(product_description, category_id)

        # Print results
        researcher.print_analysis(analysis)

        # Save results to JSON
        os.makedirs("logs/ebay_api_researcher", exist_ok=True)
        output_file = f"logs/ebay_api_researcher/ebay_analysis_{int(time.time())}.json"
        with open(output_file, "w") as f:
            json.dump(
                {
                    "search_terms": analysis.search_terms,
                    "total_sold": analysis.total_sold,
                    "total_active": analysis.total_active,
                    "price_statistics": analysis.price_statistics,
                    "market_insights": analysis.market_insights,
                    "confidence_score": analysis.confidence_score,
                    "sold_listings": [
                        {
                            "title": listing.title,
                            "price": listing.price,
                            "condition": listing.condition,
                            "sold_date": listing.sold_date,
                            "url": listing.item_url,
                        }
                        for listing in analysis.sold_listings
                    ],
                    "active_listings": [
                        {
                            "title": listing.title,
                            "price": listing.price,
                            "condition": listing.condition,
                            "url": listing.item_url,
                        }
                        for listing in analysis.active_listings
                    ],
                },
                f,
                indent=2,
            )

        print(f"\n💾 Results saved to: {output_file}")

    except Exception as e:
        print(f"❌ Error researching product: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
