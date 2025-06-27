#!/usr/bin/env python3
"""
AI Pricing Engine - Modular pricing tools using Gemini AI

Each function is designed to be a standalone MCP tool that can be called
independently by an LLM orchestrator to build pricing intelligence.
"""

import json
import os
import sys
import time
from dataclasses import dataclass
from typing import Dict, List
from urllib.parse import quote

try:
    import google.generativeai as genai
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: uv add google-generativeai requests beautifulsoup4")
    sys.exit(1)


@dataclass
class PriceEstimate:
    """AI-generated price estimate"""
    
    low_estimate: float
    high_estimate: float
    most_likely_price: float
    confidence_level: str
    reasoning: str
    factors_considered: List[str]
    comparable_items: List[str]
    market_context: str


@dataclass
class SearchResult:
    """Web search result for pricing context"""
    
    title: str
    url: str
    snippet: str
    price: float | None
    source: str


@dataclass
class MarketInsight:
    """Market insight from AI analysis"""
    
    category: str
    demand_level: str
    seasonal_factors: List[str]
    pricing_strategy: str
    best_platforms: List[str]
    timing_recommendations: List[str]


class AIPricingEngine:
    """Modular AI pricing tools for MCP integration"""
    
    def __init__(self, api_key: str | None = None):
        """Initialize with Gemini API key"""
        api_key = api_key or os.getenv('GOOGLE_AI_API_KEY')
        
        if not api_key:
            raise ValueError("Google AI API key required. Set GOOGLE_AI_API_KEY environment variable.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    # =============================================================================
    # MCP TOOL: AI Price Estimation
    # =============================================================================
    
    def estimate_price_with_ai(self, product_description: str, condition: str = "good", 
                              brand: str | None = None, additional_context: str = "") -> PriceEstimate:
        """
        MCP Tool: Get AI-powered price estimate for a product
        
        Args:
            product_description: Description of the product
            condition: Product condition (new, like new, good, fair, poor)
            brand: Brand name if known
            additional_context: Any additional context (size, year, etc.)
            
        Returns:
            PriceEstimate with price range and reasoning
        """
        
        prompt = f"""
        You are a pricing expert for resale marketplaces like eBay, Depop, Facebook Marketplace, and Mercari.
        
        Analyze this product and provide a pricing estimate in JSON format:
        
        Product: {product_description}
        Brand: {brand if brand else "Unknown"}
        Condition: {condition}
        Additional Context: {additional_context}
        
        Consider:
        - Current market demand for this type of item
        - Brand premium or discount
        - Condition impact on pricing
        - Seasonal factors
        - Platform preferences (eBay vs Depop vs Facebook, etc.)
        - Recent market trends
        
        Respond with this exact JSON structure:
        {{
            "low_estimate": <lowest reasonable price>,
            "high_estimate": <highest reasonable price>,
            "most_likely_price": <most probable selling price>,
            "confidence_level": "high|medium|low",
            "reasoning": "Detailed explanation of pricing logic",
            "factors_considered": ["factor1", "factor2", "factor3"],
            "comparable_items": ["similar item 1", "similar item 2"],
            "market_context": "Current market conditions and trends"
        }}
        
        Be specific with dollar amounts and provide realistic estimates based on actual resale market conditions.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Clean and parse response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            data = json.loads(response_text)
            
            return PriceEstimate(
                low_estimate=float(data.get('low_estimate', 0)),
                high_estimate=float(data.get('high_estimate', 0)),
                most_likely_price=float(data.get('most_likely_price', 0)),
                confidence_level=data.get('confidence_level', 'low'),
                reasoning=data.get('reasoning', ''),
                factors_considered=data.get('factors_considered', []),
                comparable_items=data.get('comparable_items', []),
                market_context=data.get('market_context', '')
            )
            
        except Exception as e:
            # Fallback if parsing fails
            return PriceEstimate(
                low_estimate=0.0,
                high_estimate=0.0,
                most_likely_price=0.0,
                confidence_level='low',
                reasoning=f"Error generating estimate: {str(e)}",
                factors_considered=[],
                comparable_items=[],
                market_context=""
            )
    
    # =============================================================================
    # MCP TOOL: Market Research via Search
    # =============================================================================
    
    def research_product_online(self, product_description: str, max_results: int = 10) -> List[SearchResult]:
        """
        MCP Tool: Research product pricing through web search
        
        Args:
            product_description: Product to research
            max_results: Maximum search results to return
            
        Returns:
            List of SearchResult with pricing context
        """
        
        results = []
        
        # Build search queries for different contexts
        queries = [
            f"{product_description} price sold",
            f"{product_description} eBay sold listings",
            f"{product_description} marketplace price",
            f"how much is {product_description} worth"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        for query in queries[:2]:  # Limit to 2 queries to avoid rate limiting
            try:
                # Google search
                search_url = f"https://www.google.com/search?q={quote(query)}"
                response = requests.get(search_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract search results
                    search_divs = soup.find_all('div', class_='g')[:max_results//2]
                    
                    for div in search_divs:
                        title_elem = div.find('h3')
                        link_elem = div.find('a')
                        snippet_elem = div.find('span', class_='aCOpRe') or div.find('span', class_='st')
                        
                        if title_elem and link_elem:
                            title = title_elem.get_text(strip=True)
                            url = link_elem.get('href', '')
                            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                            
                            # Try to extract price from snippet
                            price = self._extract_price_from_text(snippet + ' ' + title)
                            
                            results.append(SearchResult(
                                title=title,
                                url=url,
                                snippet=snippet,
                                price=price,
                                source='Google Search'
                            ))
                
                # Small delay between searches
                time.sleep(1)
                
            except Exception as e:
                print(f"Search error for '{query}': {e}")
                continue
        
        return results[:max_results]
    
    # =============================================================================
    # MCP TOOL: AI Market Analysis
    # =============================================================================
    
    def analyze_market_conditions(self, product_type: str, season: str = "current") -> MarketInsight:
        """
        MCP Tool: Get AI analysis of market conditions for a product type
        
        Args:
            product_type: Type of product (electronics, clothing, collectibles, etc.)
            season: Current season or "current" for auto-detect
            
        Returns:
            MarketInsight with market analysis
        """
        
        current_month = time.strftime("%B")
        current_year = time.strftime("%Y")
        
        prompt = f"""
        Analyze the current resale market conditions for {product_type} in {current_month} {current_year}.
        
        Provide market insights in this JSON format:
        {{
            "category": "{product_type}",
            "demand_level": "high|medium|low",
            "seasonal_factors": ["factor1", "factor2"],
            "pricing_strategy": "Recommended pricing approach",
            "best_platforms": ["platform1", "platform2"],
            "timing_recommendations": ["timing tip 1", "timing tip 2"]
        }}
        
        Consider:
        - Current economic conditions
        - Seasonal demand patterns
        - Platform-specific trends
        - Consumer behavior in {current_month}
        - Supply and demand factors
        - Upcoming holidays or events
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            data = json.loads(response_text)
            
            return MarketInsight(
                category=data.get('category', product_type),
                demand_level=data.get('demand_level', 'medium'),
                seasonal_factors=data.get('seasonal_factors', []),
                pricing_strategy=data.get('pricing_strategy', ''),
                best_platforms=data.get('best_platforms', []),
                timing_recommendations=data.get('timing_recommendations', [])
            )
            
        except Exception as e:
            return MarketInsight(
                category=product_type,
                demand_level='medium',
                seasonal_factors=[],
                pricing_strategy=f"Error analyzing market: {str(e)}",
                best_platforms=['eBay', 'Facebook Marketplace'],
                timing_recommendations=[]
            )
    
    # =============================================================================
    # MCP TOOL: Comparative Pricing
    # =============================================================================
    
    def compare_similar_products(self, target_product: str, similar_products: List[str]) -> Dict[str, PriceEstimate]:
        """
        MCP Tool: Compare pricing for similar products
        
        Args:
            target_product: Main product to price
            similar_products: List of similar products for comparison
            
        Returns:
            Dictionary mapping product names to price estimates
        """
        
        comparisons = {}
        
        # Get price estimate for target product
        target_estimate = self.estimate_price_with_ai(target_product)
        comparisons[target_product] = target_estimate
        
        # Get estimates for similar products
        for product in similar_products:
            try:
                estimate = self.estimate_price_with_ai(product)
                comparisons[product] = estimate
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"Error estimating price for {product}: {e}")
                continue
        
        return comparisons
    
    # =============================================================================
    # MCP TOOL: Condition Impact Analysis
    # =============================================================================
    
    def analyze_condition_impact(self, product_description: str, brand: str | None = None) -> Dict[str, PriceEstimate]:
        """
        MCP Tool: Analyze how condition affects pricing
        
        Args:
            product_description: Product description
            brand: Optional brand name
            
        Returns:
            Dictionary mapping conditions to price estimates
        """
        
        conditions = ["new", "like new", "good", "fair", "poor"]
        condition_analysis = {}
        
        for condition in conditions:
            try:
                estimate = self.estimate_price_with_ai(product_description, condition, brand)
                condition_analysis[condition] = estimate
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"Error analyzing condition '{condition}': {e}")
                continue
        
        return condition_analysis
    
    # =============================================================================
    # Helper Methods
    # =============================================================================
    
    def _extract_price_from_text(self, text: str) -> float | None:
        """Extract price from text using regex patterns"""
        import re
        
        # Common price patterns
        patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $123.45, $1,234.56
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?) dollars',  # 123.45 dollars
            r'USD (\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # USD 123.45
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    # Take the first match and clean it
                    price_str = matches[0].replace(',', '')
                    return float(price_str)
                except ValueError:
                    continue
        
        return None


