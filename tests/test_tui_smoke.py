from __future__ import annotations

import asyncio
from pathlib import Path

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
