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
    price_statistics: dict[str, float]
    market_insights: list[str]
    confidence_score: float


class eBayAPIResearcher:
    """Research prices using official eBay APIs"""

    def __init__(self):
        """Initialize with eBay API credentials"""
        load_dotenv()

        # eBay API credentials
        self.app_id = os.getenv("EBAY_APP_ID")
        self.cert_id = os.getenv("EBAY_CERT_ID")
        self.dev_id = os.getenv("EBAY_DEV_ID")

        if not self.app_id:
            print("❌ eBay API credentials not found!")
            print("You need to:")
            print("1. Sign up at: https://developer.ebay.com/")
            print("2. Create an app to get App ID (Client ID)")
            print("3. Set environment variables:")
            print("   export EBAY_APP_ID='your_app_id'")
            print("   export EBAY_CERT_ID='your_cert_id'")
            print("   export EBAY_DEV_ID='your_dev_id'")
            sys.exit(1)

        # API endpoints
        self.finding_api_url = "https://svcs.ebay.com/services/search/FindingService/v1"
        self.browse_api_url = "https://api.ebay.com/buy/browse/v1"

        # Headers for API requests
        self.finding_headers = {
            "X-EBAY-SOA-OPERATION-NAME": "findCompletedItems",
            "X-EBAY-SOA-SERVICE-VERSION": "1.13.0",
            "X-EBAY-SOA-REQUEST-DATA-FORMAT": "JSON",
            "X-EBAY-SOA-GLOBAL-ID": "EBAY-US",
            "Content-Type": "application/json",
        }

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

        # 1. Get sold listings (completed items)
        print("  📦 Fetching sold listings...")
        sold_listings = self._get_sold_listings(product_description, category_id)

        # 2. Get current active listings
        print("  🛒 Fetching active listings...")
        active_listings = self._get_active_listings(product_description, category_id)

        # 3. Analyze the data
        analysis = self._analyze_ebay_data(
            product_description, sold_listings, active_listings
        )

        return analysis

    def _get_sold_listings(
        self, keywords: str, category_id: str | None = None, max_results: int = 50
    ) -> list[eBayListing]:
        """Get sold/completed listings using Finding API"""
        listings = []

        try:
            # Build request payload
            payload = {
                "findCompletedItemsRequest": {
                    "keywords": keywords,
                    "itemFilter": [
                        {"name": "SoldItemsOnly", "value": "true"},
                        {"name": "ListingType", "value": ["FixedPrice", "Auction"]},
                    ],
                    "sortOrder": "EndTimeSoonest",
                    "paginationInput": {"entriesPerPage": min(max_results, 100)},
                }
            }

            # Add category filter if provided
            if category_id:
                payload["findCompletedItemsRequest"]["categoryId"] = [category_id]

            # Make API request
            response = requests.post(
                self.finding_api_url,
                headers=self.finding_headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()

            # Check for API errors
            if (
                data.get("findCompletedItemsResponse", [{}])[0].get("ack", [""])[0]
                != "Success"
            ):
                error_msg = data.get("findCompletedItemsResponse", [{}])[0].get(
                    "errorMessage", {}
                )
                print(f"    ❌ eBay API error: {error_msg}")
                return listings

            # Parse results
            search_result = data.get("findCompletedItemsResponse", [{}])[0].get(
                "searchResult", [{}]
            )[0]
            items = search_result.get("item", [])

            for item in items:
                try:
                    listing = self._parse_ebay_item(item, is_sold=True)
                    if listing:
                        listings.append(listing)
                except Exception:
                    # Skip items that can't be parsed
                    continue

            print(f"    ✅ Found {len(listings)} sold listings")

        except requests.exceptions.RequestException as e:
            print(f"    ❌ Error fetching sold listings: {e}")
        except Exception as e:
            print(f"    ❌ Unexpected error: {e}")

        return listings

    def _get_active_listings(
        self, keywords: str, category_id: str | None = None, max_results: int = 25
    ) -> list[eBayListing]:
        """Get current active listings using Finding API"""
        listings = []

        try:
            # Build request payload for active listings
            self.finding_headers["X-EBAY-SOA-OPERATION-NAME"] = "findItemsByKeywords"

            payload = {
                "findItemsByKeywordsRequest": {
                    "keywords": keywords,
                    "itemFilter": [
                        {"name": "ListingType", "value": ["FixedPrice", "Auction"]},
                        {"name": "Condition", "value": ["New", "Used"]},
                    ],
                    "sortOrder": "PricePlusShippingLowest",
                    "paginationInput": {"entriesPerPage": min(max_results, 100)},
                }
            }

            if category_id:
                payload["findItemsByKeywordsRequest"]["categoryId"] = [category_id]

            response = requests.post(
                self.finding_api_url,
                headers=self.finding_headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()

            # Check for API errors
            if (
                data.get("findItemsByKeywordsResponse", [{}])[0].get("ack", [""])[0]
                != "Success"
            ):
                error_msg = data.get("findItemsByKeywordsResponse", [{}])[0].get(
                    "errorMessage", {}
                )
                print(f"    ❌ eBay API error: {error_msg}")
                return listings

            # Parse results
            search_result = data.get("findItemsByKeywordsResponse", [{}])[0].get(
                "searchResult", [{}]
            )[0]
            items = search_result.get("item", [])

            for item in items:
                try:
                    listing = self._parse_ebay_item(item, is_sold=False)
                    if listing:
                        listings.append(listing)
                except Exception:
                    continue

            print(f"    ✅ Found {len(listings)} active listings")

        except requests.exceptions.RequestException as e:
            print(f"    ❌ Error fetching active listings: {e}")
        except Exception as e:
            print(f"    ❌ Unexpected error: {e}")

        # Reset header for next request
        self.finding_headers["X-EBAY-SOA-OPERATION-NAME"] = "findCompletedItems"

        return listings

    def _parse_ebay_item(self, item: dict, is_sold: bool = False) -> eBayListing | None:
        """Parse eBay API item response into eBayListing"""
        try:
            # Extract basic info
            title = item.get("title", [""])[0]

            # Extract price info
            selling_status = item.get("sellingStatus", [{}])[0]
            current_price = selling_status.get("currentPrice", [{}])[0]
            price = float(current_price.get("@currencyId", "0"))
            currency = current_price.get("@currencyId", "USD")

            # Extract condition
            condition_info = item.get("condition", [{}])[0]
            condition = condition_info.get("conditionDisplayName", ["Unknown"])[0]

            # Extract listing info
            listing_info = item.get("listingInfo", [{}])[0]
            listing_type = listing_info.get("listingType", ["FixedPrice"])[0]
            end_time = listing_info.get("endTime", [""])[0]

            # Extract shipping
            shipping_info = item.get("shippingInfo", [{}])[0]
            shipping_cost = None
            if shipping_info.get("shippingServiceCost"):
                shipping_cost = float(
                    shipping_info["shippingServiceCost"][0].get("__value__", 0)
                )

            # Build URLs
            item_url = item.get("viewItemURL", [""])[0]

            # Extract image
            image_url = None
            if item.get("galleryURL"):
                image_url = item["galleryURL"][0]

            # Extract seller info
            seller_info = item.get("sellerInfo", [{}])[0]
            seller_feedback = None
            if seller_info.get("feedbackScore"):
                seller_feedback = int(seller_info["feedbackScore"][0])

            return eBayListing(
                title=title,
                price=price,
                currency=currency,
                condition=condition,
                listing_type=listing_type,
                end_time=end_time if not is_sold else None,
                sold_date=end_time if is_sold else None,
                shipping_cost=shipping_cost,
                item_url=item_url,
                image_url=image_url,
                seller_feedback=seller_feedback,
            )

        except (KeyError, ValueError, IndexError):
            # Skip items that can't be parsed properly
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
        stats: dict[str, float],
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
            top_condition = max(conditions, key=conditions.get)
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
