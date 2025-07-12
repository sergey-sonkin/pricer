import json
import os
import sys
from collections.abc import Callable
from typing import Any

from anthropic import Anthropic

# Add tools directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from tools import ALL_TOOLS, ToolDefinition


class Agent:
    def __init__(
        self,
        client: Anthropic,
        get_user_message: Callable[[], tuple[str, bool]],
        tools: list[ToolDefinition],
    ):
        self.client = client
        self.get_user_message = get_user_message
        self.tools = tools

    def run(self):
        conversation = []

        print("Chat with Claude (use 'ctrl-c' to quit)")

        read_user_input = True
        while True:
            if read_user_input:
                print("\033[94mYou\033[0m: ", end="")
                user_input, ok = self.get_user_message()
                if not ok:
                    break

                user_message = {"role": "user", "content": user_input}
                conversation.append(user_message)

            message = self._run_inference(conversation)
            conversation.append({"role": "assistant", "content": message.content})

            tool_results = []
            for content in message.content:
                if content.type == "text":
                    print(f"\033[93mClaude\033[0m: {content.text}")
                elif content.type == "tool_use":
                    result = self._execute_tool(content.id, content.name, content.input)
                    tool_results.append(result)

            if len(tool_results) == 0:
                read_user_input = True
                continue

            read_user_input = False
            conversation.append({"role": "user", "content": tool_results})

    def _execute_tool(
        self, tool_id: str, name: str, tool_input: dict[str, Any]
    ) -> dict[str, Any]:
        tool_def = None
        for tool in self.tools:
            if tool.name == name:
                tool_def = tool
                break

        if tool_def is None:
            return {
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": "Tool not found",
                "is_error": True,
            }

        print(f"\033[92mtool\033[0m: {name}({json.dumps(tool_input)})")
        try:
            response = tool_def.function(tool_input)
            return {
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": response,
                "is_error": False,
            }
        except Exception as e:
            return {
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": str(e),
                "is_error": True,
            }

    def _run_inference(self, conversation: list[dict[str, Any]]):
        anthropic_tools = []
        for tool in self.tools:
            anthropic_tools.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                }
            )

        # Add system prompt to define the agent's role and purpose
        system_prompt = """You are PicPrice, an AI assistant specialized in helping users resell items by providing intelligent pricing recommendations and market analysis.

Your primary purpose is to help users:
- Identify products from photos using computer vision
- Research current market prices and trends
- Provide strategic pricing recommendations for resale platforms
- Analyze market data from eBay and other marketplaces

You have access to several tools:
- **Gemini Analyzer**: AI-powered product identification and market analysis from images (Google' Gemini API)
- **OpenAI Analyzer**: AI-powered product identification and market analysis from images (OpenAI's gpt-4o-mini)
- **Google Vision Analyzer**: Detailed feature extraction including labels, objects, text, and brand detection from images (Google Vision API)
- **eBay Researcher**: Search for products on eBay and retrieve current market data
- **File System Tools**: Read files and explore the project structure
- And of course - asking the user questions!

## eBay Research Strategy - BE PERSISTENT AND STRATEGIC

When researching products on eBay, act like a experienced reseller who doesn't give up easily:

**ALWAYS try multiple search approaches:**
1. **Start specific**: Use exact product details (brand + model + specifications)
2. **Go broader**: Use general product category if specific search yields few results
3. **Try variations**: Use synonyms, alternative names, common misspellings
4. **Search related items**: If exact match fails, search for similar/comparable products
5. **Remove constraints**: Drop specifications one by one (size, color, condition) to broaden results

**Search term strategies to try:**
- Brand + specific model (e.g., "iPhone 12 Pro 128GB")
- Generic category (e.g., "smartphone unlocked")
- Product type + key feature (e.g., "wireless earbuds noise canceling")
- Used/vintage/collectible variations when applicable
- Remove brand if getting no results
- Try both technical and common names

**Persistence guidelines:**
- If first search has <5 results, try broader terms
- If no results, try completely different keyword approach
- Always attempt 2-3 different search strategies minimum
- Combine searches to build comprehensive market picture
- Don't give up until you've tried multiple approaches

**Example search progression:**
1. "Apple iPad Mini 6th Generation 64GB WiFi" → few results
2. "iPad Mini 6th generation" → more results
3. "iPad Mini 64GB" → broader market data
4. "Apple tablet 8 inch" → alternative perspective

Remember: Real resellers are persistent researchers. One failed search never stops them from finding market data.

Be helpful, accurate, and focused on practical resale advice. Always explain your reasoning and provide actionable insights."""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=conversation,
            tools=anthropic_tools,
            system=system_prompt,
        )
        return message


def get_user_message() -> tuple[str, bool]:
    try:
        user_input = input()
        return user_input, True
    except (EOFError, KeyboardInterrupt):
        return "", False


def new_agent(
    client: Anthropic,
    get_user_message_func: Callable[[], tuple[str, bool]],
    tools: list[ToolDefinition],
) -> Agent:
    return Agent(client, get_user_message_func, tools)


def main():
    client = Anthropic()  # Uses ANTHROPIC_API_KEY environment variable

    agent = new_agent(client, get_user_message, ALL_TOOLS)

    try:
        agent.run()
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
