"""Eval harness — runs the agent across the entire dataset and collects results."""

from __future__ import annotations

import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

import anyio

from bugfix_agent.repair_loop import repair
from bugfix_agent.schemas import RepairResult
from evals.metrics import compute_metrics


# Default paths
DATASET_DIR = Path(__file__).resolve().parents[1] / "dataset" / "cases"
RESULTS_DIR = Path(__file__).resolve().parent / "results"


def discover_cases(dataset_dir: Optional[Path] = None) -> list[Path]:
    """Find all case directories that contain buggy.py + test_buggy.py."""
    base = dataset_dir or DATASET_DIR
    cases = []
    for case_dir in sorted(base.iterdir()):
        if not case_dir.is_dir():
            continue
        buggy = case_dir / "buggy.py"
        test = case_dir / "test_buggy.py"
        if buggy.exists() and test.exists():
            cases.append(case_dir)
    return cases


async def run_eval(
    dataset_dir: Optional[Path] = None,
    system_prompt_path: Optional[str] = None,
    label: str = "eval",
) -> dict:
    """Run the full eval suite.

    For each case:
    1. Copy files into a temp directory (so the original dataset stays frozen).
    2. Run the repair loop.
    3. Collect results.

    Args:
        dataset_dir: Override dataset location.
        system_prompt_path: Override system prompt.
        label: Label for the results file.

    Returns:
        Dict with 'metrics' and 'results' keys.
    """
    cases = discover_cases(dataset_dir)
    results = []

    for case_dir in cases:
        print()
        print("=" * 60)
        print(f"  Case: {case_dir.name}")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            buggy_src = case_dir / "buggy.py"
            test_src = case_dir / "test_buggy.py"
            buggy_dst = tmp_path / "buggy.py"
            test_dst = tmp_path / "test_buggy.py"

            shutil.copy2(buggy_src, buggy_dst)
            shutil.copy2(test_src, test_dst)

            try:
                result = await repair(
                    buggy_file=buggy_dst,
                    test_file=test_dst,
                    work_dir=tmp_path,
                    system_prompt_path=system_prompt_path,
                )
            except Exception as exc:
                result = RepairResult(
                    file="buggy.py",
                    test_file="test_buggy.py",
                    error=str(exc),
                )

            results.append(result)

            status = "✅ FIXED" if result.fixed else "❌ FAILED"
            print(f"  Result: {status} | Iterations: {result.iterations}")
            if result.error:
                print(f"  Error: {result.error}")

    metrics = compute_metrics(results)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = {
        "label": label,
        "timestamp": timestamp,
        "metrics": metrics.to_dict(),
        "results": [r.to_dict() for r in results],
    }

    output_path = RESULTS_DIR / f"{label}_{timestamp}.json"
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print()
    print(f"  EVAL COMPLETE — {label}")
    print(f"{'=' * 60}")
    print(f"  Overall Score:     {metrics.overall_score:.1%}")
    print(f"  Full Fix Rate:     {metrics.full_fix_rate:.1%}")
    print(f"  Partial Pass Rate: {metrics.partial_pass_rate:.1%}")
    print(f"  Files Fixed:       {metrics.files_fully_fixed}/{metrics.total_cases}")
    print(f"  Avg Iterations:    {metrics.average_iterations:.1f}")
    print(f"  Results saved to:  {output_path}")
    print()

    return output


def run_eval_sync(
    dataset_dir: Optional[Path] = None,
    system_prompt_path: Optional[str] = None,
    label: str = "eval",
) -> dict:
    """Synchronous wrapper for run_eval."""
    return anyio.run(
        lambda: run_eval(dataset_dir, system_prompt_path, label)
    )
