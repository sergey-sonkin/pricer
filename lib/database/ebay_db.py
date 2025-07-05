"""
eBay Database Module

SQLite database for storing eBay API results including search queries and listings.
Designed to work with the existing eBayListing and eBayPriceAnalysis dataclasses.
"""

import json
import sqlite3

# Import the dataclasses from the existing modules
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class eBayListing:
    """eBay listing data - matches the existing dataclass structure"""

    title: str
    price: float
    currency: str
    condition: str
    listing_type: str
    end_time: str | None
    sold_date: str | None
    shipping_cost: float | None
    item_url: str
    image_url: str | None
    seller_feedback: int | None

    @classmethod
    def from_any(cls, listing: Any) -> "eBayListing":
        """Convert any eBayListing-like object to database eBayListing"""
        return cls(
            title=listing.title,
            price=listing.price,
            currency=listing.currency,
            condition=listing.condition,
            listing_type=listing.listing_type,
            end_time=listing.end_time,
            sold_date=listing.sold_date,
            shipping_cost=listing.shipping_cost,
            item_url=listing.item_url,
            image_url=listing.image_url,
            seller_feedback=listing.seller_feedback,
        )


@dataclass
class eBayPriceAnalysis:
    """eBay price analysis results - matches the existing dataclass structure"""

    search_terms: str
    total_sold: int
    total_active: int
    sold_listings: list[eBayListing]
    active_listings: list[eBayListing]
    price_statistics: dict[str, float | int]
    market_insights: list[str]
    confidence_score: float

    @classmethod
    def from_any(cls, analysis: Any) -> "eBayPriceAnalysis":
        """Convert any eBayPriceAnalysis-like object to database eBayPriceAnalysis"""
        return cls(
            search_terms=analysis.search_terms,
            total_sold=analysis.total_sold,
            total_active=analysis.total_active,
            sold_listings=[
                eBayListing.from_any(listing) for listing in analysis.sold_listings
            ],
            active_listings=[
                eBayListing.from_any(listing) for listing in analysis.active_listings
            ],
            price_statistics=analysis.price_statistics,
            market_insights=analysis.market_insights,
            confidence_score=analysis.confidence_score,
        )


