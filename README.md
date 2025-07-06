# PicPrice - Visual Product Pricing App

_Take a photo, get smart pricing for your resale items_

## What is PicPrice?

PicPrice helps you resell items by taking a simple photo and getting intelligent pricing recommendations. Perfect for clothes, electronics, collectibles, and more across platforms like eBay, Depop, Facebook Marketplace, and Mercari.

## How it works

1. **📸 Take a photo** of the item you want to sell
2. **🤖 AI identifies** the product using computer vision
3. **💰 Get pricing** based on current market data
4. **📈 See trends** and optimal selling strategies

## Current Approach: Modular AI Agent Architecture

We've built a **Claude-powered pricing agent** with clean, modular architecture and comprehensive testing:

```bash
# Chat with the AI pricing agent:
python agent/main.py
```

**🏗️ Architecture Overview:**

- **`agent/`** - Main conversational AI that orchestrates tools
- **`lib/`** - Core reusable analyzer classes (GeminiAnalyzer, OpenAIAnalyzer, etc.)
- **`scripts/`** - CLI interfaces for standalone usage
- **`tests/`** - Documented test cases for regression testing
- **`tools/`** - Agent tool wrappers that use lib classes

**🛠️ Agent Tools:**

- **Gemini Vision Analysis** - Google's AI for product identification from photos
- **OpenAI Vision Analysis** - GPT-4 Vision for advanced product analysis and market insights
- **Google Vision Analysis** - Traditional computer vision for detailed feature extraction
- **eBay Market Research** - Real marketplace data using eBay Browse API
- **File System Tools** - Read and explore project files

**📋 Available Scripts:**

1. `gemini_analyzer.py` - AI-powered product identification using Google Gemini API
2. `openai_analyzer.py` - Advanced product analysis using OpenAI GPT-4 Vision
3. `image_analyzer.py` - Identifies products from photos using Google Vision API
4. `price_researcher.py` - Searches marketplaces for similar items and pricing
5. `ai_pricing_engine.py` - Advanced AI-powered pricing analysis
6. `ebay_api_researcher.py` - eBay marketplace research using official Browse API
7. `ebay_image_lookup.py` - Visual search on eBay using image recognition

## Quick Start

```bash
# Clone and setup
git clone https://github.com/yourusername/pickprice-app
cd pickprice-app

# Install dependencies with uv
uv sync

# Set up your API keys
export ANTHROPIC_API_KEY="your_anthropic_key"
export GOOGLE_AI_API_KEY="your_google_ai_key"
export OPENAI_API_KEY="your_openai_key"

# Try the AI agent! (recommended)
python agent/main.py

# Try individual scripts:
uv run scripts/gemini_analyzer.py examples/cat.jpeg
uv run scripts/openai_analyzer.py examples/cat.jpeg
uv run scripts/image_analyzer.py examples/cat.jpeg
uv run scripts/ebay_api_researcher.py "cat litter box"

# Example agent commands:
# "Please analyze this image with OpenAI: examples/cat.jpeg"
# "Compare Gemini and OpenAI analysis for examples/cat.jpeg"
# "Analyze the image and then research similar items on eBay"
```

## Database Storage

**🗄️ SQLite Database for eBay Data**

All eBay API results are automatically stored in a SQLite database for historical analysis and trend tracking. This solves the problem of eBay not storing past listings.

Key features: automatic storage, price trends, search history, and smart deduplication.

**📋 See [db/README.md](db/README.md) for complete database documentation.**

## Project Structure

```
pickprice/
├── agent/            # AI agent system
│   └── main.py       # Claude-powered pricing agent with tools
├── lib/              # Core library code
│   ├── analyzers/    # Reusable analyzer classes
│   ├── browseapi/    # 🆕 eBay Browse API client
│   └── database/     # 🆕 SQLite database for eBay data storage
├── tools/            # Agent tool wrappers
│   ├── __init__.py
│   ├── base.py       # Tool definition structure
│   ├── file_system.py # File operations
│   ├── gemini_analyzer.py # Gemini tool wrapper
│   ├── openai_analyzer.py # OpenAI tool wrapper
│   ├── vision_analyzer.py # Google Vision tool wrapper
│   └── ebay_researcher.py # eBay research tool wrapper
├── scripts/          # Command-line interface scripts
│   ├── gemini_analyzer.py # CLI for Gemini analysis
│   ├── openai_analyzer.py # CLI for OpenAI analysis
│   ├── image_analyzer.py
│   ├── price_researcher.py
│   ├── ai_pricing_engine.py
│   ├── ebay_api_researcher.py # eBay marketplace research
│   └── ebay_image_lookup.py # eBay visual search
├── examples/         # Sample images for testing
├── tests/            # Test cases and regression testing
│   └── test-cases.md # Documented test scenarios
├── logs/             # Analysis results and logs
└── pyproject.toml    # Python dependencies managed by uv
```

## Environment Variables

```env
# Required for Claude (base agent)
ANTHROPIC_API_KEY=your_anthropic_key

# Required for Gemini and OpenAI (tool calls)
GOOGLE_AI_API_KEY=your_google_ai_key
OPENAI_API_KEY=your_openai_key

# eBay Browse API Secrets
EBAY_SANDBOX_APP_ID=your_sandbox_app_id
EBAY_SANDBOX_CERT_ID=your_sandbox_cert_id
EBAY_PROD_APP_ID=your_prod_app_id
EBAY_PROD_CERT_ID=your_prod_cert_id
EBAY_USE_SANDBOX=true                  # Set to false for production

# Optional for future features
GOOGLE_VISION_API_KEY=your_api_key
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

## Testing & Quality

We maintain quality through documented test cases in `tests/test-cases.md`:

```bash
# Example test: Image analysis
# Input: "Please analyze this image: examples/cat.jpeg"
# Expected: Agent chooses appropriate vision tool (Gemini or OpenAI)
```

**Test Categories:**

- Image analysis and product identification
- File system navigation and code exploration
- Multi-step workflows and tool chaining
- Error handling and edge cases

Run test cases manually when making changes to ensure consistent behavior.

## Code Quality

We maintain high code quality standards using **Ruff** for linting and formatting:

```bash
# Automatically fix linting issues and format code
ruff check --fix . && ruff format .

# Or just commit - pre-commit hooks handle it automatically!
git commit -m "Your changes"
```

**Pre-commit hooks** automatically run on every commit to:

- ✅ Check and fix code style with Ruff
- ✅ Format code consistently
- ✅ Remove trailing whitespace
- ✅ Fix end-of-file formatting
- ✅ Check for merge conflicts

**Setup for new contributors:**

```bash
# Install dev dependencies
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install

# Optional: Run hooks on all files
uv run pre-commit run --all-files
```

## Contributing

This is a collaborative project! Feel free to:

- Add feature ideas to `IDEAS.md`
- Submit PRs for improvements
- Add test cases

## License

MIT License - feel free to use and modify
