"""
Gemini Analyzer - AI-powered product identification from photos

Uses Google Gemini API to analyze product images and provide intelligent
product descriptions, brand identification, and market insights.

This is the core analyzer class, separated from CLI functionality.
"""

import json
import os
from dataclasses import dataclass

try:
    import google.genai as genai
    from PIL import Image
except ImportError as e:
    raise ImportError(
        f"Missing dependencies: {e}. Install with: uv add google-genai pillow"
    ) from e


@dataclass
class ProductAnalysis:
    """AI-powered product analysis results"""

    product_description: str
    brand: str | None
    product_type: str
    condition: str | None
    notable_features: list[str]
    market_category: str
    confidence_level: str
    pricing_factors: list[str]
    raw_response: str


class GeminiAnalyzer:
    """Analyzes product images using Google Gemini AI"""

    def __init__(self, api_key: str | None = None):
        """
        Initialize with Google Gemini API key

        Args:
            api_key: Google AI API key (or set GOOGLE_AI_API_KEY env var)
        """
        # Get API key from parameter or environment
        api_key = api_key or os.getenv("GOOGLE_AI_API_KEY")

        if not api_key:
            raise ValueError(
                "Google AI API key not found! "
                "Set environment variable: export GOOGLE_AI_API_KEY='your_api_key' "
                "Or get one at: https://aistudio.google.com/app/apikey"
            )

        # Initialize Gemini client
        try:
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini client: {e}") from e

    def analyze_image(self, image_path: str) -> ProductAnalysis:
        """
        Analyze a product image using Gemini AI

        Args:
            image_path: Path to the image file

        Returns:
            ProductAnalysis with AI-generated insights
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Load and prepare image
        image = Image.open(image_path)

        # Create detailed prompt for product analysis
        prompt = """
        Analyze this product image for resale purposes. Provide a detailed analysis in the following JSON format:

        {
            "product_description": "Detailed description of the item",
            "brand": "Brand name if visible/identifiable (or null if unknown)",
            "product_type": "Category/type of product (e.g., 'clothing', 'electronics', 'books')",
            "condition": "Apparent condition (e.g., 'new', 'like new', 'good', 'fair', 'poor', or null if unclear)",
            "notable_features": ["List of", "notable features", "or characteristics"],
            "market_category": "Best marketplace category for selling this item",
            "confidence_level": "How confident you are in this analysis (high/medium/low)",
            "pricing_factors": ["Factors that", "would affect", "the resale price"]
        }

        Focus on details that would help someone price this item for resale on platforms like eBay, Depop, Facebook Marketplace, or Mercari. Look for:
        - Brand names, logos, or identifying marks
        - Product model numbers or specific product lines
        - Condition indicators (wear, damage, newness)
        - Size information if visible
        - Unique features that add or detract from value
        - Material quality indicators

        Respond ONLY with valid JSON - no additional text or explanations.
        """

        try:
            # Generate analysis using Gemini
            response = self.client.models.generate_content(
                model="gemini-1.5-flash", contents=[prompt, image]
            )

            if not response.text:
                raise ValueError("Empty response from Gemini")

            # Parse JSON response (clean up any markdown formatting)
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = (
                    response_text.replace("```json", "").replace("```", "").strip()
                )

            try:
                analysis_data = json.loads(response_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, extract what we can
                analysis_data = {
                    "product_description": response.text,
                    "brand": None,
                    "product_type": "unknown",
                    "condition": None,
                    "notable_features": [],
                    "market_category": "general",
                    "confidence_level": "low",
                    "pricing_factors": [],
                }

            return ProductAnalysis(
                product_description=analysis_data.get("product_description", ""),
                brand=analysis_data.get("brand"),
                product_type=analysis_data.get("product_type", "unknown"),
                condition=analysis_data.get("condition"),
                notable_features=analysis_data.get("notable_features", []),
                market_category=analysis_data.get("market_category", "general"),
                confidence_level=analysis_data.get("confidence_level", "medium"),
                pricing_factors=analysis_data.get("pricing_factors", []),
                raw_response=response.text,
            )

        except Exception as e:
            # Return basic analysis with error info
            return ProductAnalysis(
                product_description=f"Analysis failed: {str(e)}",
                brand=None,
                product_type="unknown",
                condition=None,
                notable_features=[],
                market_category="general",
                confidence_level="low",
                pricing_factors=[],
                raw_response=str(e),
            )
