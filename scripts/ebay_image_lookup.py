#!/usr/bin/env python3
"""
eBay Image Lookup Script

Tests eBay Browse API's search_by_image endpoint to find similar items based on a photo.
Takes an image file path and searches eBay for visually similar products.

Usage:
    python scripts/ebay_image_lookup.py <image_path>

Example:
    python scripts/ebay_image_lookup.py examples/cat.jpeg

NOTE: This script doesn't particularly work. Unclear whether this is because of an error
in the script or if eBay's sandbox doesn't support this endpoint.
"""

import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from lib.browseapi.client import BrowseAPI
from lib.browseapi.exceptions import BrowseAPIError

# Add the parent directory to Python path so we can import from lib
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()


def encode_image_to_base64(image_path: str) -> str:
    """
    Encode an image file to base64 string for eBay API

    Args:
        image_path: Path to the image file

    Returns:
        Base64 encoded string of the image
    """
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        if len(image_data) == 0:
            raise ValueError("Image file is empty")
        encoded_string = base64.b64encode(image_data).decode("utf-8")

        # Debug: check first few characters to ensure it looks like valid base64
        print(f"Base64 starts with: {encoded_string[:50]}...")
        print(f"Base64 ends with: ...{encoded_string[-20:]}")
        print(f"Image size: {len(image_data)} bytes")

        # Check if image is too large (eBay might have size limits)
        max_size_mb = 5  # Assume 5MB limit
        if len(image_data) > max_size_mb * 1024 * 1024:
            raise ValueError(
                f"Image too large: {len(image_data)} bytes (max ~{max_size_mb}MB)"
            )

        # Validate it's valid base64
        try:
            decoded_test = base64.b64decode(encoded_string)
            print(
                f"Base64 validation successful, decoded size: {len(decoded_test)} bytes"
            )
        except Exception as e:
            raise ValueError(f"Generated invalid base64: {e}") from e

    return encoded_string


def search_ebay_by_image(image_path: str) -> dict:
    """
    Search eBay for items similar to the provided image

    Args:
        image_path: Path to the image file

    Returns:
        Dictionary containing search results and metadata
    """
    # Get eBay API credentials from environment
    use_sandbox = os.getenv("EBAY_USE_SANDBOX", "true").lower() == "true"

    if use_sandbox:
        app_id = os.getenv("EBAY_SANDBOX_APP_ID")
        cert_id = os.getenv("EBAY_SANDBOX_CERT_ID")
    else:
        app_id = os.getenv("EBAY_PROD_APP_ID")
        cert_id = os.getenv("EBAY_PROD_CERT_ID")

    if not app_id or not cert_id:
        raise ValueError(
            f"Missing eBay API credentials. Set EBAY_"
            f"{'SANDBOX' if use_sandbox else 'PROD'}_APP_ID and EBAY_"
            f"{'SANDBOX' if use_sandbox else 'PROD'}_CERT_ID"
        )

    # Encode image to base64
    print(f"Encoding image: {image_path}")
    try:
        encoded_image = encode_image_to_base64(image_path)
        print(f"Image encoded successfully ({len(encoded_image)} characters)")
    except Exception as e:
        raise ValueError(f"Failed to encode image: {e}") from e

    # Initialize eBay Browse API client
    print(
        f"Initializing eBay Browse API client "
        f"({'sandbox' if use_sandbox else 'production'})"
    )
    client = BrowseAPI(app_id=app_id, cert_id=cert_id, marketplace_id="EBAY_US")

    # Perform image search
    print("Searching eBay for similar items...")
    try:
        results = client.execute(
            method="search_by_image",
            params=[
                {
                    "image": encoded_image,
                    "limit": 20,  # Get up to 20 results
                    "sort": "price",  # Sort by price
                }
            ],
            pass_errors=True,  # Allow errors to be returned instead of raised
        )
        result = results[0]  # Get first (and only) result

        # Debug: check what we actually got back
        print(f"Result type: {type(result)}")
        if hasattr(result, "__dict__"):
            print(f"Result attributes: {list(result.__dict__.keys())}")

        # Check for warnings
        if hasattr(result, "warnings") and result.warnings:
            print("API Warnings:")
            for warning in result.warnings:
                print(f"  - Error ID: {getattr(warning, 'errorId', 'N/A')}")
                print(f"  - Message: {getattr(warning, 'message', 'N/A')}")
                print(f"  - Long Message: {getattr(warning, 'longMessage', 'N/A')}")

        return result

    except BrowseAPIError as e:
        raise Exception(f"eBay API error: {e}") from e
    except Exception as e:
        import traceback

        print(f"Full traceback:\n{traceback.format_exc()}")
        raise Exception(f"Unexpected error during search: {e}") from e


