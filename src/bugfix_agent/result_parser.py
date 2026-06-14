"""Parse agent text output into a structured RepairResult."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from bugfix_agent.schemas import RepairResult
from bugfix_agent.test_runner import TestRunResult


def build_result(
    buggy_file: Path,
    test_file: Path,
    test_run: TestRunResult,
    iteration: int,
    original_test_hash: str,
    patch_summary: str,
) -> RepairResult:
    """Construct a RepairResult from the final test-run state."""
    current_test_hash = _file_hash(test_file)
    modified = current_test_hash != original_test_hash

    return RepairResult(
        file=buggy_file.name,
        test_file=test_file.name,
        fixed=test_run.passed > 0 and test_run.failed == 0 and test_run.errors == 0,
        iterations=iteration,
        tests_total=test_run.total,
        tests_passing=test_run.passed,
        tests_failing=test_run.failed + test_run.errors,
        patch_summary=patch_summary,
        modified_test_file=modified,
        timed_out=test_run.timed_out,
        syntax_error=_looks_like_syntax_error(test_run),
    )


def extract_patch_summary(agent_output: str) -> str:
    """Best-effort extraction of patch summary from agent text."""
    # Try to find JSON with patch_summary key
    json_match = re.search(r'\{[^{}]*\"patch_summary\"[^{}]*\}', agent_output, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group())
            return data.get("patch_summary", "")
        except json.JSONDecodeError:
            pass

    # Fallback: return last non-empty line
    lines = [ln.strip() for ln in agent_output.strip().splitlines() if ln.strip()]
    if lines:
        return lines[-1][:200]
    return ""


def _file_hash(path: Path) -> str:
    """Simple hash of file contents for tamper detection."""
    import hashlib
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except FileNotFoundError:
        return ""


def _looks_like_syntax_error(test_run: TestRunResult) -> bool:
    """Heuristic: did the test run fail due to a SyntaxError?"""
    combined = test_run.stdout + test_run.stderr
    return "SyntaxError" in combined or "IndentationError" in combined
