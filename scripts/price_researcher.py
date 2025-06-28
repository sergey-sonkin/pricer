#!/usr/bin/env python3
"""
Price Researcher - Find market pricing data for products

Uses web scraping to research pricing for identified products.
Provides price ranges, market trends, and comparable listings.
"""

import json
import os
import random
import re
import sys
import time
from dataclasses import dataclass
from urllib.parse import quote

try:
    import requests
    from bs4 import BeautifulSoup
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: uv add requests beautifulsoup4 python-dotenv")
    sys.exit(1)


@dataclass
class PriceData:
    """Pricing information for a product"""

    source: str
    title: str
    price: float
    condition: str | None
    sold_date: str | None
    url: str | None
    shipping: float | None = None


@dataclass
class PriceAnalysis:
    """Complete price analysis results"""

    search_terms: str
    total_results: int
    price_range: dict[str, float]  # min, max, average, median
    recent_sales: list[PriceData]
    price_trends: dict[str, str]
    recommendations: list[str]
    confidence_score: float


class PriceResearcher:
    """Research market pricing for products"""

    def __init__(self):
        """Initialize the price researcher"""
        load_dotenv()

        # Headers for web scraping (rotate user agents)
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        ]

    def research_pricing(
        self,
        product_description: str,
        product_type: str | None = None,
        brand: str | None = None,
        condition: str | None = None,
    ) -> PriceAnalysis:
        """Research pricing for a product"""
        search_terms = self._build_search_terms(
            product_description, product_type, brand
        )
        print(f"🔍 Searching for: {search_terms}")

        # Collect pricing data from multiple sources
        all_price_data = []
        all_price_data.extend(self._scrape_ebay_sold(search_terms))
        all_price_data.extend(self._scrape_ebay_current(search_terms))
        all_price_data.extend(self._scrape_google_shopping(search_terms))

        return self._analyze_pricing_data(search_terms, all_price_data, condition)

    # ===== UTILITY METHODS =====

    def _build_search_terms(
        self,
        description: str,
        product_type: str | None = None,
        brand: str | None = None,
    ) -> str:
        """Build effective search terms from product info"""
        terms = []

        if brand and brand.lower() != "null":
            terms.append(brand)

        # Remove common stop words and focus on product-specific terms
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "used",
            "good",
            "condition",
        }
        words = description.lower().split()
        key_words = [word for word in words if word not in stop_words and len(word) > 2]
        terms.extend(key_words[:4])  # Take the most relevant words

        return " ".join(terms)

    def _get_headers(self):
        """Get randomized headers for requests"""
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def _make_request(self, url: str, max_retries: int = 3):
        """Make HTTP request with retry logic"""
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    delay = random.uniform(2, 5)
                    print(f"    ⏳ Retrying in {delay:.1f}s...")
                    time.sleep(delay)

                headers = self._get_headers()
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                return response

            except requests.exceptions.Timeout:
                print(f"    ⏱️ Timeout (attempt {attempt + 1}/{max_retries})")
            except requests.exceptions.RequestException as e:
                print(
                    f"    ❌ Request failed (attempt {attempt + 1}/{max_retries}): {e}"
                )

            if attempt == max_retries - 1:
                print("    ❌ All attempts failed")
                return None

        return None

    def _extract_price_from_text(self, text: str) -> float | None:
        """Extract price from text using regex"""
        price_match = re.search(r"\$[\d,]+\.?\d*", text)
        if price_match:
            try:
                price = float(price_match.group().replace("$", "").replace(",", ""))
                return price if 1 <= price <= 10000 else None  # Reasonable price range
            except ValueError:
                pass
        return None

    def _extract_title_and_price_from_item(
        self, item, search_terms: str
    ) -> tuple[str, float | None]:
        """Extract title and price from a BeautifulSoup item element"""
        # Extract title
        title_selectors = [
            'span[role="heading"]',
            "h3.s-item__title",
            ".s-item__title",
            "a.s-item__link span",
            ".s-item__title-label",
            "h3 span",
            ".s-item__title span",
        ]

        title = None
        for selector in title_selectors:
            title_elem = item.select_one(selector)
            if title_elem and title_elem.get_text(strip=True):
                title = title_elem.get_text(strip=True)
                if title.lower() not in ["shop on ebay", "", "new listing"]:
                    break

        if not title or title.lower() in ["shop on ebay", "", "new listing"]:
            title = f"{search_terms} - eBay Listing"

        # Extract price
        price_selectors = [
            "span.notranslate",
            ".s-item__price",
            "span.s-item__price",
            ".price",
            '[data-testid="price"]',
            'span[aria-hidden="true"]',
            ".notranslate",
            ".s-item__detail--primary span",
        ]

        price = None
        for selector in price_selectors:
            price_elems = item.select(selector)
            for price_elem in price_elems:
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = self._extract_price_from_text(price_text)
                    if price:
                        break
            if price:
                break

        # Fallback: search entire item HTML for price patterns
        if not price:
            item_html = str(item)
            price_matches = re.findall(r"\$[\d,]+\.?\d*", item_html)
            for price_str in price_matches:
                price = self._extract_price_from_text(price_str)
                if price:
                    break

        return title, price

    # ===== SCRAPING METHODS =====

    def _scrape_ebay_sold(
        self, search_terms: str, max_results: int = 20
    ) -> list[PriceData]:
        """Scrape eBay sold listings for pricing data"""
        results = []

        try:
            encoded_terms = quote(search_terms)
            url = f"https://www.ebay.com/sch/i.html?_nkw={encoded_terms}&_sacat=0&LH_Sold=1&LH_Complete=1&_sop=13"

            print("  📦 Checking eBay sold listings...")
            response = self._make_request(url)
            if not response:
                return results

            soup = BeautifulSoup(response.content, "html.parser")
            print(
                f"  🔍 Response: {response.status_code}, HTML length: {len(response.content)}"
            )

            # Find items using multiple selectors
            items = []
            selectors = [
                "div.s-item__wrapper",
                "div.s-item",
                'div[data-view="mi:1686|iid:1"]',
                ".srp-results .s-item",
            ]

            for selector in selectors:
                items = soup.select(selector)
                if items:
                    print(f"  ✅ Found {len(items)} items with selector: {selector}")
                    break

            if not items:
                # Fallback: look for any div with price-like content
                all_divs = soup.find_all("div")
                print(f"  🔍 Total divs found: {len(all_divs)}")

                # Look for price patterns in the HTML
                price_pattern = re.compile(r"\$[\d,]+\.?\d*")
                price_matches = price_pattern.findall(response.text)
                if price_matches:
                    print(f"  💰 Found price patterns: {price_matches[:5]}")
                    # Create basic results from price patterns
                    for i, price_str in enumerate(price_matches[:5]):
                        try:
                            price = float(price_str.replace("$", "").replace(",", ""))
                            if price > 0:
                                results.append(
                                    PriceData(
                                        source="eBay Sold",
                                        title=f"{search_terms} - eBay Result {i + 1}",
                                        price=price,
                                        condition="used",
                                        sold_date=None,
                                        url=url,
                                    )
                                )
                        except ValueError:
                            continue
                    return results

            # Process items with detailed logging
            for i, item in enumerate(items[:max_results]):
                try:
                    print(f"  🔍 Processing item {i + 1}...")
                    title, price = self._extract_title_and_price_from_item(
                        item, search_terms
                    )

                    if price:
                        print(f"    ✅ Found price: ${price}")
                    else:
                        print(f"    ❌ No price found for item {i + 1}, skipping")
                        continue

                    # Extract additional info
                    sold_elem = item.select_one(
                        "span.POSITIVE, .s-item__sold-date, .s-item__ended-date"
                    )
                    sold_date = sold_elem.get_text(strip=True) if sold_elem else None

                    link_elem = item.select_one(
                        'a.s-item__link, a[href*="ebay.com/itm"]'
                    )
                    item_url = (
                        str(link_elem.get("href"))
                        if link_elem and link_elem.get("href")
                        else None
                    )

                    results.append(
                        PriceData(
                            source="eBay Sold",
                            title=title,
                            price=price,
                            condition="used",
                            sold_date=sold_date,
                            url=item_url,
                        )
                    )

                    print(f"  ✅ Extracted: {title[:50]}... - ${price}")

                except Exception as e:
                    print(f"  ❌ Error parsing item {i + 1}: {e}")
                    continue

        except Exception as e:
            print(f"  ❌ Error scraping eBay sold listings: {e}")

        print(f"  ✅ Found {len(results)} eBay sold listings")
        return results

    def _scrape_ebay_current(
        self, search_terms: str, max_results: int = 10
    ) -> list[PriceData]:
        """Scrape current eBay listings for market context"""
        results = []

        try:
            encoded_terms = quote(search_terms)
            url = (
                f"https://www.ebay.com/sch/i.html?_nkw={encoded_terms}&_sacat=0&_sop=15"
            )

            print("  🛒 Checking current eBay listings...")
            response = self._make_request(url)
            if not response:
                return results

            soup = BeautifulSoup(response.content, "html.parser")
            items = soup.select("div.s-item__wrapper")[:max_results]

            for item in items:
                try:
                    title, price = self._extract_title_and_price_from_item(
                        item, search_terms
                    )

                    if not price:
                        continue

                    link_elem = item.select_one("a.s-item__link")
                    item_url = (
                        str(link_elem.get("href"))
                        if link_elem and link_elem.get("href")
                        else None
                    )

                    results.append(
                        PriceData(
                            source="eBay Current",
                            title=title,
                            price=price,
                            condition="mixed",
                            sold_date=None,
                            url=item_url,
                        )
                    )

                except Exception:
                    continue

        except Exception as e:
            print(f"  ❌ Error scraping current eBay listings: {e}")

        print(f"  ✅ Found {len(results)} current eBay listings")
        return results

    def _scrape_google_shopping(
        self, search_terms: str, max_results: int = 5
    ) -> list[PriceData]:
        """Search Google Shopping for price references"""
        results = []

        try:
            encoded_terms = quote(search_terms)
            url = f"https://www.google.com/search?tbm=shop&q={encoded_terms}"

            print("  🛍️  Checking Google Shopping...")
            response = self._make_request(url)
            if not response:
                return results

            soup = BeautifulSoup(response.content, "html.parser")
            price_elements = soup.find_all("span", class_="a8Pemb")[:max_results]

            for price_elem in price_elements:
                try:
                    price_text = price_elem.get_text(strip=True)
                    price = self._extract_price_from_text(price_text)

                    if price:
                        results.append(
                            PriceData(
                                source="Google Shopping",
                                title=search_terms,
                                price=price,
                                condition="new",
                                sold_date=None,
                                url=None,
                            )
                        )
                except Exception:
                    continue

        except Exception as e:
            print(f"  ❌ Error searching Google Shopping: {e}")

        print(f"  ✅ Found {len(results)} Google Shopping results")
        return results

    # ===== ANALYSIS METHODS =====

    def _analyze_pricing_data(
        self,
        search_terms: str,
        price_data: list[PriceData],
        condition: str | None = None,
    ) -> PriceAnalysis:
        """Analyze collected pricing data and generate insights"""

        if not price_data:
            return PriceAnalysis(
                search_terms=search_terms,
                total_results=0,
                price_range={"min": 0, "max": 0, "average": 0, "median": 0},
                recent_sales=[],
                price_trends={"trend": "insufficient_data"},
                recommendations=["No pricing data found. Try different search terms."],
                confidence_score=0.0,
            )

        # Calculate price statistics
        prices = [item.price for item in price_data if item.price > 0]
        price_range = {
            "min": min(prices) if prices else 0,
            "max": max(prices) if prices else 0,
            "average": sum(prices) / len(prices) if prices else 0,
            "median": sorted(prices)[len(prices) // 2] if prices else 0,
        }

        # Generate insights
        recommendations = self._generate_recommendations(
            price_data, price_range, condition
        )
        confidence = self._calculate_confidence(price_data)
        recent_sales = [item for item in price_data if item.source == "eBay Sold"][:10]

        return PriceAnalysis(
            search_terms=search_terms,
            total_results=len(price_data),
            price_range=price_range,
            recent_sales=recent_sales,
            price_trends={"trend": "stable"},
            recommendations=recommendations,
            confidence_score=confidence,
        )

    def _generate_recommendations(
        self,
        price_data: list[PriceData],
        price_range: dict[str, float],
        condition: str | None,
    ) -> list[str]:
        """Generate pricing recommendations based on data"""
        recommendations = []
        avg_price = price_range["average"]
        sold_items = [item for item in price_data if item.source == "eBay Sold"]
        current_items = [item for item in price_data if item.source == "eBay Current"]

        if avg_price > 0:
            if condition and "good" in condition.lower():
                rec_price = avg_price * 0.8
                recommendations.append(
                    f"For good condition, consider pricing around ${rec_price:.2f}"
                )
            else:
                recommendations.append(f"Average market price: ${avg_price:.2f}")

        if sold_items and current_items:
            sold_avg = sum(item.price for item in sold_items) / len(sold_items)
            current_avg = sum(item.price for item in current_items) / len(current_items)

            if current_avg > sold_avg * 1.2:
                recommendations.append(
                    "Current listings are priced high - consider competitive pricing"
                )
            elif current_avg < sold_avg * 0.8:
                recommendations.append(
                    "Market may be soft - consider waiting or pricing aggressively"
                )

        if len(sold_items) >= 5:
            recommendations.append(
                "Good market data available - pricing confidence is high"
            )
        else:
            recommendations.append(
                "Limited sales data - consider researching similar items"
            )

        return recommendations

    def _calculate_confidence(self, price_data: list[PriceData]) -> float:
        """Calculate confidence score based on available data"""
        sold_count = len([item for item in price_data if item.source == "eBay Sold"])
        total_count = len(price_data)

        confidence = 0.0
        confidence += min(sold_count * 0.15, 0.6)  # Sold listings are most valuable
        confidence += min(total_count * 0.05, 0.3)  # Total data points

        return min(confidence, 1.0)

    def print_analysis(self, analysis: PriceAnalysis):
        """Print formatted price analysis"""
        print(f"\n💰 Price Analysis for: {analysis.search_terms}")
        print("=" * 50)
        print(f"📊 Confidence Score: {analysis.confidence_score:.2f}")
        print(f"📈 Total Results Found: {analysis.total_results}")

        if analysis.price_range["average"] > 0:
            print("\n💵 Price Range:")
            print(f"   • Low: ${analysis.price_range['min']:.2f}")
            print(f"   • High: ${analysis.price_range['max']:.2f}")
            print(f"   • Average: ${analysis.price_range['average']:.2f}")
            print(f"   • Median: ${analysis.price_range['median']:.2f}")

        if analysis.recent_sales:
            print("\n🏷️  Recent Sales:")
            for sale in analysis.recent_sales[:5]:
                print(f"   • ${sale.price:.2f} - {sale.title[:50]}...")

        if analysis.recommendations:
            print("\n💡 Recommendations:")
            for rec in analysis.recommendations:
                print(f"   • {rec}")


def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print(
            "Usage: python price_researcher.py <product_description> [brand] [condition]"
        )
        print('Example: python price_researcher.py "cat litter box" "Petmate" "good"')
        sys.exit(1)

    product_description = sys.argv[1]
    brand = sys.argv[2] if len(sys.argv) > 2 else None
    condition = sys.argv[3] if len(sys.argv) > 3 else None

    # Initialize researcher
    researcher = PriceResearcher()

    try:
        # Research pricing
        print("🔍 Researching market prices...")
        analysis = researcher.research_pricing(
            product_description, brand=brand, condition=condition
        )

        # Print results
        researcher.print_analysis(analysis)

        # Save results to JSON
        os.makedirs("logs/price_researcher", exist_ok=True)
        output_file = f"logs/price_researcher/price_analysis_{int(time.time())}.json"
        with open(output_file, "w") as f:
            json.dump(
                {
                    "search_terms": analysis.search_terms,
                    "total_results": analysis.total_results,
                    "price_range": analysis.price_range,
                    "recent_sales": [
                        {
                            "source": sale.source,
                            "title": sale.title,
                            "price": sale.price,
                            "condition": sale.condition,
                            "sold_date": sale.sold_date,
                            "url": sale.url,
                        }
                        for sale in analysis.recent_sales
                    ],
                    "recommendations": analysis.recommendations,
                    "confidence_score": analysis.confidence_score,
                },
                f,
                indent=2,
            )

        print(f"\n💾 Results saved to: {output_file}")

    except Exception as e:
        print(f"❌ Error researching prices: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
