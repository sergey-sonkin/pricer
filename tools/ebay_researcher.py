"""
eBay API Researcher Tool for Agent

Provides a clean tool interface for eBay marketplace research functionality.
Uses the eBayAPIResearcher from scripts for the agent system.
"""

import os
import sys
from typing import Any

from .base import ToolDefinition

# Add scripts directory to path to import the researcher
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

try:
    from ebay_api_researcher import eBayAPIResearcher
except ImportError as e:
    print(f"Warning: Could not import eBayAPIResearcher: {e}")
    eBayAPIResearcher = None


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
        Exception: If eBayAPIResearcher is not available or research fails
    """
    if eBayAPIResearcher is None:
        raise Exception(
            "eBayAPIResearcher not available. Check eBay API credentials are set."
        )

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
📈 Data Quality: {analysis.sold_count} sold, {analysis.active_count} active listings"""

        if analysis.active_count > 0:
            result += f"""

🛒 Active Listings Price Analysis:
   • Range: ${analysis.price_statistics['active_min']:.2f} - ${analysis.price_statistics['active_max']:.2f}
   • Average: ${analysis.price_statistics['active_avg']:.2f}
   • Median: ${analysis.price_statistics['active_median']:.2f}"""

        if analysis.sold_count > 0:
            result += f"""

💰 Sold Listings Price Analysis:
   • Range: ${analysis.price_statistics['sold_min']:.2f} - ${analysis.price_statistics['sold_max']:.2f}
   • Average: ${analysis.price_statistics['sold_avg']:.2f}
   • Median: ${analysis.price_statistics['sold_median']:.2f}"""

        if analysis.market_insights:
            result += "\n\n🔍 Market Insights:"
            for insight in analysis.market_insights:
                result += f"\n• {insight}"

        if (
            hasattr(analysis, "recommended_price_range")
            and analysis.recommended_price_range
        ):
            result += f"\n\n💡 Recommended Pricing: ${analysis.recommended_price_range['min']:.2f} - ${analysis.recommended_price_range['max']:.2f}"

        result += f"\n\n📄 Full analysis saved to: {analysis.log_file_path}"

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
