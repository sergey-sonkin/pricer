#!/usr/bin/env python3
"""
OpenAI Analyzer CLI - Command-line interface for AI-powered product identification

CLI wrapper around the OpenAIAnalyzer library class.
Uses OpenAI Vision API to analyze product images and provide intelligent
product descriptions, brand identification, and market insights.
"""

import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from lib.analyzers import OpenAIAnalyzer, ProductAnalysis

load_dotenv()

# Add parent directory to path to import lib
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


def print_analysis(analysis: ProductAnalysis, image_path: str):
    """Print formatted analysis results"""
    print(f"\n🤖 OpenAI Vision Analysis for: {os.path.basename(image_path)}")
    print("=" * 50)

    print(f"🎯 Confidence Level: {analysis.confidence_level.title()}")

    print("\n📝 Product Description:")
    print(f"   {analysis.product_description}")

    print(f"\n📦 Product Type: {analysis.product_type.title()}")
    print(f"🏪 Market Category: {analysis.market_category.title()}")

    if analysis.brand:
        print(f"🏢 Brand: {analysis.brand}")

    if analysis.condition:
        print(f"⭐ Condition: {analysis.condition.title()}")

    if analysis.notable_features:
        print("\n✨ Notable Features:")
        for feature in analysis.notable_features:
            print(f"   • {feature}")

    if analysis.pricing_factors:
        print("\n💰 Pricing Factors:")
        for factor in analysis.pricing_factors:
            print(f"   • {factor}")


def main():
    """Main function for command-line usage"""
    if len(sys.argv) != 2:
        print("Usage: uv run scripts/openai_analyzer.py <image_path>")
        print("Example: uv run scripts/openai_analyzer.py examples/cat.jpeg")
        print("\nMake sure to set OPENAI_API_KEY environment variable")
        sys.exit(1)

    image_path = sys.argv[1]

    try:
        # Initialize analyzer
        print("🔄 Initializing OpenAI Vision...")
        analyzer = OpenAIAnalyzer()

        # Analyze image
        print("🧠 Analyzing image with AI...")
        analysis = analyzer.analyze_image(image_path)

        # Print results
        print_analysis(analysis, image_path)

        # Save results to JSON
        os.makedirs("logs/openai_analyzer", exist_ok=True)
        output_file = f"logs/openai_analyzer/{Path(image_path).stem}_openai_analysis_{int(time.time())}.json"
        with open(output_file, "w") as f:
            json.dump(
                {
                    "image_path": image_path,
                    "product_description": analysis.product_description,
                    "brand": analysis.brand,
                    "product_type": analysis.product_type,
                    "condition": analysis.condition,
                    "notable_features": analysis.notable_features,
                    "market_category": analysis.market_category,
                    "confidence_level": analysis.confidence_level,
                    "pricing_factors": analysis.pricing_factors,
                    "raw_response": analysis.raw_response,
                },
                f,
                indent=2,
            )

        print(f"\n💾 Results saved to: {output_file}")

    except Exception as e:
        print(f"❌ Error analyzing image: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
