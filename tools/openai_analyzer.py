"""
OpenAI Analyzer Tool for Agent

Provides a clean tool interface for the OpenAI image analysis functionality.
Uses the OpenAIAnalyzer from lib.analyzers for the agent system.
"""

import os
from typing import Any

from lib.analyzers import OpenAIAnalyzer

from .base import ToolDefinition


def analyze_image_with_openai(input_data: dict[str, Any]) -> str:
    """
    Analyze a product image using OpenAI GPT-4 Vision for resale insights

    Args:
        input_data: Dictionary containing 'image_path' key

    Returns:
        Formatted analysis results as a string

    Raises:
        Exception: If OpenAIAnalyzer is not available or analysis fails
    """
    if OpenAIAnalyzer is None:
        raise Exception(
            "OpenAIAnalyzer not available. Install dependencies with: uv add openai pillow"
        )

    image_path = input_data["image_path"]

    # Validate image path exists
    if not os.path.exists(image_path):
        raise Exception(f"Image not found: {image_path}")

    try:
        # Initialize OpenAI analyzer
        analyzer = OpenAIAnalyzer()

        # Analyze the image
        analysis = analyzer.analyze_image(image_path)

        # Format the results as a readable string
        result = f"""🤖 OpenAI Vision Analysis for: {os.path.basename(image_path)}

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
        raise Exception(f"Error analyzing image with OpenAI: {str(e)}") from e


# Tool definition
OPENAI_ANALYZER_TOOL = ToolDefinition(
    name="analyze_image_with_openai",
    description="Analyze a product image using OpenAI GPT-4 Vision to get detailed product information, brand identification, condition assessment, and pricing factors for resale purposes. This tool provides advanced AI analysis and is excellent for sophisticated product identification and market insights.",
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
    function=analyze_image_with_openai,
)
