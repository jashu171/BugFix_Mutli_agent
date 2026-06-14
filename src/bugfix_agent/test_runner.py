"""Subprocess pytest runner — executes tests and captures results."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bugfix_agent.config import PYTEST_TIMEOUT_SECONDS


@dataclass
class TestRunResult:
    """Raw output of a pytest invocation."""

    return_code: int
    stdout: str
    stderr: str
    timed_out: bool = False
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0


def run_pytest(test_file: Path, cwd: Optional[Path] = None) -> TestRunResult:
    """Run pytest on *test_file* and return structured results.

    Args:
        test_file: Absolute or relative path to the pytest file.
        cwd: Working directory for the subprocess (defaults to test_file parent).

    Returns:
        TestRunResult with captured output and parsed pass/fail counts.
    """
    work_dir = str(cwd) if cwd else str(test_file.parent)

    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short", "--no-header"],
            capture_output=True,
            text=True,
            timeout=PYTEST_TIMEOUT_SECONDS,
            cwd=work_dir,
        )
        result = TestRunResult(
            return_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
        )
    except subprocess.TimeoutExpired:
        result = TestRunResult(
            return_code=-1,
            stdout="",
            stderr=f"pytest timed out after {PYTEST_TIMEOUT_SECONDS}s",
            timed_out=True,
        )

    _parse_summary(result)
    return result


def _parse_summary(result: TestRunResult) -> None:
    """Extract pass/fail/error counts from pytest verbose output."""
    for line in result.stdout.splitlines():
        lower = line.lower()
        if "passed" in lower or "failed" in lower or "error" in lower:
            parts = line.replace(",", " ").split()
            for i, tok in enumerate(parts):
                if tok == "passed":
                    result.passed = _safe_int(parts[i - 1])
                elif tok == "failed":
                    result.failed = _safe_int(parts[i - 1])
                elif tok in ("error", "errors"):
                    result.errors = _safe_int(parts[i - 1])
    result.total = result.passed + result.failed + result.errors


def _safe_int(s: str) -> int:
    try:
        return int(s)
    except ValueError:
        return 0
