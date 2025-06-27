# PickPrice - Visual Product Pricing App

*Take a photo, get smart pricing for your resale items*

## What is PickPrice?

PickPrice helps you resell items by taking a simple photo and getting intelligent pricing recommendations. Perfect for clothes, electronics, collectibles, and more across platforms like eBay, Depop, Facebook Marketplace, and Mercari.

## How it works

1. **📸 Take a photo** of the item you want to sell
2. **🤖 AI identifies** the product using computer vision
3. **💰 Get pricing** based on current market data
4. **📈 See trends** and optimal selling strategies

## Current Approach: Proof-of-Concept Scripts

We're starting simple! Instead of building a full web app, we're creating Python scripts to prove the concept works:

```bash
# Try it out:
uv run scripts/gemini_analyzer.py photo.jpg
```

**Available Scripts:**
1. `gemini_analyzer.py` - AI-powered product identification using Google Gemini API
2. `image_analyzer.py` - Identifies products from photos using Google Vision API  
3. `price_researcher.py` - Searches marketplaces for similar items and pricing
4. `ai_pricing_engine.py` - Advanced AI-powered pricing analysis
5. `ebay_api_researcher.py` - eBay marketplace research and pricing data

## Current Status

🔬 **Proof-of-Concept Phase** - Building simple scripts to validate the idea

## Quick Start

```bash
# Clone and setup
git clone https://github.com/yourusername/pickprice-app
cd pickprice-app

# Install dependencies with uv
uv sync

# Set up your API keys
cp .env.example .env
# Edit .env with your Google Vision API key

# Try it out! (uv automatically manages the virtual environment)
uv run scripts/gemini_analyzer.py examples/shirt.jpg
uv run scripts/image_analyzer.py examples/shirt.jpg
```

## Project Structure

```
pickprice/
├── scripts/          # Proof-of-concept Python scripts
│   ├── gemini_analyzer.py
│   ├── image_analyzer.py
│   ├── price_researcher.py
│   ├── ai_pricing_engine.py
│   └── ebay_api_researcher.py
├── examples/         # Sample images for testing
├── docs/             # Documentation and ideas
└── pyproject.toml    # Python dependencies managed by uv
```

## Environment Variables (Future)

```env
GOOGLE_VISION_API_KEY=your_api_key
EBAY_API_KEY=your_ebay_key
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

## Contributing

This is a collaborative project! Feel free to:
- Add feature ideas to `IDEAS.md`
- Pick up tasks from `TODO.md`
- Submit PRs for improvements

## License

MIT License - feel free to use and modify

---

*Built with love for the reselling community* 💜