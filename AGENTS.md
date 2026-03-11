# AGENTS.md
# Guidance for agentic coders working in this repo.

## 0) Sources of truth inside this repo

- `docs/handoff_260311_2.md` is the audited v0.1 spec and DoD.
- `llm/code_style.md` is the primary coding style policy.
- `llm/python_toolbox.md` is the default Python toolchain policy.
- `llm/textual_toolbox.md` is the Textual UI testing policy.
- `llm/agent_executor_instructions_v_1.md` defines executor scope and stop rules.
- `llm/progress_tracker.md` defines requirement tracking and tagging rules.
- `llm/user-persona.md` describes the intended user persona and preferences.

## 1) Cursor / Copilot rules

- No `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md` found.

## 2) Repo overview

- Project: agmod (Agent-Modeler), local LLM block manager.
- Core goal: scan registered block sources and copy blocks into `/llm/`.
- UI: Textual TUI launched via `uv run agmod`.
- AGENTS integration: maintain a managed section between markers.

## 3) Build, lint, test, run

### 3.1 Environment and package management

- Use `uv` for all installs and runs.
- Do not use `pip`, `venv`, or `conda`.
- `pyproject.toml` exists; use `uv sync` for env setup.
- Python version target: `>=3.13`.

### 3.2 Run the app

- `uv run agmod`

### 3.3 Build

- `uv build`

### 3.4 Formatting

- `uv run black .`

### 3.5 Linting

- `uv run ruff check .`
- Only run if a Ruff config exists; otherwise skip.

### 3.6 Type checking

- `uv run mypy .`
- Only run if a Mypy config exists; otherwise skip.

### 3.7 Tests

- `uv run pytest`

### 3.8 Single test

- `uv run pytest tests/test_file.py::test_name`
- `uv run pytest -k "pattern"`

## 4) Code style and conventions

### 4.1 General principles

- Type hints first; avoid implicit typing for new or edited code.
- Avoid string-magic and reflection (`getattr`, `setattr`).
- Favor readability over cleverness.
- Keep functions small and single-purpose.
- Prefer explicit loops when they improve clarity.

### 4.2 Imports and modules

- Group imports: standard library, third-party, local.
- Prefer `pathlib.Path` over raw string paths.
- Keep pure logic separate from UI and IO layers.

### 4.3 Formatting

- Black-compatible formatting; no manual formatting debates.
- Keep lines short enough for readability; allow Black to decide.

### 4.4 Types

- Public functions and methods must be fully typed.
- Prefer explicit, named types over clever typing tricks.
- Avoid `Any` unless justified and localized.

### 4.5 Naming

- Functions: verbs, explicit meaning (e.g., `scan_sources`).
- Private helpers: prefix with `_`.
- Constants: `UPPER_SNAKE_CASE`.
- Include units in names when ambiguous (e.g., `time_s`).

### 4.6 Docstrings

- Required for public APIs, domain logic, and IO boundaries.
- Optional for trivial internal helpers.
- Minimum content: purpose, params (units if relevant), return type/shape,
  key assumptions, and failure modes.

### 4.7 Error handling

- Validate inputs early (types, ranges, shapes).
- Raise explicit exceptions with actionable messages.
- Convert internal errors into user-friendly messages in CLI/TUI.

### 4.8 Testing expectations

- Use pytest; deterministic tests preferred.
- Cover edge cases and previously fixed bugs.
- For Textual UI: use Pilot first, then snapshots, then asciinema.

## 5) Agent workflow rules

- Preserve existing public APIs unless explicitly instructed.
- Keep changes small and localized.
- Add or update tests for behavior changes.
- Do not refactor purely for style.

## 6) Requirement tracking

- Use requirement IDs (S-*, I-*, T-*, DoD-*) verbatim.
- Add code tags in logical locations (public funcs, handlers, tests).
- Update `docs/progress_tracker.csv` if it exists in the repo.
- Record evidence before marking items Verified.

## 7) LLM Context Blocks

These files contain reusable instructions and workflows
that may be relevant when working in this repository.

<!-- agmod:start -->

- llm/agent_executor_instructions_v_1.md
- llm/code_style.md
- llm/progress_tracker.md
- llm/python_toolbox.md
- llm/textual_toolbox.md
- llm/user-persona.md

<!-- agmod:end -->
