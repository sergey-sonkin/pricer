Todos:

- Add OpenAI vision model
- Add better test images
- Enable ebay image lookup as tool
  - Write script testing ebay image lookup
- Improve ebay searching (agent currently uses a bunch of words at once, sees nothing, and gives up)
- Train the agent to ask users clarifying questions
- Add ebay researcher test case

2025/07/06:
- Store ebay results in sqlite db
- Confirm sqlite db works as intended with agent runs

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
