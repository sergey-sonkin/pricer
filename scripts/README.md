# PicPrice Scripts

We have two different approaches to image analysis - choose based on your needs:

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
