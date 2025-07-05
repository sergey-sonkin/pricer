#!/usr/bin/env python3
"""
Test script for the eBay database functionality
"""

import os
import sys

# Add parent directory to path to import lib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.database import eBayDatabase
from lib.database.ebay_db import eBayListing, eBayPriceAnalysis


def create_test_data():
    """Create test data for database testing"""
    # Create some test listings
    test_listings = [
        eBayListing(
            title="Test iPhone 12 Pro 128GB",
            price=599.99,
            currency="USD",
            condition="Used",
            listing_type="FixedPrice",
            end_time=None,
            sold_date=None,
            shipping_cost=15.00,
            item_url="https://ebay.com/itm/123456789",
            image_url="https://example.com/image1.jpg",
            seller_feedback=98,
        ),
        eBayListing(
            title="iPhone 12 Pro 256GB Unlocked",
            price=699.99,
            currency="USD",
            condition="Excellent",
            listing_type="FixedPrice",
            end_time=None,
            sold_date=None,
            shipping_cost=0.00,
            item_url="https://ebay.com/itm/987654321",
            image_url="https://example.com/image2.jpg",
            seller_feedback=100,
        ),
        eBayListing(
            title="iPhone 12 Pro 128GB - Good Condition",
            price=549.99,
            currency="USD",
            condition="Good",
            listing_type="FixedPrice",
            end_time=None,
            sold_date="2024-01-15",
            shipping_cost=10.00,
            item_url="https://ebay.com/itm/456789123",
            image_url="https://example.com/image3.jpg",
            seller_feedback=95,
        ),
    ]

    # Create test analysis
    test_analysis = eBayPriceAnalysis(
        search_terms="iPhone 12 Pro",
        total_sold=1,
        total_active=2,
        sold_listings=[test_listings[2]],  # The sold one
        active_listings=[test_listings[0], test_listings[1]],  # The active ones
        price_statistics={
            "sold_min": 549.99,
            "sold_max": 549.99,
            "sold_avg": 549.99,
            "sold_median": 549.99,
            "sold_count": 1,
            "active_min": 599.99,
            "active_max": 699.99,
            "active_avg": 649.99,
            "active_median": 649.99,
            "active_count": 2,
        },
        market_insights=[
            "Found 2 active listings",
            "Average listing price: $649.99",
            "Most common condition: Used",
        ],
        confidence_score=0.75,
    )

    return test_analysis


def test_database_functionality():
    """Test all database functions"""
    print("🧪 Testing eBay Database Functionality")
    print("=" * 50)

    # Initialize database
    db = eBayDatabase("test_db/test_ebay_data.db")

    # Test 1: Store analysis
    print("\n1. Testing store_analysis()...")
    test_analysis = create_test_data()
    search_id = db.store_analysis(test_analysis, "9355")
    print(f"✅ Stored analysis with search ID: {search_id}")

    # Test 2: Get search history
    print("\n2. Testing get_search_history()...")
    history = db.get_search_history("iPhone 12 Pro")
    print(f"✅ Found {len(history)} search records")
    if history:
        print(f"   Latest search: {history[0]['timestamp']}")

    # Test 3: Get listings for search
    print("\n3. Testing get_listings_for_search()...")
    active_listings, sold_listings = db.get_listings_for_search(search_id)
    print(
        f"✅ Found {len(active_listings)} active listings, {len(sold_listings)} sold listings"
    )

    # Test 4: Get price trends
    print("\n4. Testing get_price_trends()...")
    trends = db.get_price_trends("iPhone 12 Pro")
    print(f"✅ Found {trends['data_points']} data points for price trends")

    # Test 5: Get database stats
    print("\n5. Testing get_database_stats()...")
    stats = db.get_database_stats()
    print("✅ Database contains:")
    print(f"   - {stats['total_searches']} searches")
    print(f"   - {stats['total_listings']} listings")
    print(f"   - {stats['unique_search_terms']} unique search terms")

    # Test 6: Store duplicate analysis (should update existing listings)
    print("\n6. Testing duplicate handling...")
    search_id2 = db.store_analysis(test_analysis, "9355")
    print(f"✅ Stored duplicate analysis with search ID: {search_id2}")

    # Check stats again
    stats2 = db.get_database_stats()
    print(
        f"   After duplicate: {stats2['total_searches']} searches, {stats2['total_listings']} listings"
    )

    print("\n🎉 All tests completed successfully!")
    print(f"📄 Database file: {db.db_path}")

    return db


def test_with_real_data():
    """Test with real eBay API data if available"""
    print("\n🔍 Testing with Real eBay API Data")
    print("=" * 50)

    try:
        # Try to use the real eBay API researcher
        from scripts.ebay_api_researcher import eBayAPIResearcher

        researcher = eBayAPIResearcher()
        analysis = researcher.research_product("test item", None)

        # Store in database
        db = eBayDatabase("test_db/test_ebay_data.db")
        search_id = db.store_analysis(analysis, None)

        print(f"✅ Successfully stored real API data with search ID: {search_id}")

    except Exception as e:
        print(f"⚠️ Could not test with real API data: {e}")
        print("   (This is expected if eBay API credentials are not configured)")


if __name__ == "__main__":
    # Run tests
    db = test_database_functionality()

    # Test with real data if user wants
    if len(sys.argv) > 1 and sys.argv[1] == "--real":
        test_with_real_data()

    print("\n📋 To view database contents:")
    print(f"   sqlite3 {db.db_path}")
    print("   .tables")
    print("   SELECT * FROM searches;")
    print("   SELECT * FROM listings;")