# =============================================================================
# CLI Interface for Testing Individual Tools
# =============================================================================

def main():
    """CLI interface for testing individual pricing tools"""
    if len(sys.argv) < 3:
        print("Usage: python ai_pricing_engine.py <tool> <args...>")
        print("\nAvailable tools:")
        print("  estimate <product_description> [condition] [brand]")
        print("  research <product_description> [max_results]")
        print("  market <product_type> [season]")
        print("  compare <target_product> <similar_product1> <similar_product2> ...")
        print("  condition <product_description> [brand]")
        print("\nExamples:")
        print("  python ai_pricing_engine.py estimate \"cat litter box\" good")
        print("  python ai_pricing_engine.py research \"iphone 12\" 5")
        print("  python ai_pricing_engine.py market \"electronics\"")
        sys.exit(1)
    
    tool = sys.argv[1]
    
    try:
        engine = AIPricingEngine()
        
        if tool == "estimate":
            product = sys.argv[2]
            condition = sys.argv[3] if len(sys.argv) > 3 else "good"
            brand = sys.argv[4] if len(sys.argv) > 4 else None
            
            print(f"🔍 Estimating price for: {product}")
            estimate = engine.estimate_price_with_ai(product, condition, brand)
            
            print(f"\n💰 Price Estimate:")
            print(f"   Range: ${estimate.low_estimate:.2f} - ${estimate.high_estimate:.2f}")
            print(f"   Most Likely: ${estimate.most_likely_price:.2f}")
            print(f"   Confidence: {estimate.confidence_level}")
            print(f"\n💭 Reasoning: {estimate.reasoning}")
            print(f"\n📊 Factors: {', '.join(estimate.factors_considered)}")
            
        elif tool == "research":
            product = sys.argv[2]
            max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            
            print(f"🔍 Researching: {product}")
            results = engine.research_product_online(product, max_results)
            
            print(f"\n📈 Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                price_str = f"${result.price:.2f}" if result.price else "No price"
                print(f"   {i}. {price_str} - {result.title[:60]}...")
                
        elif tool == "market":
            product_type = sys.argv[2]
            season = sys.argv[3] if len(sys.argv) > 3 else "current"
            
            print(f"📊 Analyzing market for: {product_type}")
            insight = engine.analyze_market_conditions(product_type, season)
            
            print(f"\n🎯 Market Analysis:")
            print(f"   Demand Level: {insight.demand_level}")
            print(f"   Strategy: {insight.pricing_strategy}")
            print(f"   Best Platforms: {', '.join(insight.best_platforms)}")
            print(f"   Seasonal Factors: {', '.join(insight.seasonal_factors)}")
            
        elif tool == "compare":
            target = sys.argv[2]
            similar = sys.argv[3:] if len(sys.argv) > 3 else []
            
            print(f"🔄 Comparing: {target}")
            comparisons = engine.compare_similar_products(target, similar)
            
            print(f"\n📊 Price Comparisons:")
            for product, estimate in comparisons.items():
                print(f"   {product}: ${estimate.most_likely_price:.2f}")
                
        elif tool == "condition":
            product = sys.argv[2]
            brand = sys.argv[3] if len(sys.argv) > 3 else None
            
            print(f"🔍 Condition analysis for: {product}")
            analysis = engine.analyze_condition_impact(product, brand)
            
            print(f"\n📈 Condition Impact:")
            for condition, estimate in analysis.items():
                print(f"   {condition.title()}: ${estimate.most_likely_price:.2f}")
        
        else:
            print(f"❌ Unknown tool: {tool}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()