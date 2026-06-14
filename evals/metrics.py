"""Eval metrics computation from a list of RepairResults."""

from __future__ import annotations

from bugfix_agent.schemas import EvalMetrics, RepairResult


def compute_metrics(results: list[RepairResult]) -> EvalMetrics:
    """Compute aggregate metrics from individual repair results.

    Args:
        results: List of RepairResult from eval run.

    Returns:
        EvalMetrics with computed values.
    """
    n = len(results)
    if n == 0:
        return EvalMetrics()

    fully_fixed = [r for r in results if r.fixed]
    partially_fixed = [r for r in results if not r.fixed and r.tests_passing > 0]
    failed = [r for r in results if not r.fixed and r.tests_passing == 0]

    total_iterations = sum(r.iterations for r in results)
    syntax_errors = sum(1 for r in results if r.syntax_error)
    timeouts = sum(1 for r in results if r.timed_out)
    test_modified = sum(1 for r in results if r.modified_test_file)

    full_fix_rate = len(fully_fixed) / n
    partial_rate = len(partially_fixed) / n

    overall_score = (len(fully_fixed) + 0.5 * len(partially_fixed)) / n

    return EvalMetrics(
        overall_score=round(overall_score, 4),
        full_fix_rate=round(full_fix_rate, 4),
        partial_pass_rate=round(partial_rate, 4),
        files_fully_fixed=len(fully_fixed),
        files_partially_fixed=len(partially_fixed),
        files_failed=len(failed),
        average_iterations=round(total_iterations / n, 2),
        syntax_error_rate=round(syntax_errors / n, 4),
        timeout_rate=round(timeouts / n, 4),
        test_file_modified_rate=round(test_modified / n, 4),
        total_cases=n,
    )
