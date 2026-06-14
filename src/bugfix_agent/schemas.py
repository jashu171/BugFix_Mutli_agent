"""Data models for agent repair results."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional
import json


@dataclass
class RepairResult:
    """Structured result of one agent repair run."""

    file: str
    test_file: str
    fixed: bool = False
    iterations: int = 0
    tests_total: int = 0
    tests_passing: int = 0
    tests_failing: int = 0
    patch_summary: str = ""
    modified_test_file: bool = False
    error: Optional[str] = None
    timed_out: bool = False
    syntax_error: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict) -> "RepairResult":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class EvalMetrics:
    """Aggregated evaluation metrics across a dataset."""

    overall_score: float = 0.0
    full_fix_rate: float = 0.0
    partial_pass_rate: float = 0.0
    files_fully_fixed: int = 0
    files_partially_fixed: int = 0
    files_failed: int = 0
    average_iterations: float = 0.0
    syntax_error_rate: float = 0.0
    timeout_rate: float = 0.0
    test_file_modified_rate: float = 0.0
    total_cases: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
