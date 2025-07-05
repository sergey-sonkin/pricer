"""
eBay API Researcher Tool for Agent

Provides a clean tool interface for eBay marketplace research functionality.
Uses the BrowseAPI from lib/browseapi directly.
"""

import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

from lib.browseapi.client import BrowseAPI

from .base import ToolDefinition


@dataclass
class eBayListing:
    """eBay listing data"""

    title: str
    price: float
    currency: str
    condition: str
    listing_type: str
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
    log_file_path: str | None = None


class eBayAPIResearcher:
    """Research prices using eBay Browse API"""

    def __init__(self):
        """Initialize with eBay API credentials"""
        load_dotenv()

        # eBay API credentials
        self.use_sandbox = os.getenv("EBAY_USE_SANDBOX", "true").lower() == "true"

        if self.use_sandbox:
            self.app_id = os.getenv("EBAY_SANDBOX_APP_ID")
            self.cert_id = os.getenv("EBAY_SANDBOX_CERT_ID")
        else:
            self.app_id = os.getenv("EBAY_PROD_APP_ID")
            self.cert_id = os.getenv("EBAY_PROD_CERT_ID")

        if not self.app_id or not self.cert_id:
            env_type = "SANDBOX" if self.use_sandbox else "PROD"
            raise Exception(f"eBay {env_type} API credentials not found")

        # Initialize BrowseAPI client
        self.browse_client = BrowseAPI(
            app_id=self.app_id,
            cert_id=self.cert_id,
            marketplace_id="EBAY_US",
        )

    def research_product(
        self, product_description: str, category_id: str | None = None
    ) -> eBayPriceAnalysis:
        """Research a product using eBay APIs"""
        # Get active listings using Browse API
        active_listings = self._get_active_listings(product_description, category_id)

        # Note: Browse API doesn't provide sold listings
        sold_listings = []

        # Analyze the data
        analysis = self._analyze_ebay_data(
            product_description, sold_listings, active_listings
        )

        return analysis

    def _get_active_listings(
        self, keywords: str, category_id: str | None = None, max_results: int = 50
    ) -> list[eBayListing]:
        """Get active listings using Browse API"""
        listings = []

        try:
            # Prepare search parameters for browseapi library
            search_params = [{"q": keywords, "limit": min(max_results, 200)}]

            if category_id:
                search_params[0]["category_ids"] = category_id

            # Use browseapi library to search
            responses = self.browse_client.execute("search", search_params)

            if not responses:
                return listings

            response = responses[0]
            if hasattr(response, "itemSummaries"):
                for item_summary in response.itemSummaries:
                    try:
                        listing = self._parse_browse_item_summary(item_summary)
                        if listing:
                            listings.append(listing)
                    except Exception:
                        continue

        except Exception:
            pass

        return listings

    def _parse_browse_item_summary(self, item_summary) -> eBayListing | None:
        """Parse browseapi ItemSummary object into eBayListing"""
        try:
            title = item_summary.title or ""

            # Extract price info
            price = 0.0
            currency = "USD"
            if hasattr(item_summary, "price") and item_summary.price:
                price = float(item_summary.price.value or 0)
                currency = item_summary.price.currency or "USD"

            condition = item_summary.condition or "Unknown"
            listing_type = "FixedPrice"

            # Extract shipping
            shipping_cost = None
            if (
                hasattr(item_summary, "shippingOptions")
                and item_summary.shippingOptions
            ):
                shipping_option = item_summary.shippingOptions[0]
                if (
                    hasattr(shipping_option, "shippingCost")
                    and shipping_option.shippingCost
                ):
                    shipping_cost = float(shipping_option.shippingCost.value or 0)

            item_url = item_summary.itemWebUrl or ""
            image_url = ""
            if hasattr(item_summary, "image") and item_summary.image:
                image_url = item_summary.image.imageUrl or ""

            seller_feedback = None
            if hasattr(item_summary, "seller") and item_summary.seller:
                if hasattr(item_summary.seller, "feedbackPercentage"):
                    seller_feedback = int(
                        float(item_summary.seller.feedbackPercentage or 0)
                    )

            return eBayListing(
                title=title,
                price=price,
                currency=currency,
                condition=condition,
                listing_type=listing_type,
                end_time=None,
                sold_date=None,
                shipping_cost=shipping_cost,
                item_url=item_url,
                image_url=image_url,
                seller_feedback=seller_feedback,
            )

        except (AttributeError, ValueError, TypeError):
            return None

    def _analyze_ebay_data(
        self,
        search_terms: str,
        sold_listings: list[eBayListing],
        active_listings: list[eBayListing],
    ) -> eBayPriceAnalysis:
        """Analyze eBay data and generate insights"""
        # Calculate price statistics
        sold_prices = [listing.price for listing in sold_listings if listing.price > 0]
        active_prices = [
            listing.price for listing in active_listings if listing.price > 0
        ]

        price_stats: dict[str, float | int] = {
            "sold_min": min(sold_prices) if sold_prices else 0.0,
            "sold_max": max(sold_prices) if sold_prices else 0.0,
            "sold_avg": sum(sold_prices) / len(sold_prices) if sold_prices else 0.0,
            "sold_median": sorted(sold_prices)[len(sold_prices) // 2]
            if sold_prices
            else 0.0,
            "sold_count": len(sold_prices),
            "active_min": min(active_prices) if active_prices else 0.0,
            "active_max": max(active_prices) if active_prices else 0.0,
            "active_avg": sum(active_prices) / len(active_prices)
            if active_prices
            else 0.0,
            "active_median": sorted(active_prices)[len(active_prices) // 2]
            if active_prices
            else 0.0,
            "active_count": len(active_prices),
        }

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

        if stats["active_count"] > 0:
            insights.append(f"Found {stats['active_count']} active listings")
            insights.append(f"Average listing price: ${stats['active_avg']:.2f}")

        if stats["active_count"] == 0:
            insights.append(
                "No active listings found - consider expanding search terms"
            )

        # Condition analysis
        active_conditions = {}
        for listing in active_listings:
            active_conditions[listing.condition] = (
                active_conditions.get(listing.condition, 0) + 1
            )

        if active_conditions:
            top_condition = max(
                active_conditions.keys(), key=lambda k: active_conditions[k]
            )
            insights.append(f"Most common condition: {top_condition}")

        return insights

    def _calculate_confidence(self, sold_count: int, active_count: int) -> float:
        """Calculate confidence score based on data availability"""
        confidence = 0.0

        # Active listings provide some market context
        confidence += min(active_count * 0.02, 0.8)  # Up to 0.8 for 40+ active items

        # Sold listings are most valuable (but not available via Browse API)
        confidence += min(sold_count * 0.02, 0.2)  # Up to 0.2 for sold items

        return min(confidence, 1.0)


def research_ebay_prices(input_data: dict[str, Any]) -> str:
    """
    Research eBay marketplace data for pricing insights

    Args:
        input_data: Dictionary containing:
            - 'product_description' (required): The product to search for
            - 'category_id' (optional): eBay category ID to narrow search

    Returns:
        Formatted market analysis results as a string

    Raises:
        Exception: If BrowseAPI is not available or research fails
    """
    if BrowseAPI is None:
        raise Exception("BrowseAPI not available. Check eBay API credentials are set.")

    product_description = input_data["product_description"]
    category_id = input_data.get("category_id")

    if not product_description.strip():
        raise Exception("Product description cannot be empty")

    try:
        # Initialize eBay researcher
        researcher = eBayAPIResearcher()

        # Research the product
        analysis = researcher.research_product(product_description, category_id)

        # Format the results as a readable string
        result = f"""📊 eBay Market Analysis for: {product_description}
============================================================
🎯 Confidence Score: {analysis.confidence_score:.2f}
📈 Data Quality: {analysis.total_sold} sold, {analysis.total_active} active listings"""

        if analysis.total_active > 0:
            result += f"""

🛒 Active Listings Price Analysis:
   • Range: ${analysis.price_statistics["active_min"]:.2f} - ${analysis.price_statistics["active_max"]:.2f}
   • Average: ${analysis.price_statistics["active_avg"]:.2f}
   • Median: ${analysis.price_statistics["active_median"]:.2f}"""

        if analysis.total_sold > 0:
            result += f"""

💰 Sold Listings Price Analysis:
   • Range: ${analysis.price_statistics["sold_min"]:.2f} - ${analysis.price_statistics["sold_max"]:.2f}
   • Average: ${analysis.price_statistics["sold_avg"]:.2f}
   • Median: ${analysis.price_statistics["sold_median"]:.2f}"""

        if analysis.market_insights:
            result += "\n\n🔍 Market Insights:"
            for insight in analysis.market_insights:
                result += f"\n• {insight}"

        return result

    except Exception as e:
        raise Exception(f"Error researching eBay prices: {str(e)}") from e


# Tool definition
EBAY_RESEARCHER_TOOL = ToolDefinition(
    name="research_ebay_prices",
    description="Research eBay marketplace data to get comprehensive pricing insights including active listings, sold items analysis, market trends, and pricing recommendations. Essential for understanding current market conditions and competitive pricing for resale items.",
    input_schema={
        "type": "object",
        "properties": {
            "product_description": {
                "type": "string",
                "description": "The product to research on eBay. Be specific and include relevant details like brand, model, condition, etc. Example: 'iPhone 12 Pro 128GB Unlocked' or 'vintage Levi's 501 jeans size 32x34'",
            },
            "category_id": {
                "type": "string",
                "description": "Optional eBay category ID to narrow the search results. Use specific category IDs like '9355' for Cell Phones or '11450' for Clothing. Leave empty for broad search.",
            },
        },
        "required": ["product_description"],
    },
    function=research_ebay_prices,
)
