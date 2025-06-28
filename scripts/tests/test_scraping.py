#!/usr/bin/env python3
"""
Test script to check if we can access various pricing websites
"""

import requests
from bs4 import BeautifulSoup


def test_site_access():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Test eBay access
    print("🧪 Testing eBay access...")
    try:
        url = "https://www.ebay.com/sch/i.html?_nkw=test"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        print(f"   Status: {response.status_code}")
        print(f"   Title: {soup.title.string if soup.title else 'No title'}")

        # Check for common eBay elements
        items = soup.find_all("div", class_="s-item__wrapper")
        print(f"   Found {len(items)} items with 's-item__wrapper' class")

        # Try different selectors
        alt_items = soup.find_all("div", {"data-view": "mi:1686|iid:1"})
        print(f"   Found {len(alt_items)} items with data-view selector")

        # Look for any item containers
        all_divs = soup.find_all("div", class_=lambda x: x and "item" in x.lower())
        print(f"   Found {len(all_divs)} divs with 'item' in class name")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    print()

    # Test a simple product search
    print("🧪 Testing specific product search...")
    try:
        url = "https://www.ebay.com/sch/i.html?_nkw=iphone+case&LH_Sold=1&LH_Complete=1"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        print(f"   Status: {response.status_code}")

        # Debug: Print first few div classes to see structure
        divs = soup.find_all("div", class_=True)[:10]
        print("   First 10 div classes found:")
        for i, div in enumerate(divs):
            classes = div.get("class", [])
            print(f"     {i+1}. {' '.join(classes[:3])}...")  # Show first 3 classes

    except Exception as e:
        print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    test_site_access()
