#!/usr/bin/env python3
"""
Image Analyzer - Extract product information from photos

Uses Google Vision API to identify products, detect text, and classify items
for pricing analysis.
"""

import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

try:
    import io

    from google.cloud import vision
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: uv add google-cloud-vision pillow")
    sys.exit(1)


@dataclass
class ProductInfo:
    """Information extracted from product image"""

    labels: List[str]
    text: List[str]
    objects: List[str]
    brands: List[str]
    confidence_score: float


class ImageAnalyzer:
    """Analyzes product images using Google Vision API"""

    def __init__(self, api_key_path: Optional[str] = None):
        """
        Initialize with Google Vision API credentials

        Args:
            api_key_path: Path to service account JSON file
        """
        if api_key_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = api_key_path

        try:
            self.client = vision.ImageAnnotatorClient()
        except Exception as e:
            print(f"Failed to initialize Google Vision client: {e}")
            print("Make sure you have:")
            print("1. Created a Google Cloud project")
            print("2. Enabled Vision API")
            print("3. Created service account credentials")
            print("4. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
            sys.exit(1)

    def analyze_image(self, image_path: str) -> ProductInfo:
        """
        Analyze a product image and extract information

        Args:
            image_path: Path to the image file

        Returns:
            ProductInfo with extracted data
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Load image
        with io.open(image_path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        # Detect labels (general object detection)
        labels_response = self.client.annotate_image(
            {
                "image": image,
                "features": [{"type_": vision.Feature.Type.LABEL_DETECTION}],
            }
        )
        labels = [label.description for label in labels_response.label_annotations]

        # Detect text
        text_response = self.client.annotate_image(
            {
                "image": image,
                "features": [{"type_": vision.Feature.Type.TEXT_DETECTION}],
            }
        )
        texts = []
        if text_response.text_annotations:
            # First annotation contains all detected text
            full_text = text_response.text_annotations[0].description
            texts = [line.strip() for line in full_text.split("\n") if line.strip()]

        # Detect objects
        objects_response = self.client.annotate_image(
            {
                "image": image,
                "features": [{"type_": vision.Feature.Type.OBJECT_LOCALIZATION}],
            }
        )
        objects = [obj.name for obj in objects_response.localized_object_annotations]

        # Extract potential brands from text
        brands = self._extract_brands(texts)

        # Calculate confidence score
        confidence = self._calculate_confidence(labels, texts, objects)

        return ProductInfo(
            labels=labels,
            text=texts,
            objects=objects,
            brands=brands,
            confidence_score=confidence,
        )

    def _extract_brands(self, texts: List[str]) -> List[str]:
        """Extract potential brand names from detected text"""
        # Common brand indicators
        brand_indicators = ["®", "™", "©"]
        potential_brands = []

        for text in texts:
            # Look for trademark symbols
            if any(indicator in text for indicator in brand_indicators):
                potential_brands.append(text.strip())

            # Look for all-caps words (often brands)
            words = text.split()
            for word in words:
                if (
                    len(word) > 2
                    and word.isupper()
                    and word.isalpha()
                    and word not in ["THE", "AND", "FOR", "WITH"]
                ):
                    potential_brands.append(word)

        return list(set(potential_brands))

    def _calculate_confidence(
        self, labels: List[str], texts: List[str], objects: List[str]
    ) -> float:
        """Calculate confidence score based on detected information"""
        score = 0.0

        # More labels = higher confidence
        score += min(len(labels) * 0.1, 0.5)

        # Detected text adds confidence
        score += min(len(texts) * 0.05, 0.3)

        # Object detection adds confidence
        score += min(len(objects) * 0.1, 0.2)

        return min(score, 1.0)


    def print_analysis(self, product_info: ProductInfo, image_path: str):
        """Print formatted analysis results"""
        print(f"\n🔍 Analysis Results for: {os.path.basename(image_path)}")
        print("=" * 50)

        print(f"📊 Confidence Score: {product_info.confidence_score:.2f}")

        if product_info.labels:
            print("\n🏷️  Detected Labels:")
            for label in product_info.labels[:5]:  # Show top 5
                print(f"   • {label}")

        if product_info.objects:
            print("\n📦 Detected Objects:")
            for obj in product_info.objects:
                print(f"   • {obj}")

        if product_info.brands:
            print("\n🏢 Potential Brands:")
            for brand in product_info.brands:
                print(f"   • {brand}")

        if product_info.text:
            print("\n📝 Detected Text:")
            for text in product_info.text[:3]:  # Show first 3 lines
                print(f"   • {text}")


def main():
    """Main function for command-line usage"""
    if len(sys.argv) != 2:
        print("Usage: python image_analyzer.py <image_path>")
        print("Example: python image_analyzer.py ../examples/shirt.jpg")
        sys.exit(1)

    image_path = sys.argv[1]

    # Initialize analyzer
    analyzer = ImageAnalyzer()

    try:
        # Analyze image
        print("🔄 Analyzing image...")
        product_info = analyzer.analyze_image(image_path)

        # Print results
        analyzer.print_analysis(product_info, image_path)

        # Save results to JSON
        os.makedirs('logs/image_analyzer', exist_ok=True)
        output_file = f"logs/image_analyzer/{Path(image_path).stem}_analysis_{int(time.time())}.json"
        with open(output_file, "w") as f:
            json.dump(
                {
                    "image_path": image_path,
                    "labels": product_info.labels,
                    "text": product_info.text,
                    "objects": product_info.objects,
                    "brands": product_info.brands,
                    "confidence_score": product_info.confidence_score,
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
