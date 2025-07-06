"""
OpenAI Analyzer - AI-powered product identification from photos

Uses OpenAI Vision API to analyze product images and provide intelligent
product descriptions, brand identification, and market insights.

This is the core analyzer class, separated from CLI functionality.
"""

import base64
import json
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI


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


class OpenAIAnalyzer:
    """Analyzes product images using OpenAI Vision API"""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        """
        Initialize with OpenAI API key

        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: OpenAI model to use (gpt-4o, gpt-4o-mini, gpt-4-vision-preview)
        """
        # Get API key from parameter or environment
        load_dotenv()
        api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OpenAI API key not found! "
                "Set environment variable: export OPENAI_API_KEY='your_api_key' "
                "Or get one at: https://platform.openai.com/api-keys"
            )

        # Initialize OpenAI client
        try:
            self.client = OpenAI(api_key=api_key)
            self.model = model
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI client: {e}") from e

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 for OpenAI API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def analyze_image(self, image_path: str) -> ProductAnalysis:
        """
        Analyze a product image using OpenAI Vision

        Args:
            image_path: Path to the image file

        Returns:
            ProductAnalysis with AI-generated insights
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Encode image for API
        base64_image = self._encode_image(image_path)

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
            # Generate analysis using OpenAI Vision
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=1000,
            )

            if not response.choices or not response.choices[0].message.content:
                raise ValueError("Empty response from OpenAI")

            # Parse JSON response (clean up any markdown formatting)
            response_text = response.choices[0].message.content.strip()
            if response_text.startswith("```json"):
                response_text = (
                    response_text.replace("```json", "").replace("```", "").strip()
                )

            try:
                analysis_data = json.loads(response_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, extract what we can
                analysis_data = {
                    "product_description": response_text,
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
                raw_response=response_text,
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
