# PicPrice Agent Test Cases

This document contains test cases for regression testing the PicPrice AI agent. Since AI responses can vary, these cases help us detect significant changes in behavior and ensure quality remains consistent.

## How to Use This Document

1. **Run test cases** manually when making changes to the agent or underlying tools
2. **Compare outputs** with the documented expected behavior
3. **Evaluate changes** - are they improvements, regressions, or acceptable variations?
4. **Update baselines** when intentional improvements are made

## Test Cases

### TC-001: Basic Product Image Analysis

**Date Recorded:** 2024-06-28
**Input:** `Please analyze this image: examples/cat.jpeg`
**Expected Behavior:** Agent should use the Gemini analyzer tool to identify the cat toy/product and provide structured analysis

**Expected Tool Call:**

```
analyze_image_with_gemini({"image_path": "examples/cat.jpeg"})
```

**Expected Output Structure:**

- Product description (should identify as cat-related item)
- Product type classification
- Market category suggestion
- Condition assessment (if visible)
- Notable features
- Pricing factors
- Confidence level

**Baseline Output (2024-06-28):**

```
🤖 Gemini AI Analysis for: cat.jpeg

🎯 Confidence Level: Medium

📝 Product Description:
A used, gray and white plastic cat litter box.  The litter box appears to be in good condition but has some minor wear from use, indicated by slight discoloration and surface markings.  A small amount of cat urine is visible on the floor next to it.

📦 Product Type: Pet Supplies
🏪 Market Category: Pet Supplies > Cat Supplies > Litter Boxes & Accessories
🏢 Brand: null
⭐ Condition: Good

✨ Notable Features:
• Gray and white plastic construction
• Shows signs of minor use and wear
• Size appears to be standard for a single cat

💰 Pricing Factors:
• Brand (if identified)
• Size of litter box
• Overall condition
• Pre-owned condition: presence of minor wear and visible urine
• Market demand for used litter boxes
• Competition from similar products on the resale platform
```

**Notes:**

- Should correctly identify this as a cat-related product (litter box, not toy as initially assumed)
- Should provide relevant marketplace suggestions (pet supplies)
- Confidence should be reasonable given image quality

---

### TC-002: File System Navigation

**Date Recorded:** 2024-06-28
**Input:** `What files are in the examples directory?`
**Expected Behavior:** Agent should use list_files tool to show directory contents

**Expected Tool Call:**

```
list_files({"path": "examples"})
```

**Expected Output:**

- Should list files in examples/ directory
- Should include cat.jpeg and any other example files
- Clean, formatted response

**Baseline Output (2024-06-28):**

```
Files in examples directory:
cat.jpeg
```

---

### TC-003: Code Exploration

**Date Recorded:** 2024-06-28
**Input:** `Show me how the Gemini analyzer tool is implemented`
**Expected Behavior:** Agent should use read_file tool to examine relevant files

**Expected Tool Call:**

```
read_file({"path": "tools/gemini_analyzer.py"})
```

**Expected Output:**

- Should read and summarize the tool implementation
- May also explore lib/analyzers/gemini.py
- Should explain the architecture

**Baseline Output (2024-06-28):**

```
[TO BE FILLED - Run actual test]
```

---

### TC-004: Multi-step Product Analysis Workflow

**Date Recorded:** 2024-06-28
**Input:** `I want to sell this cat toy. First analyze the image examples/cat.jpeg, then tell me what marketplace would be best for selling it.`
**Expected Behavior:** Agent should chain multiple operations to provide comprehensive selling advice

**Expected Flow:**

1. Use analyze_image_with_gemini tool
2. Interpret results
3. Provide marketplace recommendations based on analysis
4. Suggest pricing strategy

**Baseline Output (2024-06-28):**

```
[TO BE FILLED - Run actual test]
```

**Notes:**

- Tests agent's ability to chain operations
- Tests practical use case scenario
- Should demonstrate understanding of resale context

---

## NEW: eBay Market Research Test Cases (January 2025)

### TC-005: eBay Market Research

**Date Recorded:** 2025-01-04
**Input:** `Research the market for "cat litter box" on eBay`
**Expected Behavior:** Should use eBay API researcher to get current market data

**Expected Script Usage:**
```bash
python scripts/ebay_api_researcher.py "cat litter box"
```

**Expected Output Structure:**
- Active listings count and data
- Price analysis (min, max, average, median)
- Market insights and trends
- Confidence score based on data availability
- JSON export with structured data

**Test Verification:**
1. Script should connect to eBay API successfully
2. Should retrieve active listings with price data
3. Should calculate meaningful statistics
4. Should save results to logs/ebay_api_researcher/
5. Should handle API errors gracefully

### TC-006: eBay Integration Test

**Date Recorded:** 2025-01-04
**Input:** `Can you research this product on eBay and tell me the market price?`
**Expected Behavior:** Future agent integration test

**Notes:**
- Will test agent's ability to use eBay research tool
- Should integrate with image analysis for complete workflow
- Currently pending agent tool wrapper implementation

## Proposed Additional Test Cases

### TC-007: Error Handling - Invalid Image Path

**Input:** `Please analyze this image: nonexistent.jpg`
**Purpose:** Test error handling when image doesn't exist

### TC-008: Complex Pricing Question

**Input:** `What factors should I consider when pricing vintage electronics for resale?`
**Purpose:** Test general knowledge without tool usage

### TC-009: Mixed Request

**Input:** `List the files in the scripts directory and explain what the gemini_analyzer.py script does`
**Purpose:** Test multiple tool usage in sequence

### TC-010: Architecture Understanding

**Input:** `Explain the difference between the lib/, tools/, and scripts/ directories in this project`
**Purpose:** Test agent's understanding of the codebase structure

---

## Test Execution Notes

- **Environment:** Ensure ANTHROPIC_API_KEY and GOOGLE_AI_API_KEY are set
- **Consistency:** Run tests from project root directory
- **Documentation:** Record any significant variations from expected behavior
- **Updates:** Update baselines when making intentional improvements

## Evaluation Criteria

**✅ Good Response:**

- Correct tool usage
- Accurate information
- Helpful and relevant
- Appropriate confidence levels

**⚠️ Review Needed:**

- Different tool usage pattern
- Significantly different output structure
- Changed confidence levels
- New or missing information

**❌ Regression:**

- Incorrect tool usage
- Factual errors
- Unhelpful responses
- Tool failures
