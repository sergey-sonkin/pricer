# PicPrice Scripts

We have specialized scripts for different aspects of product pricing analysis

## Image Analyzer (Vision API)

The `image_analyzer.py` script provides structured product identification using Google Vision API.

### Setup

1. **Install dependencies:**

   ```bash
   uv sync
   ```

2. **Set up Google Vision API:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the Vision API
   - Create a service account and download the JSON key file
   - Set environment variable:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
     ```

### Usage

```bash
python image_analyzer.py path/to/your/image.jpg
```

### Example Output

```
🔍 Analysis Results for: shirt.jpg
==================================================
📊 Confidence Score: 0.75
📂 Suggested Category: Clothing

🏷️  Detected Labels:
   • Clothing
   • Shirt
   • Sleeve
   • Collar
   • Fashion

📦 Detected Objects:
   • Shirt

🏢 Potential Brands:
   • NIKE
   • ADIDAS

📝 Detected Text:
   • Size: Large
   • 100% Cotton
   • Made in USA

💾 Results saved to: shirt_analysis.json
```

### What it does

- **Label Detection**: Identifies what's in the image
- **Text Recognition**: Extracts text from the image (brands, sizes, etc.)
- **Object Detection**: Locates specific objects
- **Brand Extraction**: Finds potential brand names
- **Category Suggestion**: Suggests product category
- **Confidence Scoring**: Rates how confident the analysis is

### Testing

Try it with different types of items:

- Clothing (shirts, shoes, jeans)
- Electronics (phones, laptops)
- Books
- Household items

The better the photo quality and lighting, the better the results!

---

## Gemini Analyzer (AI Vision)

The `gemini_analyzer.py` script uses Google's advanced Gemini AI for sophisticated product analysis.

### Setup

1. **Install dependencies:**

   ```bash
   uv sync
   ```

2. **Set up Google AI API:**
   - Go to [Google AI Studio](https://aistudio.google.com/)
   - Get your API key
   - Set environment variable:
     ```bash
     export GOOGLE_AI_API_KEY="your_google_ai_key"
     ```

### Usage

```bash
python gemini_analyzer.py path/to/your/image.jpg
```

### Example Output

```
🤖 Gemini AI Analysis for: vintage_watch.jpg

🎯 Confidence Level: High

📝 Product Description:
A vintage Rolex Submariner watch with a black dial and stainless steel bracelet.
The watch appears to be in excellent condition with minimal wear on the case and bracelet.

📦 Product Type: Luxury Watch
🏪 Market Category: Jewelry & Watches > Watches > Luxury Watches > Rolex
🏢 Brand: Rolex
⭐ Condition: Excellent

✨ Notable Features:
• Submariner model with rotating bezel
• Stainless steel construction
• Black dial with luminous markers
• Automatic movement
• Professional diving watch (300m water resistance)

💰 Pricing Factors:
• Model year and reference number
• Condition and service history
• Original box and papers availability
• Market demand for vintage Rolexes
• Authentication and provenance
```

### What it does

- **Advanced AI Analysis**: Uses Gemini's multimodal AI for deep product understanding
- **Detailed Descriptions**: Rich, contextual product descriptions
- **Market Category Mapping**: Specific marketplace categories
- **Brand Recognition**: Sophisticated brand identification
- **Condition Assessment**: AI-powered condition evaluation
- **Pricing Insights**: Factors that affect market value

---

## OpenAI Vision Analyzer (GPT-4 Vision)

The `openai_analyzer.py` script uses OpenAI's GPT-4 Vision for advanced product analysis and market insights.

### Setup

1. **Install dependencies:**

   ```bash
   uv sync
   ```

2. **Set up OpenAI API:**
   - Go to [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create an API key
   - Set environment variable:
     ```bash
     export OPENAI_API_KEY="your_openai_api_key"
     ```

### Usage

```bash
python openai_analyzer.py path/to/your/image.jpg
```

### Example Output

```
🤖 OpenAI Vision Analysis for: vintage_camera.jpg
==================================================
🎯 Confidence Level: High

