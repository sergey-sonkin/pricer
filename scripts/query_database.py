#!/usr/bin/env python3
"""
Query eBay Database - Utility script for viewing stored eBay data
"""

import argparse
import os
import sys

# Add parent directory to path to import lib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.database import eBayDatabase


def show_database_stats(db):
    """Display database statistics"""
    stats = db.get_database_stats()

    print("📊 Database Statistics")
    print("=" * 50)
    print(f"Total searches: {stats['total_searches']}")
    print(f"Total listings: {stats['total_listings']}")
    print(f"Unique search terms: {stats['unique_search_terms']}")
    print(f"Database file: {stats['database_file']}")

    if stats["top_searches"]:
        print("\nTop searched terms:")
        for term, count in stats["top_searches"]:
            print(f"  • {term}: {count} searches")


def show_search_history(db, search_terms=None, limit=10):
    """Display search history"""
    if search_terms:
        print(f"📋 Search History for: {search_terms}")
        history = db.get_search_history(search_terms, limit)
    else:
        print("📋 Recent Search History")
        # Get all recent searches
        import sqlite3

        with sqlite3.connect(db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM searches
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (limit,),
            )
            history = [dict(row) for row in cursor.fetchall()]

    print("=" * 50)

    if not history:
        print("No search history found.")
        return

    for record in history:
        print(f"\n🔍 Search ID: {record['id']}")
        print(f"   Terms: {record['search_terms']}")
        print(f"   Date: {record['timestamp']}")
        print(
            f"   Results: {record['total_active']} active, {record['total_sold']} sold"
        )
        print(f"   Confidence: {record['confidence_score']:.2f}")
        if record["category_id"]:
            print(f"   Category: {record['category_id']}")


def show_price_trends(db, search_terms, days=30):
    """Display price trends for a product"""
    trends = db.get_price_trends(search_terms, days)

    print(f"📈 Price Trends for: {search_terms}")
    print("=" * 50)
    print(f"Period: {days} days")
    print(f"Data points: {trends['data_points']}")

    if not trends["trends"]:
        print("No price trend data found.")
        return

    print("\nDaily Price Data:")
    for trend in trends["trends"]:
        print(
            f"  {trend['date']}: ${trend['avg_price']:.2f} avg "
            f"(${trend['min_price']:.2f}-${trend['max_price']:.2f}, "
            f"{trend['listing_count']} listings)"
        )


def show_listings_for_search(db, search_id):
    """Display listings for a specific search"""
    active_listings, sold_listings = db.get_listings_for_search(search_id)

    print(f"📦 Listings for Search ID: {search_id}")
    print("=" * 50)

    if active_listings:
        print(f"\n🛒 Active Listings ({len(active_listings)}):")
        for i, listing in enumerate(active_listings, 1):
            print(f"  {i}. ${listing.price:.2f} - {listing.title[:60]}...")
            print(f"     Condition: {listing.condition}, URL: {listing.item_url}")

    if sold_listings:
        print(f"\n💰 Sold Listings ({len(sold_listings)}):")
        for i, listing in enumerate(sold_listings, 1):
            print(f"  {i}. ${listing.price:.2f} - {listing.title[:60]}...")
            print(f"     Condition: {listing.condition}, Sold: {listing.sold_date}")


def cleanup_old_data(db, days=90):
    """Clean up old data from the database"""
    print(f"🧹 Cleaning up data older than {days} days...")

    # Get stats before cleanup
    stats_before = db.get_database_stats()

    # Perform cleanup
    rows_deleted = db.cleanup_old_data(days)

    # Get stats after cleanup
    stats_after = db.get_database_stats()

    print("✅ Cleanup completed")
    print(
        f"   Searches: {stats_before['total_searches']} → {stats_after['total_searches']}"
    )
    print(
        f"   Listings: {stats_before['total_listings']} → {stats_after['total_listings']}"
    )
    print(f"   Rows deleted: {rows_deleted}")


def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(description="Query eBay Database")
    parser.add_argument("--db", default="db/ebay_data.db", help="Database file path")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Stats command
    subparsers.add_parser("stats", help="Show database statistics")

    # History command
    history_parser = subparsers.add_parser("history", help="Show search history")
    history_parser.add_argument("--terms", help="Filter by search terms")
    history_parser.add_argument(
        "--limit", type=int, default=10, help="Limit number of results"
    )

    # Trends command
    trends_parser = subparsers.add_parser("trends", help="Show price trends")
    trends_parser.add_argument("terms", help="Search terms to analyze")
    trends_parser.add_argument(
        "--days", type=int, default=30, help="Number of days to analyze"
    )

    # Listings command
    listings_parser = subparsers.add_parser(
        "listings", help="Show listings for a search"
    )
    listings_parser.add_argument(
        "search_id", type=int, help="Search ID to show listings for"
    )

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old data")
    cleanup_parser.add_argument(
        "--days", type=int, default=90, help="Keep data newer than this many days"
    )

    args = parser.parse_args()

    # Initialize database
    db = eBayDatabase(args.db)

    # Execute commands
    if args.command == "stats":
        show_database_stats(db)
    elif args.command == "history":
        show_search_history(db, args.terms, args.limit)
    elif args.command == "trends":
        show_price_trends(db, args.terms, args.days)
    elif args.command == "listings":
        show_listings_for_search(db, args.search_id)
    elif args.command == "cleanup":
        cleanup_old_data(db, args.days)
    else:
        # Default: show stats
        show_database_stats(db)


if __name__ == "__main__":
    main()
