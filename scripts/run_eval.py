#!/usr/bin/env python3
"""Run the full eval harness across all dataset cases.

Usage:
    python scripts/run_eval.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evals.run_eval import run_eval_sync


def main() -> None:
    print()
    print("=" * 60)
    print("  BugFix Agent — Eval Harness")
    print("=" * 60)
    print()

    run_eval_sync(label="eval")


if __name__ == "__main__":
    main()
