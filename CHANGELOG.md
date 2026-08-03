# Changelog

## v0.2.0 — 2026-08-03

### Added

- Preset blocks install their declared dependencies in order, repair partial
  installations, preflight conflicts, and roll back newly copied files when an
  installation fails.
- `agmod --update` downloads and runs the official latest-release installer.
- Vim-style `gg` and `G` bindings move to the top and bottom of the focused
  source or project tree.
- A missing user configuration is populated with a useful default source by
  both the runtime and release installer.

### Changed

- The selected tree row now uses the higher-contrast Everforest option 3 style
  in focused and blurred panels.
- Canonical block IDs are used to recognize installed blocks where available.
- The README documents presets, self-update behavior, generated configuration,
  and current keybindings.

### Fixed

- Existing configuration files are preserved during installation and updates.
- Source selections remain aligned with visible tree lines after refreshes.
- Color-sensitive Textual tests remain deterministic when `NO_COLOR` is set in
  the surrounding environment.

## v0.1.3 — 2026-03-20

- Removed obsolete crawl4ai assets.
- Refreshed color demo tests and the TUI layout snapshot.

## v0.1.2

- Added canonical Markdown metadata rendering and related TUI improvements.
