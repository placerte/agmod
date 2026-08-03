# agmod — GitHub Issues #1–#5

This handoff extends the audited v0.1 contract for the five issues ingested on
2026-08-03. Existing single-block behavior and the flat project `llm/` layout
remain compatible.

## Specifications

### S-260803-1 — Default configuration installation

- A missing config is created with active source
  `kb_llm = "~/llm-blocks/blocks/"` plus commented `personal` and `workflows`
  examples.
- The release installer targets the invoking user's home when run with `sudo`.
- Existing config content is never overwritten.

### S-260803-2 — Selection contrast lab

- A standalone Textual app displays `option_1` through `option_6` using the
  production Everforest dark-hard theme.
- Cursor movement applies progressively stronger focused and blurred styles and
  explains the active theme tokens.
- The production app uses selected `option_3`: focused
  `$panel-lighten-1 / $foreground` and blurred `$panel / $foreground`.

### S-260803-3 — Preset installation

- Canonical presets use the ordered IDs under `## Includes (ordered)`.
- Installing a preset copies its definition followed by all resolved blocks.
- Duplicate or missing IDs, self-reference, nested presets, and filename
  collisions fail before writes; I/O failures roll back newly created files.
- Existing matching canonical IDs are retained, partial installs are repaired,
  and removing a preset leaves its dependencies installed.

### S-260803-4 — Vim tree boundary navigation

- `gg` moves the cursor to the first visible node in the focused tree.
- `G` moves the cursor to the last visible node in the focused tree.
- Both bindings apply independently to the source and project trees.

### S-260803-5 — Release self-update

- `agmod --update` downloads and executes the official latest-release installer
  without starting the TUI.
- Running `agmod` without arguments remains compatible and starts the TUI.
- Download and installer failures produce actionable errors; installer failure
  advises `sudo agmod --update` for the default `/usr/local/bin` installation.

## Implementation

- I-260803-1: Share the exact default template between runtime config creation,
  the installer behavior, and documentation.
- I-260803-2: Add `selection_style_demo_tui_app` with six typed style options and
  Pilot-observable focused/blurred behavior.
- I-260803-3: Add typed preset parsing, indexing, resolution, installation, and
  TUI integration without changing the existing `copy_block` API.
- I-260803-4: Extend `StyledTree` with focused `gg` and `G` navigation.
- I-260803-5: Add CLI dispatch and reuse the official installer for updates.

## Tests

- T-260803-1: Default creation, preservation, loading, and isolated installer.
- T-260803-2: Six-option Pilot navigation and locked dark-hard theme.
- T-260803-3: Ordered resolution, invalid catalogs, collision preflight,
  rollback, repair, AGENTS updates, and non-cascading removal.
- T-260803-4: Pilot navigation to both boundaries in both production trees.
- T-260803-5: CLI routing, installer execution, and update failure reporting.

## Definition of Done

### DoD-260803-1

- All three issue behaviors are implemented and requirement-tagged.
- `bash -n scripts/install.sh`, Black checks, `uv run pytest`, and `uv build`
  succeed.
- `docs/progress_tracker.csv` records verification evidence.

### DoD-260803-2

- Issues #4 and #5 are implemented and requirement-tagged.
- Pilot, CLI, full-suite, formatting, shell syntax, and package build checks
  succeed.
- `docs/progress_tracker.csv` records verification evidence.