📝 Product Description:
   Vintage 35mm film camera with leather body and manual controls.
   Appears to be a classic rangefinder style camera from the 1960s-70s era.

📦 Product Type: Photography Equipment
🏪 Market Category: Cameras & Photo > Vintage Cameras
🏢 Brand: Leica
⭐ Condition: Good

✨ Notable Features:
   • Manual focus and exposure controls
   • Leather body with metal trim
   • Vintage rangefinder design
   • Original lens appears intact

💰 Pricing Factors:
   • Brand reputation and model rarity
   • Working condition of mechanisms
   • Lens quality and clarity
   • Completeness of original accessories
   • Age and historical significance
```

### What it does

- **GPT-4 Vision Analysis**: Uses OpenAI's most advanced vision model
- **Market-Focused Insights**: Tailored for resale scenarios
- **Detailed Descriptions**: Rich contextual analysis
- **Brand Recognition**: Sophisticated identification capabilities
- **Pricing Context**: Factors that influence market value
- **Condition Assessment**: AI-powered condition evaluation

---

## 🆕 eBay Image Lookup

The `ebay_image_lookup.py` script allows you to search eBay using an image instead of text queries.

### Setup

1. **Install dependencies:**

   ```bash
   uv sync
   ```

2. **Set up eBay API:**
   - Go to [eBay Developers](https://developer.ebay.com/)
   - Create an app to get App ID and Cert ID
   - Set environment variables:
     ```bash
     export EBAY_SANDBOX_APP_ID="your_sandbox_app_id"
     export EBAY_SANDBOX_CERT_ID="your_sandbox_cert_id"
     export EBAY_USE_SANDBOX="true"  # Set to false for production
     ```

### Usage

```bash
python ebay_image_lookup.py path/to/your/image.jpg
```

### Example Output

```
=== eBay Image Lookup ===
Image: vintage_watch.jpg

🔍 Searching eBay using image...
📊 Found 23 similar items

=== Search Results Summary ===
Total items found: 23
Items returned: 23

💰 Price Analysis:
Min price: $89.99
Max price: $2,450.00
Average price: $486.23
Median price: $325.00

=== Sample Items ===
1. Vintage Omega Speedmaster Professional - $1,250.00
   Condition: Used
   Seller: watch_collector_pro

2. Rolex Submariner Date Vintage - $2,450.00
   Condition: Pre-owned
   Seller: luxury_timepieces

3. Seiko Diver's Watch 200m - $189.95
   Condition: Used
   Seller: affordable_watches

Full results saved to: logs/ebay_image_lookup/vintage_watch_lookup_1234567890.json
```

### What it does

- **Visual Search**: Find similar items using image recognition
- **Price Discovery**: Get current market pricing for visually similar items
- **Market Analysis**: Statistical breakdown of found listings
- **Detailed Results**: Complete item information including seller data
- **JSON Export**: Structured data for further analysis
- **Production Ready**: Robust error handling and API management

---

## 🆕 eBay Market Research

The `ebay_api_researcher.py` script provides real marketplace data using eBay's official Browse API.

### Setup

1. **Install dependencies:**

   ```bash
   uv sync
   ```

2. **Set up eBay API:**
   - Go to [eBay Developers](https://developer.ebay.com/)
   - Create an app to get App ID and Cert ID
   - Set environment variables:
     ```bash
     export EBAY_SANDBOX_APP_ID="your_sandbox_app_id"
     export EBAY_SANDBOX_CERT_ID="your_sandbox_cert_id"
     export EBAY_USE_SANDBOX="true"  # Set to false for production
     ```

### Usage

```bash
# Basic search
python ebay_api_researcher.py "vintage rolex"

