"""Core agent — wraps Claude Agent SDK to perform bug-fixing queries."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import anyio
from claude_agent_sdk import (
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ResultMessage,
    query,
)

from bugfix_agent.config import ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL, MODEL


def _load_system_prompt(override_path: Optional[str] = None) -> str:
    """Load the system prompt from disk."""
    if override_path:
        path = Path(override_path)
    else:
        path = Path(__file__).resolve().parents[2] / "prompts" / "system_prompt.txt"
    return path.read_text(encoding="utf-8").strip()


async def run_agent(
    buggy_file: Path,
    test_file: Path,
    work_dir: Path,
    system_prompt_path: Optional[str] = None,
) -> str:
    """Send a single bug-fix query to Claude via the Agent SDK.

    The agent is given:
      - The full source of the buggy file
      - The full source of the test file
      - Instructions to read, analyse, fix, and re-test

    Returns:
        The concatenated text output from the agent.
    """
    # Inject OpenRouter env vars so the SDK subprocess picks them up
    os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
    os.environ["ANTHROPIC_BASE_URL"] = ANTHROPIC_BASE_URL

    system_prompt = _load_system_prompt(system_prompt_path)

    buggy_content = buggy_file.read_text(encoding="utf-8")
    test_content = test_file.read_text(encoding="utf-8")

    user_prompt = (
        f"You are a test-driven bug-fixing agent.\n\n"
        f"## Buggy source file: {buggy_file.name}\n"
        f"Path: {buggy_file}\n"
        f"```python\n{buggy_content}\n```\n\n"
        f"## Test file: {test_file.name}\n"
        f"Path: {test_file}\n"
        f"```python\n{test_content}\n```\n\n"
        f"## Instructions\n"
        f"1. Run the tests with: python -m pytest {test_file} -v --tb=short\n"
        f"2. Analyse failures carefully.\n"
        f"3. Edit ONLY the buggy source file at {buggy_file} to fix the bug.\n"
        f"4. Do NOT edit the test file at {test_file}.\n"
        f"5. Re-run tests to verify the fix.\n"
        f"6. Make minimal, surgical changes.\n"
        f"7. After fixing, output a short JSON summary:\n"
        f'   {{"patch_summary": "description of what you fixed"}}\n'
    )

    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        allowed_tools=["Read", "Write", "Edit", "Bash"],
        permission_mode="acceptEdits",
        cwd=str(work_dir),
        model=MODEL,
        max_turns=15,
    )

    output_parts: list[str] = []

    async for message in query(prompt=user_prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    output_parts.append(block.text)
        elif isinstance(message, ResultMessage):
            # ResultMessage has .result (str), not .content
            if message.result and not message.is_error:
                output_parts.append(message.result)

    return "\n".join(output_parts)
