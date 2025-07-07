#!/usr/bin/env python3
"""
Vision Analyzer Script - Extract product information from photos using Google Vision API

Uses the new tool-based architecture with VisionAnalyzer from lib.analyzers.
This script provides a CLI interface for the Vision API functionality.
"""

import json
import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from lib.analyzers.vision import VisionAnalyzer


def print_analysis(analysis, image_path: str):
    """Print formatted analysis results"""
    print(f"\n🔍 Google Vision API Analysis for: {os.path.basename(image_path)}")
    print("=" * 50)

    print(f"📊 Confidence Score: {analysis.confidence_score:.2f}")

    if analysis.labels:
        print("\n🏷️ Detected Labels:")
        for label in analysis.labels[:5]:  # Show top 5
            print(f"   • {label}")

    if analysis.objects:
        print("\n📦 Detected Objects:")
        for obj in analysis.objects:
            print(f"   • {obj}")

    if analysis.brands:
        print("\n🏢 Potential Brands:")
        for brand in analysis.brands:
            print(f"   • {brand}")

    if analysis.text:
        print("\n📝 Detected Text:")
        for text in analysis.text[:3]:  # Show first 3 lines
            print(f"   • {text}")


def main():
    """Main function for command-line usage"""
    if len(sys.argv) != 2:
        print("Usage: python image_analyzer.py <image_path>")
        print("Example: python image_analyzer.py ../examples/cat.jpeg")
        sys.exit(1)

    image_path = sys.argv[1]

    # Initialize analyzer
    try:
        analyzer = VisionAnalyzer()
    except Exception as e:
        print(f"❌ Failed to initialize Vision API: {e}")
        sys.exit(1)

    try:
        # Analyze image
        print("🔄 Analyzing image with Google Vision API...")
        analysis = analyzer.analyze_image(image_path)

        # Print results
        print_analysis(analysis, image_path)

        # Save results to JSON
        os.makedirs("logs/image_analyzer", exist_ok=True)
        output_file = f"logs/image_analyzer/{Path(image_path).stem}_analysis_{int(time.time())}.json"
        with open(output_file, "w") as f:
            json.dump(
                {
                    "image_path": image_path,
                    "labels": analysis.labels,
                    "text": analysis.text,
                    "objects": analysis.objects,
                    "brands": analysis.brands,
                    "confidence_score": analysis.confidence_score,
                    "timestamp": int(time.time()),
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