class eBayDatabase:
    """SQLite database manager for eBay API results"""

    def __init__(self, db_path: str = "db/ebay_data.db"):
        """
        Initialize the database connection and create tables if they don't exist

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database schema
        self._create_tables()

    def _create_tables(self):
        """Create the database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_terms TEXT NOT NULL,
                    category_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    total_active INTEGER DEFAULT 0,
                    total_sold INTEGER DEFAULT 0,
                    confidence_score REAL DEFAULT 0.0,
                    price_statistics TEXT,
                    market_insights TEXT
                );

                CREATE TABLE IF NOT EXISTS listings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    price REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    condition TEXT,
                    listing_type TEXT,
                    end_time DATETIME,
                    sold_date DATETIME,
                    shipping_cost REAL,
                    item_url TEXT UNIQUE,
                    image_url TEXT,
                    seller_feedback INTEGER,
                    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS search_listings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_id INTEGER NOT NULL,
                    listing_id INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (search_id) REFERENCES searches(id),
                    FOREIGN KEY (listing_id) REFERENCES listings(id),
                    UNIQUE(search_id, listing_id)
                );

                CREATE INDEX IF NOT EXISTS idx_searches_terms ON searches(search_terms);
                CREATE INDEX IF NOT EXISTS idx_listings_url ON listings(item_url);
                CREATE INDEX IF NOT EXISTS idx_search_listings_search ON search_listings(search_id);
                CREATE INDEX IF NOT EXISTS idx_search_listings_listing ON search_listings(listing_id);
            """)

    def store_analysis(self, analysis: Any, category_id: Optional[str] = None) -> int:
        """
        Store a complete eBay price analysis in the database

        Args:
            analysis: eBayPriceAnalysis object to store (any compatible type)
            category_id: Optional eBay category ID

        Returns:
            The ID of the stored search record
        """
        # Convert to database eBayPriceAnalysis type
        db_analysis = eBayPriceAnalysis.from_any(analysis)

        with sqlite3.connect(self.db_path) as conn:
            # Store the search record
            search_id = self._store_search(conn, db_analysis, category_id)

            # Store all listings and link them to the search
            all_listings = db_analysis.sold_listings + db_analysis.active_listings
            for listing in all_listings:
                listing_id = self._store_listing(conn, listing)
                is_active = listing in db_analysis.active_listings
                self._link_search_listing(conn, search_id, listing_id, is_active)

            return search_id

    def _store_search(
        self,
        conn: sqlite3.Connection,
        analysis: eBayPriceAnalysis,
        category_id: Optional[str],
    ) -> int:
        """Store a search record and return its ID"""
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO searches (
                search_terms, category_id, total_active, total_sold,
                confidence_score, price_statistics, market_insights
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                analysis.search_terms,
                category_id,
                analysis.total_active,
                analysis.total_sold,
                analysis.confidence_score,
                json.dumps(analysis.price_statistics),
                json.dumps(analysis.market_insights),
            ),
        )
        return cursor.lastrowid or 0

    def _store_listing(self, conn: sqlite3.Connection, listing: eBayListing) -> int:
        """Store or update a listing and return its ID"""
        cursor = conn.cursor()

        # Check if listing already exists by URL
        cursor.execute(
            "SELECT id FROM listings WHERE item_url = ?", (listing.item_url,)
        )
        existing = cursor.fetchone()

        if existing:
            # Update existing listing's last_seen timestamp
            cursor.execute(
                """
                UPDATE listings SET last_seen = CURRENT_TIMESTAMP WHERE id = ?
            """,
                (existing[0],),
            )
            return existing[0]
        else:
            # Insert new listing
            cursor.execute(
                """
                INSERT INTO listings (
                    title, price, currency, condition, listing_type,
                    end_time, sold_date, shipping_cost, item_url,
                    image_url, seller_feedback
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    listing.title,
                    listing.price,
                    listing.currency,
                    listing.condition,
                    listing.listing_type,
                    listing.end_time,
                    listing.sold_date,
                    listing.shipping_cost,
                    listing.item_url,
                    listing.image_url,
                    listing.seller_feedback,
                ),
            )
            return cursor.lastrowid or 0

    def _link_search_listing(
        self, conn: sqlite3.Connection, search_id: int, listing_id: int, is_active: bool
    ):
        """Link a search to a listing"""
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO search_listings (search_id, listing_id, is_active)
            VALUES (?, ?, ?)
        """,
            (search_id, listing_id, is_active),
        )

    def get_search_history(self, search_terms: str, limit: int = 10) -> list[dict]:
        """
        Get search history for specific search terms

        Args:
            search_terms: The search terms to look up
            limit: Maximum number of results to return

        Returns:
            List of search records as dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM searches
                WHERE search_terms = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (search_terms, limit),
            )

            return [dict(row) for row in cursor.fetchall()]

    def get_listings_for_search(
        self, search_id: int
    ) -> tuple[list[eBayListing], list[eBayListing]]:
        """
        Get active and sold listings for a specific search

        Args:
            search_id: The search ID to look up

        Returns:
            Tuple of (active_listings, sold_listings)
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT l.*, sl.is_active
                FROM listings l
                JOIN search_listings sl ON l.id = sl.listing_id
                WHERE sl.search_id = ?
            """,
                (search_id,),
            )

            active_listings = []
            sold_listings = []

            for row in cursor.fetchall():
                listing = eBayListing(
                    title=row["title"],
                    price=row["price"],
                    currency=row["currency"],
                    condition=row["condition"],
                    listing_type=row["listing_type"],
                    end_time=row["end_time"],
                    sold_date=row["sold_date"],
                    shipping_cost=row["shipping_cost"],
                    item_url=row["item_url"],
                    image_url=row["image_url"],
                    seller_feedback=row["seller_feedback"],
                )

                if row["is_active"]:
                    active_listings.append(listing)
                else:
                    sold_listings.append(listing)

            return active_listings, sold_listings

    def get_price_trends(self, search_terms: str, days: int = 30) -> dict:
        """
        Get price trends for a product over time

        Args:
            search_terms: The search terms to analyze
            days: Number of days to look back

        Returns:
            Dictionary containing price trend data
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                f"""
                SELECT
                    DATE(s.timestamp) as date,
                    AVG(l.price) as avg_price,
                    MIN(l.price) as min_price,
                    MAX(l.price) as max_price,
                    COUNT(l.id) as listing_count
                FROM searches s
                JOIN search_listings sl ON s.id = sl.search_id
                JOIN listings l ON sl.listing_id = l.id
                WHERE s.search_terms = ?
                AND s.timestamp >= datetime('now', '-{days} days')
                GROUP BY DATE(s.timestamp)
                ORDER BY date
            """,
                (search_terms,),
            )

            trends = [dict(row) for row in cursor.fetchall()]

            return {
                "search_terms": search_terms,
                "period_days": days,
                "data_points": len(trends),
                "trends": trends,
            }

    def get_database_stats(self) -> dict:
        """Get statistics about the database contents"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM searches")
            total_searches = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM listings")
            total_listings = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT search_terms) FROM searches")
            unique_search_terms = cursor.fetchone()[0]

            cursor.execute("""
                SELECT search_terms, COUNT(*) as count
                FROM searches
                GROUP BY search_terms
                ORDER BY count DESC
                LIMIT 5
            """)
            top_searches = cursor.fetchall()

            return {
                "total_searches": total_searches,
                "total_listings": total_listings,
                "unique_search_terms": unique_search_terms,
                "top_searches": top_searches,
                "database_file": str(self.db_path),
            }

    def cleanup_old_data(self, days: int = 90):
        """
        Remove old data to keep database size manageable

        Args:
            days: Keep data newer than this many days
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Remove old searches and their associated data
            cursor.execute(f"""
                DELETE FROM search_listings
                WHERE search_id IN (
                    SELECT id FROM searches
                    WHERE timestamp < datetime('now', '-{days} days')
                )
            """)

            cursor.execute(f"""
                DELETE FROM searches
                WHERE timestamp < datetime('now', '-{days} days')
            """)

            # Remove orphaned listings
            cursor.execute("""
                DELETE FROM listings
                WHERE id NOT IN (
                    SELECT DISTINCT listing_id FROM search_listings
                )
            """)

            # Vacuum to reclaim space
            cursor.execute("VACUUM")

            return cursor.rowcount
