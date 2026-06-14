"""Repair loop — orchestrates the read→test→fix→retest cycle."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

import anyio

from bugfix_agent.agent import run_agent
from bugfix_agent.config import MAX_REPAIR_ITERATIONS
from bugfix_agent.result_parser import build_result, extract_patch_summary
from bugfix_agent.schemas import RepairResult
from bugfix_agent.test_runner import run_pytest


def _file_hash(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except FileNotFoundError:
        return ""


async def repair(
    buggy_file: Path,
    test_file: Path,
    work_dir: Optional[Path] = None,
    system_prompt_path: Optional[str] = None,
    max_iterations: int | None = None,
) -> RepairResult:
    """Run the iterative repair loop.

    1. Run pytest to capture baseline failures.
    2. Ask the agent to fix the buggy file.
    3. Re-run pytest.
    4. If tests pass → return success.
    5. If tests still fail and iterations remain → repeat from step 2.
    6. After max iterations → return failure result.

    Args:
        buggy_file: Path to the buggy Python source.
        test_file: Path to the corresponding pytest file.
        work_dir: Working directory (defaults to buggy_file parent).
        system_prompt_path: Optional override for the system prompt.
        max_iterations: Override for MAX_REPAIR_ITERATIONS config.

    Returns:
        RepairResult with structured outcome.
    """
    _max = max_iterations if max_iterations is not None else MAX_REPAIR_ITERATIONS
    work = work_dir if work_dir is not None else buggy_file.parent
    original_test_hash = _file_hash(test_file)
    patch_summary = ""

    for iteration in range(1, _max + 1):
        # Run pytest to see current state
        test_run = run_pytest(test_file, cwd=work)

        # Check if tests already pass
        if test_run.passed > 0 and test_run.failed == 0 and test_run.errors == 0:
            patch_summary = patch_summary or "Tests already passing — no fix needed."
            return build_result(
                buggy_file, test_file, test_run,
                iteration=iteration,
                original_test_hash=original_test_hash,
                patch_summary=patch_summary,
            )

        # Ask agent to fix the bug
        try:
            agent_output = await run_agent(
                buggy_file, test_file, work,
                system_prompt_path=system_prompt_path,
            )
            patch_summary = extract_patch_summary(agent_output) or patch_summary
        except Exception as exc:
            return RepairResult(
                file=buggy_file.name,
                test_file=test_file.name,
                error=f"Agent error on iteration {iteration}: {exc}",
                iterations=iteration,
            )

        # Re-run tests after agent fix
        test_run = run_pytest(test_file, cwd=work)

        # If agent timed out, return immediately
        if test_run.timed_out:
            return build_result(
                buggy_file, test_file, test_run,
                iteration=iteration,
                original_test_hash=original_test_hash,
                patch_summary=patch_summary,
            )

        # Check if all tests pass now
        if test_run.passed > 0 and test_run.failed == 0 and test_run.errors == 0:
            return build_result(
                buggy_file, test_file, test_run,
                iteration=iteration,
                original_test_hash=original_test_hash,
                patch_summary=patch_summary,
            )

    # Exhausted all iterations — return last result
    return build_result(
        buggy_file, test_file, test_run,
        iteration=_max,
        original_test_hash=original_test_hash,
        patch_summary=patch_summary,
    )


def repair_sync(
    buggy_file: Path,
    test_file: Path,
    work_dir: Optional[Path] = None,
    system_prompt_path: Optional[str] = None,
    max_iterations: int | None = None,
) -> RepairResult:
    """Synchronous wrapper around the async repair loop."""
    return anyio.run(
        lambda: repair(buggy_file, test_file, work_dir, system_prompt_path, max_iterations)
    )
