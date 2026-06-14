#!/usr/bin/env python3
"""Test connection to OpenRouter via Claude Agent SDK.

Sends a trivial query to verify credentials, model, and SDK integration.
Does NOT print API keys.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import anyio
from claude_agent_sdk import (
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ResultMessage,
    query,
)

from bugfix_agent.config import (
    ANTHROPIC_BASE_URL,
    MODEL,
)


async def main() -> None:
    print("=" * 52)
    print("  BugFix Agent — Connection Test")
    print("=" * 52)
    print(f"  Base URL : {ANTHROPIC_BASE_URL}")
    print(f"  Model    : {MODEL}")
    print(f"  API Key  : [hidden]")
    print("=" * 52)
    print()
    print("Sending: 'What is 2 + 2? Reply with just the number.'")
    print()

    options = ClaudeAgentOptions(
        allowed_tools=[],
        model=MODEL,
        max_turns=1,
    )

    got_response = False
    error_text = None

    try:
        async for message in query(
            prompt="What is 2 + 2? Reply with just the number.",
            options=options,
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock) and block.text.strip():
                        print(f"  Agent response: {block.text.strip()}")
                        got_response = True
            elif isinstance(message, ResultMessage):
                # ResultMessage has .result (str), not .content
                if message.is_error:
                    error_text = message.result or "Unknown error"
                elif message.result and message.result.strip():
                    print(f"  Result: {message.result.strip()}")
                    got_response = True
    except Exception as exc:
        print(f"  ❌ Exception: {exc}")
        sys.exit(1)

    print()
    if error_text:
        print(f"  ❌ Model returned error: {error_text}")
        sys.exit(1)
    elif got_response:
        print("  ✅ Connection successful — SDK is working!")
    else:
        print("  ⚠️  Connected but got no visible text response.")
        print("      This is normal for some tool-use-only responses.")
        print("  ✅ Connection OK")
    print()


if __name__ == "__main__":
    anyio.run(main)
