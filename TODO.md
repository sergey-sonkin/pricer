Todos:

- Pick out 5 more images to use as test examples
- Train the agent to ask users clarifying questions
- Add ebay researcher test case
- Enable ebay image lookup as tool
- Look into using real ebay production

2025/07/12:

- Update system prompt to improve ebay searching (agent now tries multiple searches)
- Added 4 test images directly from eBay listings
- Add debug flag to agent to view results of tool calls

2025/07/07:

- Clean up try-except imports
- Download images from eBay training set (https://github.com/eBay/ImageGuidedTranslationDataset)

2025/07/06:

- Store ebay results in sqlite db
- Confirm sqlite db works as intended with agent runs
- Add OpenAI vision model

2025/07/05:

- Add agent support to use the google vision tool
- Refactor ebayAPI researcher to use lib/ rather than scripts/
- Added Example 1 (Apple iPad Mini 6th Gen 64GB)
- Support multiple images (turns out this just works natively! tested and happy with result)
- Add sqlite db for storing ebay listings, tests, scripts

2025/07/04:

- Test eBay API script with new keys
- Migrate to eBay Browse API
- Add eBay Browse to agent
- Implement system prompt
- Allow agent to iterate with multiple tools
- Add tool to use google vision api
