"""
Gemini Analyzer Tool for Agent

Provides a clean tool interface for the Gemini image analysis functionality.
Uses the GeminiAnalyzer from lib.analyzers for the agent system.
"""

import os
from typing import Any

from .base import ToolDefinition

try:
    from lib.analyzers import GeminiAnalyzer
except ImportError as e:
    print(f"Warning: Could not import GeminiAnalyzer: {e}")
    GeminiAnalyzer = None


def analyze_image_with_gemini(input_data: dict[str, Any]) -> str:
    """
    Analyze a product image using Google Gemini AI for resale insights

    Args:
        input_data: Dictionary containing 'image_path' key

    Returns:
        Formatted analysis results as a string

    Raises:
        Exception: If GeminiAnalyzer is not available or analysis fails
    """
    if GeminiAnalyzer is None:
        raise Exception(
            "GeminiAnalyzer not available. Install dependencies with: uv add google-genai pillow"
        )

    image_path = input_data["image_path"]

    # Validate image path exists
    if not os.path.exists(image_path):
        raise Exception(f"Image not found: {image_path}")

    try:
        # Initialize Gemini analyzer
        analyzer = GeminiAnalyzer()

        # Analyze the image
        analysis = analyzer.analyze_image(image_path)

        # Format the results as a readable string
        result = f"""🤖 Gemini AI Analysis for: {os.path.basename(image_path)}

🎯 Confidence Level: {analysis.confidence_level.title()}

📝 Product Description:
{analysis.product_description}

📦 Product Type: {analysis.product_type.title()}
🏪 Market Category: {analysis.market_category.title()}"""

        if analysis.brand:
            result += f"\n🏢 Brand: {analysis.brand}"

        if analysis.condition:
            result += f"\n⭐ Condition: {analysis.condition.title()}"

        if analysis.notable_features:
            result += "\n\n✨ Notable Features:"
            for feature in analysis.notable_features:
                result += f"\n• {feature}"

        if analysis.pricing_factors:
            result += "\n\n💰 Pricing Factors:"
            for factor in analysis.pricing_factors:
                result += f"\n• {factor}"

        return result

    except Exception as e:
        raise Exception(f"Error analyzing image with Gemini: {str(e)}") from e


# Tool definition
GEMINI_ANALYZER_TOOL = ToolDefinition(
    name="analyze_image_with_gemini",
    description="Analyze a product image using Google Gemini AI to get detailed product information, brand identification, condition assessment, and pricing factors for resale purposes. This tool is excellent for identifying products from photos and understanding their market value.",
    input_schema={
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "The relative or absolute path to the image file to analyze. Supports common image formats like JPG, PNG, etc.",
            }
        },
        "required": ["image_path"],
    },
    function=analyze_image_with_gemini,
)
