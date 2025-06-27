# Logs Directory

This directory contains output files from various PickPrice scripts.

## Structure

```
logs/
├── image_analyzer/        # Google Vision API analysis results
├── gemini_analyzer/       # Gemini AI analysis results  
├── price_researcher/      # Web scraping price research
├── ebay_api_researcher/   # eBay API research results
├── ai_pricing_engine/     # AI pricing estimates (future)
└── old_files/            # Legacy files moved from root
```

## File Naming Convention

All log files follow the pattern:
`{script_name}_{product_name}_{timestamp}.json`

Examples:
- `image_analyzer/shirt_analysis_1750890123.json`
- `gemini_analyzer/cat_gemini_analysis_1750890124.json`
- `price_researcher/price_analysis_1750890125.json`

## Cleanup

Log files are automatically timestamped. You can safely delete old files when:
- Testing is complete
- Data is no longer needed
- Directory becomes too large

The scripts will automatically create these directories as needed.