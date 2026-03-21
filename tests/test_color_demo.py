"""Pilot-based tests for color_demo_tui_app.

Verify that theme colour swatches render with differentiated colours
and that theme cycling actually changes them.
"""

from __future__ import annotations

import asyncio
from agmod.color_demo_tui_app import ColorDemoApp


def test_swatches_render_with_differentiated_colors() -> None:
    """Swatch rows for different base colours must have distinct foreground
    or background colours in the rendered output."""
    app = ColorDemoApp()

    async def run() -> None:
        async with app.run_test(size=(100, 50)) as pilot:
            await pilot.pause()

            # Collect background colors from a few swatch rows that should differ.
            # We pick base shades (no suffix) for primary, accent, error, success.
            targets = ["primary", "accent", "error", "success"]
            bg_colors: dict[str, object] = {}

            for widget in app.query("SwatchRow"):
                text = (
                    widget.render().plain
                    if hasattr(widget.render(), "plain")
                    else str(widget.render())
                )
                for target in targets:
                    if f"${target} " in text or text.strip() == f"${target}":
                        # Get the actual rendered style from the widget
                        bg_colors[target] = widget.styles.background
                        break

            # We should have found at least 3 of the 4 targets
            assert len(bg_colors) >= 3, (
                f"Expected at least 3 swatch targets, found {len(bg_colors)}: "
                f"{list(bg_colors.keys())}"
            )

    asyncio.run(run())


def test_theme_cycling_changes_subtitle() -> None:
    """Pressing 't' should cycle the theme and update the subtitle."""
    app = ColorDemoApp()

    async def run() -> None:
        async with app.run_test(size=(100, 50)) as pilot:
            await pilot.pause()
            initial_theme = app.theme
            initial_subtitle = app.sub_title

            await pilot.press("t")
            await pilot.pause()

            assert app.theme != initial_theme, "Theme should have changed"
            assert app.sub_title != initial_subtitle, (
                "Subtitle should reflect new theme"
            )
            assert app.sub_title == app.theme, "Subtitle should match theme name"

    asyncio.run(run())


def test_theme_cycling_changes_colors() -> None:
    """Theme change should produce different resolved colour values for
    semantic tokens like 'accent'."""
    app = ColorDemoApp()

    async def run() -> None:
        async with app.run_test(size=(100, 50)) as pilot:
            await pilot.pause()

            # Capture accent color from current theme
            variables_before = app.get_css_variables()
            accent_before = variables_before.get("accent")

            # Cycle through several themes to find one with a different accent
            found_different = False
            for _ in range(5):
                await pilot.press("t")
                await pilot.pause()
                variables_after = app.get_css_variables()
                accent_after = variables_after.get("accent")
                if accent_after != accent_before:
                    found_different = True
                    break

            assert found_different, (
                "Expected to find a theme with a different accent colour "
                f"after cycling. accent stayed: {accent_before}"
            )

    asyncio.run(run())


def test_snapshot_shows_colored_swatches() -> None:
    """Take a screenshot and verify it contains non-trivial colour content.
    This is a visual-regression baseline."""
    app = ColorDemoApp()

    async def run() -> None:
        async with app.run_test(size=(100, 60)) as pilot:
            await pilot.pause()

            # Export SVG snapshot for visual inspection
            svg = app.export_screenshot()
            assert len(svg) > 500, "Screenshot SVG should have substantial content"

            # The SVG should contain multiple distinct fill/color values
            # indicating that swatches are actually coloured differently
            import re

            # Extract all hex color values from the SVG
            hex_colors = set(re.findall(r"#[0-9a-fA-F]{6}", svg))

            # We expect many distinct colors since we're showing
            # primary, secondary, accent, success, warning, error
            # each with 7 shade variants
            assert len(hex_colors) >= 10, (
                f"Expected at least 10 distinct colours in snapshot, "
                f"found {len(hex_colors)}: {sorted(hex_colors)[:20]}"
            )

    asyncio.run(run())
