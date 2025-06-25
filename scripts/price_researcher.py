#!/usr/bin/env python3
"""
Price Researcher - Find market pricing data for products

Uses eBay API and web scraping to research pricing for identified products.
Provides price ranges, market trends, and comparable listings.
"""

import json
import os
import sys
import time
from dataclasses import dataclass
from typing import Dict, List
from urllib.parse import quote
import random

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
    price_range: Dict[str, float]  # min, max, average, median
    recent_sales: List[PriceData]
    price_trends: Dict[str, str]
    recommendations: List[str]
    confidence_score: float


class PriceResearcher:
    """Research market pricing for products"""
    
    def __init__(self):
        """Initialize the price researcher"""
        load_dotenv()
        
        # eBay API credentials (optional for now)
        self.ebay_app_id = os.getenv('EBAY_APP_ID')
        self.ebay_cert_id = os.getenv('EBAY_CERT_ID')
        
        # Headers for web scraping (rotate user agents)
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
        ]
    
    def _get_headers(self):
        """Get randomized headers for requests"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def _make_request(self, url: str, max_retries: int = 3):
        """Make HTTP request with retry logic"""
        for attempt in range(max_retries):
            try:
                # Add random delay between requests
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
                if attempt == max_retries - 1:
                    print(f"    ❌ All attempts failed due to timeout")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"    ❌ Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return None
        
        return None
    
    def research_pricing(self, product_description: str, product_type: str | None = None, 
                        brand: str | None = None, condition: str | None = None) -> PriceAnalysis:
        """
        Research pricing for a product
        
        Args:
            product_description: Description of the product
            product_type: Type/category of product
            brand: Brand name if known
            condition: Product condition
            
        Returns:
            PriceAnalysis with pricing data
        """
        # Build search terms
        search_terms = self._build_search_terms(product_description, product_type, brand)
        
        print(f"🔍 Searching for: {search_terms}")
        
        # Collect pricing data from multiple sources
        all_price_data = []
        
        # 1. eBay sold listings (web scraping)
        ebay_data = self._scrape_ebay_sold(search_terms)
        all_price_data.extend(ebay_data)
        
        # 2. eBay current listings (for market context)
        ebay_current = self._scrape_ebay_current(search_terms)
        all_price_data.extend(ebay_current)
        
        # 3. Google Shopping (basic price check)
        google_data = self._search_google_shopping(search_terms)
        all_price_data.extend(google_data)
        
        # Analyze the collected data
        analysis = self._analyze_pricing_data(search_terms, all_price_data, condition)
        
        return analysis
    
    def _build_search_terms(self, description: str, product_type: str | None = None, brand: str | None = None) -> str:
        """Build effective search terms from product info"""
        terms = []
        
        # Add brand if available
        if brand and brand.lower() != 'null':
            terms.append(brand)
        
        # Extract key words from description
        # Remove common stop words and focus on product-specific terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'used', 'good', 'condition'}
        words = description.lower().split()
        key_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Take the most relevant words (usually first few are most important)
        terms.extend(key_words[:4])
        
        return ' '.join(terms)
    
    def _scrape_ebay_sold(self, search_terms: str, max_results: int = 20) -> List[PriceData]:
        """Scrape eBay sold listings for pricing data"""
        results = []
        
        try:
            # eBay sold listings URL
            encoded_terms = quote(search_terms)
            url = f"https://www.ebay.com/sch/i.html?_nkw={encoded_terms}&_sacat=0&LH_Sold=1&LH_Complete=1&_sop=13"
            
            print("  📦 Checking eBay sold listings...")
            response = self._make_request(url)
            if not response:
                return results
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find listing items
            items = soup.find_all('div', class_='s-item__wrapper')[:max_results]
            
            for item in items:
                try:
                    # Extract title
                    title_elem = item.find('span', role='heading')
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # Extract price
                    price_elem = item.find('span', class_='notranslate')
                    if not price_elem:
                        continue
                    
                    price_text = price_elem.get_text(strip=True)
                    # Parse price (remove $ and convert to float)
                    price = float(price_text.replace('$', '').replace(',', ''))
                    
                    # Extract sold date
                    sold_elem = item.find('span', class_='POSITIVE')
                    sold_date = sold_elem.get_text(strip=True) if sold_elem else None
                    
                    # Extract URL
                    link_elem = item.find('a', class_='s-item__link')
                    item_url = None
                    if link_elem and hasattr(link_elem, 'get'):
                        href = link_elem.get('href')
                        item_url = str(href) if href else None
                    
                    results.append(PriceData(
                        source='eBay Sold',
                        title=title,
                        price=price,
                        condition='used',  # Most sold items are used
                        sold_date=sold_date,
                        url=item_url
                    ))
                    
                except (ValueError, AttributeError):
                    # Skip items that can't be parsed
                    continue
        
        except Exception as e:
            print(f"  ❌ Error scraping eBay sold listings: {e}")
        
        print(f"  ✅ Found {len(results)} eBay sold listings")
        return results
    
    def _scrape_ebay_current(self, search_terms: str, max_results: int = 10) -> List[PriceData]:
        """Scrape current eBay listings for market context"""
        results = []
        
        try:
            encoded_terms = quote(search_terms)
            url = f"https://www.ebay.com/sch/i.html?_nkw={encoded_terms}&_sacat=0&_sop=15"  # Sort by price
            
            print("  🛒 Checking current eBay listings...")
            response = self._make_request(url)
            if not response:
                return results
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find listing items
            items = soup.find_all('div', class_='s-item__wrapper')[:max_results]
            
            for item in items:
                try:
                    # Extract title
                    title_elem = item.find('span', role='heading')
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # Extract price
                    price_elem = item.find('span', class_='notranslate')
                    if not price_elem:
                        continue
                    
                    price_text = price_elem.get_text(strip=True)
                    price = float(price_text.replace('$', '').replace(',', ''))
                    
                    # Extract URL
                    link_elem = item.find('a', class_='s-item__link')
                    item_url = None
                    if link_elem and hasattr(link_elem, 'get'):
                        href = link_elem.get('href')
                        item_url = str(href) if href else None
                    
                    results.append(PriceData(
                        source='eBay Current',
                        title=title,
                        price=price,
                        condition='mixed',
                        sold_date=None,
                        url=item_url
                    ))
                    
                except (ValueError, AttributeError):
                    continue
        
        except Exception as e:
            print(f"  ❌ Error scraping current eBay listings: {e}")
        
        print(f"  ✅ Found {len(results)} current eBay listings")
        return results
    
    def _search_google_shopping(self, search_terms: str, max_results: int = 5) -> List[PriceData]:
        """Search Google Shopping for price references"""
        results = []
        
        try:
            # Google Shopping search
            encoded_terms = quote(search_terms)
            url = f"https://www.google.com/search?tbm=shop&q={encoded_terms}"
            
            print("  🛍️  Checking Google Shopping...")
            response = self._make_request(url)
            if not response:
                return results
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find shopping results (simplified parsing)
            price_elements = soup.find_all('span', class_='a8Pemb')[:max_results]
            
            for price_elem in price_elements:
                try:
                    price_text = price_elem.get_text(strip=True)
                    if '$' in price_text:
                        price = float(price_text.replace('$', '').replace(',', ''))
                        
                        results.append(PriceData(
                            source='Google Shopping',
                            title=search_terms,
                            price=price,
                            condition='new',  # Google Shopping usually shows new items
                            sold_date=None,
                            url=None
                        ))
                except (ValueError, AttributeError):
                    continue
        
        except Exception as e:
            print(f"  ❌ Error searching Google Shopping: {e}")
        
        print(f"  ✅ Found {len(results)} Google Shopping results")
        return results
    
    def _analyze_pricing_data(self, search_terms: str, price_data: List[PriceData], 
                            condition: str | None = None) -> PriceAnalysis:
        """Analyze collected pricing data and generate insights"""
        
        if not price_data:
            return PriceAnalysis(
                search_terms=search_terms,
                total_results=0,
                price_range={'min': 0, 'max': 0, 'average': 0, 'median': 0},
                recent_sales=[],
                price_trends={'trend': 'insufficient_data'},
                recommendations=['No pricing data found. Try different search terms.'],
                confidence_score=0.0
            )
        
        # Extract prices for analysis
        prices = [item.price for item in price_data if item.price > 0]
        
        # Calculate price statistics
        price_range = {
            'min': min(prices) if prices else 0,
            'max': max(prices) if prices else 0,
            'average': sum(prices) / len(prices) if prices else 0,
            'median': sorted(prices)[len(prices)//2] if prices else 0
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(price_data, price_range, condition)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(price_data)
        
        # Get recent sales for display
        recent_sales = [item for item in price_data if item.source == 'eBay Sold'][:10]
        
        return PriceAnalysis(
            search_terms=search_terms,
            total_results=len(price_data),
            price_range=price_range,
            recent_sales=recent_sales,
            price_trends={'trend': 'stable'},  # Simplified for now
            recommendations=recommendations,
            confidence_score=confidence
        )
    
    def _generate_recommendations(self, price_data: List[PriceData], 
                                price_range: Dict[str, float], condition: str | None) -> List[str]:
        """Generate pricing recommendations based on data"""
        recommendations = []
        
        avg_price = price_range['average']
        sold_items = [item for item in price_data if item.source == 'eBay Sold']
        current_items = [item for item in price_data if item.source == 'eBay Current']
        
        if avg_price > 0:
            if condition and 'good' in condition.lower():
                rec_price = avg_price * 0.8  # 80% of average for used/good condition
                recommendations.append(f"For good condition, consider pricing around ${rec_price:.2f}")
            else:
                recommendations.append(f"Average market price: ${avg_price:.2f}")
        
        if sold_items and current_items:
            sold_avg = sum(item.price for item in sold_items) / len(sold_items)
            current_avg = sum(item.price for item in current_items) / len(current_items)
            
            if current_avg > sold_avg * 1.2:
                recommendations.append("Current listings are priced high - consider competitive pricing")
            elif current_avg < sold_avg * 0.8:
                recommendations.append("Market may be soft - consider waiting or pricing aggressively")
        
        if len(sold_items) >= 5:
            recommendations.append("Good market data available - pricing confidence is high")
        else:
            recommendations.append("Limited sales data - consider researching similar items")
        
        return recommendations
    
    def _calculate_confidence(self, price_data: List[PriceData]) -> float:
        """Calculate confidence score based on available data"""
        sold_count = len([item for item in price_data if item.source == 'eBay Sold'])
        total_count = len(price_data)
        
        # Base confidence on amount and quality of data
        confidence = 0.0
        
        # Sold listings are most valuable
        confidence += min(sold_count * 0.15, 0.6)
        
        # Total data points
        confidence += min(total_count * 0.05, 0.3)
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def print_analysis(self, analysis: PriceAnalysis):
        """Print formatted price analysis"""
        print(f"\n💰 Price Analysis for: {analysis.search_terms}")
        print("=" * 50)
        
        print(f"📊 Confidence Score: {analysis.confidence_score:.2f}")
        print(f"📈 Total Results Found: {analysis.total_results}")
        
        if analysis.price_range['average'] > 0:
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
        print("Usage: python price_researcher.py <product_description> [brand] [condition]")
        print("Example: python price_researcher.py \"cat litter box\" \"Petmate\" \"good\"")
        sys.exit(1)
    
    product_description = sys.argv[1]
    brand = sys.argv[2] if len(sys.argv) > 2 else None
    condition = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Initialize researcher
    researcher = PriceResearcher()
    
    try:
        # Research pricing
        print("🔍 Researching market prices...")
        analysis = researcher.research_pricing(product_description, brand=brand, condition=condition)
        
        # Print results
        researcher.print_analysis(analysis)
        
        # Save results to JSON
        output_file = f"price_analysis_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump({
                'search_terms': analysis.search_terms,
                'total_results': analysis.total_results,
                'price_range': analysis.price_range,
                'recent_sales': [
                    {
                        'source': sale.source,
                        'title': sale.title,
                        'price': sale.price,
                        'condition': sale.condition,
                        'sold_date': sale.sold_date,
                        'url': sale.url
                    } for sale in analysis.recent_sales
                ],
                'recommendations': analysis.recommendations,
                'confidence_score': analysis.confidence_score
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error researching prices: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()