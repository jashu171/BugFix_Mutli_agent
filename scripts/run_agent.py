#!/usr/bin/env python3
"""Run the bug-fix agent on a single case.

Usage:
    python scripts/run_agent.py <buggy_file> <test_file>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bugfix_agent.repair_loop import repair_sync


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BugFix agent on a single case")
    parser.add_argument("buggy_file", type=Path, help="Path to the buggy Python file")
    parser.add_argument("test_file", type=Path, help="Path to the test file")
    parser.add_argument(
        "--max-iterations", "-n",
        type=int,
        default=None,
        help="Maximum repair iterations (default: from config)",
    )
    args = parser.parse_args()

    buggy_file = args.buggy_file.resolve()
    test_file = args.test_file.resolve()

    if not buggy_file.exists():
        print(f"Error: {buggy_file} not found")
        sys.exit(1)
    if not test_file.exists():
        print(f"Error: {test_file} not found")
        sys.exit(1)

    print()
    print("=" * 60)
    print("  BugFix Agent — Single Repair")
    print("=" * 60)
    print(f"  Buggy file: {buggy_file}")
    print(f"  Test file:  {test_file}")
    print("=" * 60)
    print()

    result = repair_sync(
        buggy_file=buggy_file,
        test_file=test_file,
        max_iterations=args.max_iterations,
    )

    print()
    print("=" * 60)
    print("  RESULT")
    print("=" * 60)
    print(result.to_json(indent=2))
    print()


if __name__ == "__main__":
    main()
