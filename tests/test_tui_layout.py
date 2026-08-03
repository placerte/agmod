from __future__ import annotations

import asyncio
from pathlib import Path
import re

import pytest
from textual.widgets import Tree

from agmod.tui.app import AgmodApp


def _cursor_colors(tree: Tree) -> tuple[str | None, str | None]:
    style = tree.get_component_rich_style("tree--cursor", partial=False)
    color = style.color.name if style.color is not None else None
    background = style.bgcolor.name if style.bgcolor is not None else None
    return color, background


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


def test_tui_layout_snapshot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NO_COLOR", raising=False)
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

    def normalize(svg: str) -> str:
        stable_ids = re.sub(r"terminal-\d+", "terminal-ID", svg)
        return re.sub(r'(?<=fill=")#[0-9a-fA-F]{6}', "#COLOR", stable_ids)

    assert normalize(snapshot) == normalize(expected)


def test_tree_cursor_uses_option_3_for_focused_and_blurred_states(
    tmp_path: Path,
) -> None:
    # [S-260803-2] [T-260803-2]
    project_root, config_path = _build_fixture(tmp_path)
    app = AgmodApp(project_root=project_root, config_path=config_path)

    async def run_app() -> None:
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            sources = app.query_one("#sources", Tree)
            project = app.query_one("#project", Tree)
            variables = app.get_css_variables()

            assert sources.has_focus
            assert _cursor_colors(sources) == (
                variables["foreground"].lower(),
                variables["panel-lighten-1"].lower(),
            )

            await pilot.press("tab")
            await pilot.pause()

            assert project.has_focus
            assert _cursor_colors(sources) == (
                variables["foreground"].lower(),
                variables["panel"].lower(),
            )

    asyncio.run(run_app())
