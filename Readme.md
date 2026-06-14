# BugFix Multi-Agent 🔧🤖

> **Proptimise AI — Agentic AI Engineer Take-Home Project**

A **test-driven bug-fixing agent** built with the [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python), featuring a complete **eval harness** and **prompt optimizer** that demonstrates measurable before/after improvement.

---

## What This Project Does

The agent receives two files — a **buggy Python source file** and its **pytest test file** — and autonomously fixes the bug until all tests pass. No hidden solution or answer key is provided; the agent must **infer the bug from the code and test failures alone**.

### Why This Is Agentic

This is not a simple prompt → response system. The agent exhibits **real agentic behavior**:

| Agentic Property | How It's Demonstrated |
|---|---|
| **Tool use** | Agent uses `Read`, `Write`, `Edit`, and `Bash` tools via Claude Code runtime |
| **Multi-step reasoning** | Reads code → runs tests → analyzes failures → forms hypothesis → applies fix → re-tests |
| **Iterative self-correction** | Up to 3 repair iterations with feedback from pytest output |
| **Environment interaction** | Executes pytest in a subprocess and reads real failure tracebacks |
| **Autonomous decision-making** | Agent decides *what* the bug is and *how* to fix it without human guidance |

### Why Claude Agent SDK (Not Raw API)

The assignment requires the **Claude Agent SDK framework**. This project uses `claude-agent-sdk` (not a raw OpenRouter/Anthropic chat-completions wrapper) because:

- The SDK provides a **full agent loop** with tool execution built in
- Tools like `Read`, `Write`, `Edit`, and `Bash` are handled by the **Claude Code CLI runtime** — the agent can actually read files, run commands, and edit code
- This is **real agentic tool use**, not simulated function calling
- Permission controls (`allowed_tools`, `permission_mode`) provide safety guardrails

---

## Architecture

```
BugFix Multi-Agent/
├── src/bugfix_agent/       # Core agent package
│   ├── config.py           # Environment config loader
│   ├── schemas.py          # RepairResult & EvalMetrics dataclasses
│   ├── agent.py            # Claude Agent SDK wrapper
│   ├── repair_loop.py      # Iterative fix loop orchestrator
│   ├── test_runner.py      # Subprocess pytest runner
│   └── result_parser.py    # Result builder & tamper detection
├── prompts/
│   ├── system_prompt.txt   # Agent system prompt (optimizable)
│   ├── optimizer_prompt.txt# Meta-prompt for optimizer
│   └── versions/           # Saved prompt versions
├── dataset/cases/          # 8 intentionally buggy Python files
│   ├── wrong_operator_01/
│   ├── off_by_one_02/
│   ├── none_handling_03/
│   ├── empty_list_04/
│   ├── inverted_logic_05/
│   ├── boundary_condition_06/
│   ├── sorting_filtering_07/
│   └── string_edge_case_08/
├── evals/
│   ├── run_eval.py         # Eval harness
│   ├── metrics.py          # Metric computation
│   └── results/            # Saved eval results (JSON)
├── optimizer/
│   ├── optimize_prompt.py  # Prompt optimizer
│   └── reports/            # Optimization reports
└── scripts/                # CLI entry points
    ├── test_connection.py
    ├── run_agent.py
    ├── run_eval.py
    └── run_optimizer.py
```

### Agent Loop Flow

```
┌─────────────────────────────────────────┐
│         Repair Loop (max 3 iters)       │
│                                         │
│  1. Run pytest → capture failures       │
│  2. Send to Claude Agent SDK            │
│     (buggy code + test code + failures) │
│  3. Agent uses tools:                   │
│     • Bash: run pytest                  │
│     • Read: inspect files               │
│     • Edit/Write: apply fix             │
│  4. Re-run pytest                       │
│  5. All pass? → Return success          │
│  6. Still failing? → Loop back to 2     │
│  7. Max iterations? → Return failure    │
│                                         │
│  Output: Structured RepairResult JSON   │
└─────────────────────────────────────────┘
```

---

## How OpenRouter Gateway Is Configured

The Claude Agent SDK communicates with models through environment variables:

```bash
ANTHROPIC_BASE_URL=https://openrouter.ai/api    # Routes SDK traffic through OpenRouter
ANTHROPIC_API_KEY=sk-or-v1-your-key-here         # Your OpenRouter API key
MODEL=qwen/qwen3-coder:free                      # Main bug-fixing model
REASONING_MODEL=openai/gpt-oss-120b:free          # Optimizer analysis model
```

The SDK's Claude Code CLI subprocess inherits these env vars, so all API calls go through OpenRouter transparently. No code changes are needed to switch providers — just change the env vars.

---

## Setup

### Prerequisites

