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
python pricing_assistant.py photo.jpg
```

**Script Pipeline:**
1. `image_analyzer.py` - Identifies products from photos using Google Vision API
2. `price_researcher.py` - Searches marketplaces for similar items and pricing
3. `market_analyzer.py` - Analyzes trends and provides recommendations
4. `pricing_assistant.py` - Main script that orchestrates everything

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

# Activate virtual environment and try it out!
source .venv/bin/activate
python scripts/image_analyzer.py examples/shirt.jpg
```

## Project Structure

```
pickprice/
├── scripts/          # Proof-of-concept Python scripts
│   ├── image_analyzer.py
│   ├── price_researcher.py
│   ├── market_analyzer.py
│   └── pricing_assistant.py
├── examples/         # Sample images for testing
├── docs/             # Documentation and ideas
└── requirements.txt  # Python dependencies
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