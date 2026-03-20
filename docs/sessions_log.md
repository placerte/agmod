# Sessions Log

## 2026-03-20
- Completed: added canonical markdown viewer rendering modes, frontmatter parsing, and updated TUI to use a single Markdown panel with scroll reset.
- Added: renderer tests and progress tracker entries for S/I/T/DoD requirements.
- Tests: `uv run pytest` failed during collection (missing `crawl4ai` and `color_demo_tui_app` modules).
- Notes: user will human test the metadata viewer in the next session.

## 2026-03-13
- Completed: iterated on the TUI layout (panel widths, framed panels with titles), navigation, and tree rendering.
- Changed: `Tree` rendering now uses `StyledTree` to preserve per-node colors and full-line cursor background; leaf nodes use `add_leaf()`; source tree hides the root and collapses single-source view; project tree is flat.
- Tests: updated and regenerated Textual snapshots; TUI smoke tests still pass.
- Notes: duplicate filenames in `llm/` now skip with a toast; cursor highlight spans the full line using a post-style render override.
