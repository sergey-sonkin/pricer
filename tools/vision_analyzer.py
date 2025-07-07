"""
Google Vision API Analyzer Tool for Agent

Provides a clean tool interface for the Google Vision API image analysis functionality.
Uses the VisionAnalyzer from lib.analyzers for the agent system.
"""

import os
from typing import Any

from lib.analyzers.vision import VisionAnalyzer

from .base import ToolDefinition


def analyze_image_with_vision(input_data: dict[str, Any]) -> str:
    """
    Analyze a product image using Google Vision API for detailed feature extraction

    Args:
        input_data: Dictionary containing 'image_path' key

    Returns:
        Formatted analysis results as a string

    Raises:
        Exception: If VisionAnalyzer is not available or analysis fails
    """
    if VisionAnalyzer is None:
        raise Exception(
            "VisionAnalyzer not available. Install dependencies with: uv add google-cloud-vision"
        )

    image_path = input_data["image_path"]

    # Validate image path exists
    if not os.path.exists(image_path):
        raise Exception(f"Image not found: {image_path}")

    try:
        # Initialize Vision analyzer
        analyzer = VisionAnalyzer()

        # Analyze the image
        analysis = analyzer.analyze_image(image_path)

        # Format the results as a readable string
        result = f"""🔍 Google Vision API Analysis for: {os.path.basename(image_path)}

📊 Confidence Score: {analysis.confidence_score:.2f}"""

        if analysis.labels:
            result += "\n\n🏷️ Detected Labels:"
            for label in analysis.labels[:5]:  # Show top 5
                result += f"\n• {label}"

        if analysis.objects:
            result += "\n\n📦 Detected Objects:"
            for obj in analysis.objects:
                result += f"\n• {obj}"

        if analysis.brands:
            result += "\n\n🏢 Potential Brands:"
            for brand in analysis.brands:
                result += f"\n• {brand}"

        if analysis.text:
            result += "\n\n📝 Detected Text:"
            for text in analysis.text[:3]:  # Show first 3 lines
                result += f"\n• {text}"

        return result

    except Exception as e:
        raise Exception(f"Error analyzing image with Google Vision: {str(e)}") from e


# Tool definition
VISION_ANALYZER_TOOL = ToolDefinition(
    name="analyze_image_with_vision",
    description="Analyze a product image using Google Vision API to extract detailed features including labels, objects, text, and potential brands. This tool is excellent for detecting specific product features and text that might be missed by AI vision models.",
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
    function=analyze_image_with_vision,
)
