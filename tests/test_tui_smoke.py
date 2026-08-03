from __future__ import annotations

import asyncio
from pathlib import Path

from textual.widgets import Tree

from agmod.block_model import Block
from agmod.tui.app import AgmodApp


def test_tui_smoke_add_remove(tmp_path: Path) -> None:
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

    app = AgmodApp(project_root=project_root, config_path=config_path)

    async def run_app() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            if app._ui is None:
                raise AssertionError("UI nodes not initialized")
            app._ui.sources.focus()
            await pilot.pause()
            app.select_source_block(Path("tool.md"))
            app.action_add_block()
            await pilot.pause()
            assert (project_root / "llm" / "tool.md").exists()

            app._ui.project.focus()
            await pilot.pause()
            app.select_project_block(Path("tool.md"))
            app.action_remove_block()
            await pilot.pause()
            assert not (project_root / "llm" / "tool.md").exists()

    asyncio.run(run_app())


def test_vim_top_and_bottom_keys_apply_to_each_tree(tmp_path: Path) -> None:
    # [T-260803-4]
    source = tmp_path / "source"
    source.mkdir()
    for name in ("alpha.md", "beta.md", "gamma.md"):
        (source / name).write_text(f"# {name}\n", encoding="utf-8")

    config_path = tmp_path / "config.toml"
    config_path.write_text(
        f'[sources]\nlocal = "{source.as_posix()}"\n', encoding="utf-8"
    )
    project_root = tmp_path / "project"
    project_llm = project_root / "llm"
    project_llm.mkdir(parents=True)
    for name in ("alpha.md", "beta.md", "gamma.md"):
        (project_llm / name).write_text(f"# {name}\n", encoding="utf-8")

    app = AgmodApp(project_root=project_root, config_path=config_path)

    async def run_app() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            sources = app.query_one("#sources", Tree)
            project = app.query_one("#project", Tree)

            await pilot.press("G")
            assert sources.cursor_line == sources.last_line
            await pilot.press("g", "g")
            assert sources.cursor_line == 0

            await pilot.press("tab", "G")
            assert project.has_focus
            assert project.cursor_line == project.last_line
            await pilot.press("g", "g")
            assert project.cursor_line == 0

    asyncio.run(run_app())


def test_tui_vim_bindings_add_remove(tmp_path: Path) -> None:
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

    app = AgmodApp(project_root=project_root, config_path=config_path)

    async def run_app() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            if app._ui is None:
                raise AssertionError("UI nodes not initialized")
            app._ui.sources.focus()
            await pilot.pause()
            app.select_source_block(Path("tool.md"))
            await pilot.press("l")
            await pilot.pause()
            assert (project_root / "llm" / "tool.md").exists()

            await pilot.press("h")
            await pilot.pause()
            assert not (project_root / "llm" / "tool.md").exists()

    asyncio.run(run_app())


def test_tui_installs_and_non_cascading_removes_preset(tmp_path: Path) -> None:
    # [T-260803-3]
    source = tmp_path / "source"
    presets = source / "presets"
    presets.mkdir(parents=True)
    metadata = """scope: core
version: 1.0
status: active
revised: 2026-08-03
summary: Test.
"""
    (source / "tool.md").write_text(
        f"---\nid: TOOL\nname: Tool\ntype: toolbox\n{metadata}---\n",
        encoding="utf-8",
    )
    (presets / "starter.md").write_text(
        f"---\nid: PRESET\nname: Starter\ntype: preset\n{metadata}---\n\n"
        "## Includes (ordered)\n- TOOL\n",
        encoding="utf-8",
    )
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        f'[sources]\nlocal = "{source.as_posix()}"\n', encoding="utf-8"
    )
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
    app = AgmodApp(project_root=project_root, config_path=config_path)

    async def run_app() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            if app._ui is None:
                raise AssertionError("UI nodes not initialized")
            app._ui.sources.focus()
            await pilot.pause()
            app.select_source_block(Path("presets/starter.md"))
            assert app._ui.sources.cursor_node is not None
            selected = app._ui.sources.cursor_node.data
            assert isinstance(selected, Block)
            assert selected.relative_path == Path("presets/starter.md")
            assert app.focused is app._ui.sources
            await pilot.press("l")
            await pilot.pause()
            assert (project_root / "llm" / "starter.md").exists()
            assert (project_root / "llm" / "tool.md").exists()
            agents_text = (project_root / "AGENTS.md").read_text(encoding="utf-8")
            assert "llm/starter.md" in agents_text
            assert "llm/tool.md" in agents_text

            app.select_source_block(Path("presets/starter.md"))
            await pilot.press("h")
            await pilot.pause()
            assert not (project_root / "llm" / "starter.md").exists()
            assert (project_root / "llm" / "tool.md").exists()

    asyncio.run(run_app())
