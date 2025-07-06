"""
Google Vision API Analyzer - Extract product information from photos

Uses Google Vision API to identify products, detect text, and classify items
for pricing analysis.

This is the core analyzer class, separated from CLI functionality.
"""

import os
from dataclasses import dataclass

try:
    from google.cloud import vision
except ImportError as e:
    raise ImportError(
        f"Missing dependencies: {e}. Install with: uv add google-cloud-vision"
    ) from e


@dataclass
class VisionAnalysis:
    """Google Vision API analysis results"""

    labels: list[str]
    text: list[str]
    objects: list[str]
    brands: list[str]
    confidence_score: float
    raw_response: dict


class VisionAnalyzer:
    """Analyzes product images using Google Vision API"""

    def __init__(self, api_key_path: str | None = None):
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
            raise RuntimeError(
                f"Failed to initialize Google Vision client: {e}. "
                "Make sure you have:\n"
                "1. Created a Google Cloud project\n"
                "2. Enabled Vision API\n"
                "3. Created service account credentials\n"
                "4. Set GOOGLE_APPLICATION_CREDENTIALS environment variable"
            ) from e

    def analyze_image(self, image_path: str) -> VisionAnalysis:
        """
        Analyze a product image using Google Vision API

        Args:
            image_path: Path to the image file

        Returns:
            VisionAnalysis with extracted data
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Load image
        with open(image_path, "rb") as image_file:
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

        # Compile raw response data
        raw_response = {
            "labels_response": labels_response,
            "text_response": text_response,
            "objects_response": objects_response,
        }

        return VisionAnalysis(
            labels=labels,
            text=texts,
            objects=objects,
            brands=brands,
            confidence_score=confidence,
            raw_response=raw_response,
        )

    def _extract_brands(self, texts: list[str]) -> list[str]:
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
        self, labels: list[str], texts: list[str], objects: list[str]
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