- Python 3.10+
- Claude Code CLI (`claude --version` should work)
- OpenRouter API key ([get one here](https://openrouter.ai/keys))

### Install

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/BugFix-Multi-Agent.git
cd BugFix-Multi-Agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Configure credentials
cp .env.example .env
# Edit .env with your real API keys
```

### Configure Credentials

Edit `.env`:

```bash
OPENROUTER_API_KEY=sk-or-v1-your-actual-key
ANTHROPIC_BASE_URL=https://openrouter.ai/api
ANTHROPIC_API_KEY=sk-or-v1-your-actual-key
MODEL=qwen/qwen3-coder:free
REASONING_MODEL=openai/gpt-oss-120b:free
```

> ⚠️ Never commit `.env`. It's in `.gitignore`.

---

## Usage

### 1. Test Connection

Verify your API keys and model access:

```bash
python scripts/test_connection.py
```

### 2. Run One Repair

Fix a single buggy file:

```bash
python scripts/run_agent.py dataset/cases/wrong_operator_01/buggy.py dataset/cases/wrong_operator_01/test_buggy.py
```

Output: Structured JSON result with fix status, iterations, and test counts.

### 3. Run Eval Harness

Evaluate the agent across all 8 dataset cases:

```bash
python scripts/run_eval.py
```

Results are saved to `evals/results/eval_YYYYMMDD_HHMMSS.json`.

### 4. Run Optimizer

Optimize the system prompt using eval feedback:

```bash
python scripts/run_optimizer.py --iterations 3
```

This will:
1. Run baseline eval
2. Analyze failures with `REASONING_MODEL`
3. Generate improved system prompts
4. Re-run evals to measure improvement
5. Save a before/after report to `optimizer/reports/`

---

## Metrics

| Metric | Description |
|---|---|
| `overall_score` | Weighted score: 100% for full fix, 50% for partial, 0% for failure |
| `full_fix_rate` | Fraction of cases where all tests pass after repair |
| `partial_pass_rate` | Fraction of cases with some (but not all) tests passing |
| `files_fully_fixed` | Count of fully fixed cases |
| `files_partially_fixed` | Count of partially fixed cases |
| `files_failed` | Count of cases where no tests pass |
| `average_iterations` | Mean repair iterations used |
| `syntax_error_rate` | Fraction of cases that produced SyntaxError |
| `timeout_rate` | Fraction of cases that timed out |
| `test_file_modified_rate` | Fraction of cases where the test file was improperly modified |

---

## Dataset

8 intentionally buggy Python files covering common bug categories:

| Case | Bug Type | Description |
|---|---|---|
| `wrong_operator_01` | Wrong operator | Uses `+` instead of `-` in discount calc |
| `off_by_one_02` | Off-by-one | Pagination start index and ceiling division |
| `none_handling_03` | None handling | Missing None checks on user dict |
| `empty_list_04` | Empty list/string | ZeroDivisionError and wrong accumulation |
| `inverted_logic_05` | Inverted boolean | Flipped conditions in access control |
| `boundary_condition_06` | Boundary condition | Exclusive vs inclusive bounds, wrong clamp |
| `sorting_filtering_07` | Sorting/filtering | Inverted sort order, wrong filter predicate |
| `string_edge_case_08` | String edge case | Truncation, slug collapse, email masking |

Each case contains `buggy.py` and `test_buggy.py`. No answer keys are included.

---

## Results

> **⚠️ Results must be generated locally by running the eval harness. The scores below are placeholders.**

### Baseline vs Optimized

```
┌───────────────┬──────────┬───────────┐
│ Metric        │ Baseline │ Optimized │
├───────────────┼──────────┼───────────┤
│ Overall Score │  ?.?%    │   ?.?%    │
│ Full Fix Rate │  ?/8     │   ?/8     │
│ Avg Iterations│  ?.?     │   ?.?     │
└───────────────┴──────────┴───────────┘
```

To generate real results:

```bash
# Run eval
python scripts/run_eval.py

# Run optimizer (includes baseline + optimized evals)
python scripts/run_optimizer.py --iterations 3

# Check results
cat evals/results/*.json
cat optimizer/reports/*.json
```

---

## Safety Rules

- ✅ Agent edits ONLY the buggy source file
- ✅ Test file is never modified (tamper detection included)
- ✅ Public function signatures are preserved
- ✅ Minimal, surgical fixes preferred
- ✅ Max 3 repair iterations
- ✅ API keys never appear in source code
- ✅ Dataset stays frozen during optimizer runs (only system_prompt.txt changes)

---

## Limitations

- **Model-dependent**: Quality depends on the underlying model's coding ability. Free-tier models may struggle with complex bugs.
- **Single-file scope**: Agent only handles single-file bugs, not cross-module issues.
- **Python-only**: Dataset and tooling target Python; no multi-language support.
- **No incremental patches**: Agent rewrites the buggy file rather than producing git-style patches.
- **OpenRouter rate limits**: Free-tier models may have rate limits that affect eval throughput.

## Future Improvements

- Add more dataset cases (type errors, concurrency bugs, API misuse)
- Support multi-file bugs
- Implement git-style diff output
- Add cost tracking per eval run
- Parallelize eval runs
- Add a web dashboard for eval results
- Support additional models and compare performance
- Implement a RAG component for looking up documentation

---

## Demo Instructions

```bash
# 1. Setup
git clone <repo-url> && cd BugFix-Multi-Agent
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env  # Then edit with your API keys

# 2. Verify connection
python scripts/test_connection.py

# 3. Fix one bug
python scripts/run_agent.py dataset/cases/wrong_operator_01/buggy.py dataset/cases/wrong_operator_01/test_buggy.py

# 4. Run full eval
python scripts/run_eval.py

# 5. Optimize prompts
python scripts/run_optimizer.py --iterations 3

# 6. View results
cat optimizer/reports/*.json
```

---

## License

MIT
