from __future__ import annotations

import asyncio
from pathlib import Path

from textual.widgets import Tree

from agmod.tui.app import AgmodApp


def _build_fixture(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "source"
    source.mkdir()
    (source / "tool.md").write_text("# Tool\n", encoding="utf-8")

    config_path = tmp_path / "config.toml"
    config_path.write_text(
        f'[sources]\nlocal = "{source.as_posix()}"\n', encoding="utf-8"
    )

    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "AGENTS.md").write_text(
        "# AGENTS.md\n# Guidance for agentic coders working in this repo.\n",
        encoding="utf-8",
    )

    return project_root, config_path


def test_tui_layout_snapshot(tmp_path: Path) -> None:
    project_root, config_path = _build_fixture(tmp_path)
    app = AgmodApp(project_root=project_root, config_path=config_path)

    async def run_app() -> str:
        async with app.run_test(size=(100, 24)) as pilot:
            await pilot.pause()
            sources = app.query_one("#sources", Tree)
            project = app.query_one("#project", Tree)
            info = app.query_one("#info")
            assert sources.size.width >= 24
            assert project.size.width >= 24
            assert info.size.width >= 32
            return app.export_screenshot(simplify=True)

    snapshot = asyncio.run(run_app())
    expected_path = Path(__file__).parent / "snapshots" / "tui_layout.svg"
    expected = expected_path.read_text(encoding="utf-8")
    assert snapshot == expected