def analyze_results(results, image_path: str) -> dict:
    """
    Analyze and format the search results

    Args:
        results: Raw results from eBay API (BrowseAPIResponse object)
        image_path: Original image path for context

    Returns:
        Formatted analysis dictionary
    """
    analysis = {
        "query_info": {
            "image_path": image_path,
            "search_timestamp": datetime.now().isoformat(),
            "search_method": "eBay Browse API - search_by_image",
        },
        "results_summary": {},
        "items": [],
    }

    # Check if we got valid results and handle errors
    if hasattr(results, "errors"):
        analysis["results_summary"]["error"] = "API returned errors"
        analysis["results_summary"]["error_details"] = [
            str(error) for error in results.errors
        ]
        return analysis

    # Check if we got valid results
    if hasattr(results, "total"):
        total_count = getattr(results, "total", 0)
        analysis["results_summary"]["total_items_found"] = total_count

        # Get item summaries if they exist
        item_summaries = getattr(results, "itemSummaries", [])
        analysis["results_summary"]["items_returned"] = len(item_summaries)

        # Process individual items
        prices = []

        for item_summary in item_summaries:
            item_info = {
                "title": getattr(item_summary, "title", "N/A"),
                "item_id": getattr(item_summary, "itemId", "N/A"),
                "price": None,
                "currency": None,
                "condition": getattr(item_summary, "condition", "N/A"),
                "seller": None,
                "image_url": None,
                "item_url": getattr(item_summary, "itemWebUrl", "N/A"),
            }

            # Extract price info
            if hasattr(item_summary, "price") and item_summary.price:
                price_obj = item_summary.price
                item_info["price"] = getattr(price_obj, "value", None)
                item_info["currency"] = getattr(price_obj, "currency", "USD")
                if item_info["price"]:
                    try:
                        prices.append(float(item_info["price"]))
                    except (ValueError, TypeError):
                        pass

            # Extract seller info
            if hasattr(item_summary, "seller") and item_summary.seller:
                item_info["seller"] = getattr(item_summary.seller, "username", "N/A")

            # Extract image URL
            if hasattr(item_summary, "image") and item_summary.image:
                item_info["image_url"] = getattr(item_summary.image, "imageUrl", None)

            analysis["items"].append(item_info)

        # Calculate price statistics
        if prices:
            analysis["results_summary"]["price_stats"] = {
                "min_price": min(prices),
                "max_price": max(prices),
                "avg_price": sum(prices) / len(prices),
                "median_price": sorted(prices)[len(prices) // 2],
                "price_count": len(prices),
                "currency": "USD",  # Assuming USD for now
            }

    else:
        analysis["results_summary"]["total_items_found"] = 0
        analysis["results_summary"]["items_returned"] = 0
        analysis["results_summary"]["error"] = "No results found or API error"

        # Check for error info
        if hasattr(results, "error"):
            analysis["results_summary"]["api_error"] = str(results.error)

    return analysis


def save_results(analysis: dict, image_path: str):
    """Save analysis results to logs directory"""

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs/ebay_image_lookup")
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_name = Path(image_path).stem
    filename = f"ebay_image_lookup_{image_name}_{timestamp}.json"
    filepath = logs_dir / filename

    # Save to file
    with open(filepath, "w") as f:
        json.dump(analysis, f, indent=2)

    print(f"Results saved to: {filepath}")
    return filepath


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/ebay_image_lookup.py <image_path>")
        print("Example: python scripts/ebay_image_lookup.py examples/cat.jpeg")
        sys.exit(1)

    image_path = sys.argv[1]

    # Validate image file exists
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)

    try:
        # Perform eBay image search
        print("\n=== eBay Image Lookup ===")
        print(f"Image: {image_path}")
        print()

        results = search_ebay_by_image(image_path)

        # Analyze results
        analysis = analyze_results(results, image_path)

        # Save results
        saved_file = save_results(analysis, image_path)

        # Print summary
        print("\n=== Search Results Summary ===")
        summary = analysis["results_summary"]
        print(f"Total items found: {summary.get('total_items_found', 'N/A')}")
        print(f"Items returned: {summary.get('items_returned', 'N/A')}")

        if "price_stats" in summary:
            stats = summary["price_stats"]
            print(f"Price range: ${stats['min_price']:.2f} - ${stats['max_price']:.2f}")
            print(f"Average price: ${stats['avg_price']:.2f}")
            print(f"Median price: ${stats['median_price']:.2f}")

        if summary.get("total_items_found", 0) > 0:
            print("\n=== Sample Items ===")
            for i, item in enumerate(analysis["items"][:3]):  # Show first 3 items
                print(f"{i + 1}. {item['title']}")
                if item["price"]:
                    print(f"   Price: ${item['price']} {item['currency']}")
                print(f"   Condition: {item['condition']}")
                print(f"   Seller: {item['seller']}")
                print()

        print(f"Full results saved to: {saved_file}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
