#!/usr/bin/env python3
"""Run the prompt optimizer.

Usage:
    python scripts/run_optimizer.py --iterations 3
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from optimizer.optimize_prompt import optimize_sync


def main() -> None:
    parser = argparse.ArgumentParser(description="Run prompt optimizer")
    parser.add_argument(
        "--iterations", "-n",
        type=int,
        default=3,
        help="Number of optimization iterations (default: 3)",
    )
    args = parser.parse_args()

    print()
    print("=" * 60)
    print("  BugFix Agent — Prompt Optimizer")
    print(f"  Iterations: {args.iterations}")
    print("=" * 60)
    print()

    optimize_sync(iterations=args.iterations)


if __name__ == "__main__":
    main()
