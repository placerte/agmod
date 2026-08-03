from __future__ import annotations

import asyncio

from textual.widgets import Static, Tree

from agmod.selection_style_demo_tui_app import (
    SELECTION_OPTIONS,
    SelectionStyleDemoApp,
)


def test_selection_lab_exposes_six_dark_theme_options() -> None:
    # [T-260803-2]
    app = SelectionStyleDemoApp()

    async def run() -> None:
        async with app.run_test(size=(90, 24)) as pilot:
            await pilot.pause()
            tree = app.query_one("#options", Tree)
            labels = [str(node.label) for node in tree.root.children]
            assert labels == [f"option_{index}" for index in range(1, 7)]
            assert app.theme == "everforest-dark-hard"
            assert tree.has_focus

            await pilot.press("down")
            await pilot.pause()
            assert tree.cursor_node is not None
            assert tree.cursor_node.data == SELECTION_OPTIONS[1]
            explanation = app.query_one("#explanation", Static)
            assert "option_2" in str(explanation.render())

            await pilot.press("tab")
            await pilot.pause()
            assert not tree.has_focus

    asyncio.run(run())
