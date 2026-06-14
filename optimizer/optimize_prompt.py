"""Prompt optimizer — uses eval results to improve the system prompt."""

from __future__ import annotations

import json
import os
from datetime import datetime
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

from bugfix_agent.config import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_BASE_URL,
    REASONING_MODEL,
)
from evals.run_eval import run_eval


PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"
VERSIONS_DIR = PROMPTS_DIR / "versions"
REPORTS_DIR = Path(__file__).resolve().parent / "reports"


async def suggest_improved_prompt(
    current_prompt: str,
    eval_output: dict,
    optimizer_prompt_path: Optional[str] = None,
) -> str:
    """Use REASONING_MODEL to suggest an improved system prompt."""
    os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
    os.environ["ANTHROPIC_BASE_URL"] = ANTHROPIC_BASE_URL

    if optimizer_prompt_path:
        meta_prompt = Path(optimizer_prompt_path).read_text(encoding="utf-8")
    else:
        meta_prompt = (PROMPTS_DIR / "optimizer_prompt.txt").read_text(encoding="utf-8")

    metrics = eval_output.get("metrics", {})
    results = eval_output.get("results", [])
    failures = [r for r in results if not r.get("fixed", False)]
    failure_summary = json.dumps(failures, indent=2) if failures else "No failures."

    user_prompt = (
        f"## Current System Prompt\n"
        f"```\n{current_prompt}\n```\n\n"
        f"## Eval Metrics\n"
        f"```json\n{json.dumps(metrics, indent=2)}\n```\n\n"
        f"## Failure Details\n"
        f"```json\n{failure_summary}\n```\n\n"
        f"Produce an improved system prompt."
    )

    options = ClaudeAgentOptions(
        system_prompt=meta_prompt,
        allowed_tools=[],
        model=REASONING_MODEL,
        max_turns=1,
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

    return "\n".join(output_parts).strip()


async def optimize(
    iterations: int = 3,
    dataset_dir: Optional[Path] = None,
) -> dict:
    """Run the optimization loop.

    1. Run baseline eval with current prompt.
    2. For each iteration:
       a. Analyse failures with REASONING_MODEL.
       b. Save improved prompt as a new version.
       c. Re-run eval with improved prompt.
    3. Select the best prompt.
    4. Save before/after report.
    """
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    prompt_path = PROMPTS_DIR / "system_prompt.txt"
    current_prompt = prompt_path.read_text(encoding="utf-8")

    # Save baseline prompt
    baseline_version = VERSIONS_DIR / "v0_baseline.txt"
    baseline_version.write_text(current_prompt, encoding="utf-8")

    # Run baseline eval
    print("\n" + "=" * 60)
    print("  BASELINE EVAL")
    print("=" * 60)
    baseline_eval = await run_eval(
        dataset_dir=dataset_dir,
        system_prompt_path=str(prompt_path),
        label="baseline",
    )

    history = [
        {
            "version": "v0_baseline",
            "score": baseline_eval["metrics"]["overall_score"],
            "prompt_path": str(baseline_version),
            "eval_output": baseline_eval,
        }
    ]

    best_score = baseline_eval["metrics"]["overall_score"]
    best_version = "v0_baseline"
    best_prompt_path = str(baseline_version)

    for i in range(1, iterations + 1):
        print(f"\n{'='*60}")
        print(f"  OPTIMIZATION ITERATION {i}/{iterations}")
        print(f"{'='*60}")

        prev_eval = history[-1]["eval_output"]

        try:
            improved_prompt = await suggest_improved_prompt(current_prompt, prev_eval)
        except Exception as exc:
            print(f"  ⚠️ Optimizer failed: {exc}")
            continue

        if not improved_prompt.strip():
            print("  ⚠️ Empty prompt returned, skipping iteration.")
            continue

        version_name = f"v{i}_optimized"
        version_path = VERSIONS_DIR / f"{version_name}.txt"
        version_path.write_text(improved_prompt, encoding="utf-8")
        prompt_path.write_text(improved_prompt, encoding="utf-8")
        current_prompt = improved_prompt

        eval_output = await run_eval(
            dataset_dir=dataset_dir,
            system_prompt_path=str(version_path),
            label=f"optimized_v{i}",
        )

        score = eval_output["metrics"]["overall_score"]
        history.append({
            "version": version_name,
            "score": score,
            "prompt_path": str(version_path),
            "eval_output": eval_output,
        })

        if score > best_score:
            best_score = score
            best_version = version_name
            best_prompt_path = str(version_path)
            print(f"  🎯 New best: {best_version} (score: {best_score:.1%})")
        else:
            print(f"  📊 Score: {score:.1%} (best: {best_version} {best_score:.1%})")

    # Restore best prompt
    best_content = Path(best_prompt_path).read_text(encoding="utf-8")
    prompt_path.write_text(best_content, encoding="utf-8")

    report = {
        "timestamp": datetime.now().isoformat(),
        "iterations": iterations,
        "best_version": best_version,
        "best_score": best_score,
        "baseline_score": history[0]["score"],
        "improvement": best_score - history[0]["score"],
        "score_progression": [
            {"version": h["version"], "score": h["score"]}
            for h in history
        ],
    }

    report_path = REPORTS_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"  OPTIMIZATION COMPLETE")
    print(f"{'='*60}")
    print(f"  Baseline Score:  {history[0]['score']:.1%}")
    print(f"  Best Score:      {best_score:.1%}")
    print(f"  Best Version:    {best_version}")
    print(f"  Improvement:     {report['improvement']:+.1%}")
    print(f"  Report:          {report_path}")
    print()

    return report


def optimize_sync(iterations: int = 3, dataset_dir: Optional[Path] = None) -> dict:
    """Synchronous wrapper for optimize."""
    return anyio.run(lambda: optimize(iterations, dataset_dir))