# Search with category ID for better results
python ebay_api_researcher.py "vintage rolex" "31387"
```

### Example Output

```
🚀 Using eBay Browse API with App ID: YourApp...
🔍 Researching 'vintage rolex' on eBay...
  🛒 Fetching active listings...
    📊 API returned 47 active items
    🛒 Active: $2,850.00 - Vintage Rolex Submariner 5513...
    🛒 Active: $4,200.00 - 1970s Rolex GMT Master 1675...
    🛒 Active: $3,100.00 - Rolex Datejust 16030 Vintage...
    ✅ Found 47 active listings

📊 eBay Analysis for: vintage rolex
============================================================
🎯 Confidence Score: 0.47
📈 Data: 0 sold, 47 active

🛒 Active Listings Price Analysis:
   • Range: $1,200.00 - $8,500.00
   • Average: $3,420.15
   • Median: $3,100.00

💡 Market Insights:
   • Market data based on 47 active listings
   • Most common condition sold: Used
   • Current market shows strong demand for vintage models

💾 Results saved to: logs/ebay_api_researcher/ebay_analysis_1234567890.json
```

### What it does

- **Real Market Data**: Live eBay marketplace information
- **Price Analytics**: Statistical analysis of current listings
- **Market Insights**: Automated trend analysis and recommendations
- **Condition Comparison**: Analysis of how condition affects pricing
- **Confidence Scoring**: Data quality assessment
- **JSON Export**: Structured data for further analysis
- **Error Handling**: Graceful API error management

### Features

✅ **Active Listings** - Current marketplace inventory and pricing
✅ **Price Statistics** - Min, max, average, median calculations
✅ **Market Insights** - Automated analysis of pricing trends
✅ **Condition Analysis** - Compare pricing by item condition
✅ **Data Export** - Save results in JSON format
✅ **Production Ready** - Type-safe code with robust error handling

---

## Price Research Tools

### `price_researcher.py`

Web scraping tool for multi-platform price comparison.

### `ai_pricing_engine.py`

Advanced AI-powered pricing analysis and recommendations.

---

## Quick Reference

### All Available Scripts

| Script                   | Purpose                                  | API Required    |
| ------------------------ | ---------------------------------------- | --------------- |
| `image_analyzer.py`      | Google Vision API product identification | Google Vision   |
| `gemini_analyzer.py`     | Advanced AI analysis with Gemini         | Google AI       |
| `openai_analyzer.py`     | **NEW!** OpenAI GPT-4 Vision analysis    | OpenAI API      |
| `ebay_api_researcher.py` | Real eBay marketplace data               | eBay Browse API |
| `ebay_image_lookup.py`   | **NEW!** Visual search on eBay           | eBay Browse API |
| `price_researcher.py`    | Multi-platform price scraping            | None            |
| `ai_pricing_engine.py`   | AI-powered pricing engine                | Various         |

### Environment Variables Setup

```bash
# Core APIs
export GOOGLE_AI_API_KEY="your_google_ai_key"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
export OPENAI_API_KEY="your_openai_api_key"  # NEW!

# eBay Browse API
export EBAY_SANDBOX_APP_ID="your_sandbox_app_id"
export EBAY_SANDBOX_CERT_ID="your_sandbox_cert_id"
export EBAY_USE_SANDBOX="true"
```

### Typical Workflow

1. **Analyze Product**: Use `gemini_analyzer.py` for detailed product analysis
2. **Research Market**: Use `ebay_api_researcher.py` for current market data
3. **Compare Prices**: Use `price_researcher.py` for cross-platform comparison
4. **Get Recommendations**: Use `ai_pricing_engine.py` for final pricing

### Integration with AI Agent

All these scripts can be orchestrated through the main AI agent:

```bash
# Chat with the AI agent that can use all tools
python agent/main.py
```

The agent can chain operations like: Image Analysis → Market Research → Pricing Recommendations

---

## Recent Updates (January 2025)

✅ **eBay Browse API Integration** - Professional marketplace research
✅ **Enhanced Market Analysis** - Condition comparison and trend insights
✅ **Type-Safe Code** - Modern Python with comprehensive error handling
✅ **Production Ready** - All LSP errors resolved, robust API clients

See the main [README.md](../README.md) for complete project documentation.
