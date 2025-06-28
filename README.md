# PickPrice - Visual Product Pricing App

_Take a photo, get smart pricing for your resale items_

## What is PickPrice?

PickPrice helps you resell items by taking a simple photo and getting intelligent pricing recommendations. Perfect for clothes, electronics, collectibles, and more across platforms like eBay, Depop, Facebook Marketplace, and Mercari.

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
- **`lib/`** - Core reusable analyzer classes (GeminiAnalyzer, etc.)
- **`tools/`** - Agent tool wrappers that use lib classes
- **`scripts/`** - CLI interfaces for standalone usage
- **`agent/`** - Main conversational AI that orchestrates tools
- **`tests/`** - Documented test cases for regression testing

**🛠️ Agent Tools:**
- **Gemini Vision Analysis** - Google's AI for product identification from photos
- **File System Tools** - Read and explore project files
- **Future Tools** - Price research, market analysis, and more

**📋 Available Scripts:**
1. `gemini_analyzer.py` - AI-powered product identification using Google Gemini API
2. `image_analyzer.py` - Identifies products from photos using Google Vision API
3. `price_researcher.py` - Searches marketplaces for similar items and pricing
4. `ai_pricing_engine.py` - Advanced AI-powered pricing analysis
5. `ebay_api_researcher.py` - eBay marketplace research and pricing data

## Current Status

🤖 **AI Agent Phase** - Claude as the main pricing agent with clean modular tools
🏗️ **Clean Architecture** - Separated library code, tools, and CLI interfaces
🧪 **Quality Assurance** - Documented test cases for regression testing
🔬 **Proof-of-Concept Phase** - Building simple scripts to validate ideas

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

# Try the AI agent! (recommended)
python agent/main.py

# Or try individual scripts:
uv run scripts/gemini_analyzer.py examples/cat.jpeg
uv run scripts/image_analyzer.py examples/cat.jpeg
```

## Project Structure

```
pickprice/
├── agent/            # AI agent system
│   └── main.py       # Claude-powered pricing agent with tools
├── lib/              # Core library code
│   └── analyzers/    # Reusable analyzer classes
│       ├── __init__.py
│       └── gemini.py # Gemini AI product analysis
├── tools/            # Agent tool wrappers
│   ├── __init__.py
│   ├── base.py       # Tool definition structure
│   ├── file_system.py # File operations
│   └── gemini_analyzer.py # Gemini tool wrapper
├── scripts/          # Command-line interface scripts
│   ├── gemini_analyzer.py # CLI for Gemini analysis
│   ├── image_analyzer.py
│   ├── price_researcher.py
│   ├── ai_pricing_engine.py
│   └── ebay_api_researcher.py
├── examples/         # Sample images for testing
├── tests/            # Test cases and regression testing
│   └── test-cases.md # Documented test scenarios
├── logs/             # Analysis results and logs
└── pyproject.toml    # Python dependencies managed by uv
```

## Environment Variables

```env
# Required for AI agent
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_AI_API_KEY=your_google_ai_key

# Optional for future features
GOOGLE_VISION_API_KEY=your_api_key
EBAY_API_KEY=your_ebay_key
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

## Testing & Quality

We maintain quality through documented test cases in `tests/test-cases.md`:

```bash
# Example test: Image analysis
# Input: "Please analyze this image: examples/cat.jpeg"
# Expected: Gemini tool usage with structured product analysis
```

**Test Categories:**
- Image analysis and product identification
- File system navigation and code exploration
- Multi-step workflows and tool chaining
- Error handling and edge cases

Run test cases manually when making changes to ensure consistent behavior.

## Contributing

This is a collaborative project! Feel free to:

- Add feature ideas to `IDEAS.md`
- Pick up tasks from `TODO.md`
- Submit PRs for improvements
- Run test cases when making changes

## License

MIT License - feel free to use and modify

---

_Built with love for the reselling community_ 💜
