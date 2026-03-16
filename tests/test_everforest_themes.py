"""Tests for Everforest themes registration, shade overrides, and visual output."""

from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

# Ensure project root is on sys.path for color_demo_tui_app import.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from agmod.tui.themes import (
    EVERFOREST_DARK_HARD,
    EVERFOREST_DARK_MEDIUM,
    EVERFOREST_DARK_SOFT,
    EVERFOREST_LIGHT_HARD,
    EVERFOREST_LIGHT_MEDIUM,
    EVERFOREST_LIGHT_SOFT,
    EVERFOREST_THEMES,
    register_everforest_themes,
)
from color_demo_tui_app import ColorDemoApp


def test_all_six_variants_defined() -> None:
    """EVERFOREST_THEMES should contain exactly 6 variants."""
    assert len(EVERFOREST_THEMES) == 6
    names = {t.name for t in EVERFOREST_THEMES}
    assert names == {
        "everforest-dark-hard",
        "everforest-dark-medium",
        "everforest-dark-soft",
        "everforest-light-hard",
        "everforest-light-medium",
        "everforest-light-soft",
    }


def test_dark_variants_have_dark_flag() -> None:
    """All dark variants must have dark=True, light variants dark=False."""
    for theme in [EVERFOREST_DARK_HARD, EVERFOREST_DARK_MEDIUM, EVERFOREST_DARK_SOFT]:
        assert theme.dark is True, f"{theme.name} should be dark"
    for theme in [
        EVERFOREST_LIGHT_HARD,
        EVERFOREST_LIGHT_MEDIUM,
        EVERFOREST_LIGHT_SOFT,
    ]:
        assert theme.dark is False, f"{theme.name} should be light"


def test_distinct_backgrounds_across_contrasts() -> None:
    """Hard/medium/soft variants within dark or light must have different backgrounds."""
    dark_bgs = {t.name: t.background for t in EVERFOREST_THEMES if t.dark}
    light_bgs = {t.name: t.background for t in EVERFOREST_THEMES if not t.dark}

    assert len(set(dark_bgs.values())) == 3, (
        f"Expected 3 distinct dark backgrounds, got: {dark_bgs}"
    )
    assert len(set(light_bgs.values())) == 3, (
        f"Expected 3 distinct light backgrounds, got: {light_bgs}"
    )


def test_shade_overrides_present() -> None:
    """Each theme should have background/surface/panel shade overrides
    in the variables dict."""
    required_keys = [
        "background-darken-1",
        "background-lighten-1",
        "surface-darken-1",
        "surface-lighten-1",
        "panel-darken-1",
        "panel-lighten-1",
        "error-muted",
        "warning-muted",
        "success-muted",
        "primary-muted",
        "secondary-muted",
        "accent-muted",
    ]
    for theme in EVERFOREST_THEMES:
        for key in required_keys:
            assert key in theme.variables, (
                f"{theme.name} missing variable override: {key}"
            )


def test_shade_overrides_are_distinct_from_base() -> None:
    """Shade overrides should differ from the base colour they modify,
    confirming we're not just repeating the same value."""
    theme = EVERFOREST_DARK_HARD
    assert theme.background is not None

    bg_base = theme.background.lower()
    bg_darken1 = theme.variables["background-darken-1"].lower()
    bg_lighten1 = theme.variables["background-lighten-1"].lower()

    assert bg_darken1 != bg_base, "background-darken-1 should differ from base"
    assert bg_lighten1 != bg_base, "background-lighten-1 should differ from base"
    assert bg_darken1 != bg_lighten1, "darken and lighten should differ"


def test_register_themes_in_app() -> None:
    """register_everforest_themes should make all 6 themes available."""
    app = ColorDemoApp()

    async def run() -> None:
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            available = app.available_themes
            for theme in EVERFOREST_THEMES:
                assert theme.name in available, f"{theme.name} not registered"

    asyncio.run(run())


def test_switch_to_everforest_dark_hard() -> None:
    """App should accept switching to everforest-dark-hard and render."""
    app = ColorDemoApp()

    async def run() -> None:
        async with app.run_test(size=(100, 60)) as pilot:
            await pilot.pause()
            app.theme = "everforest-dark-hard"
            await pilot.pause()
            assert app.theme == "everforest-dark-hard"

    asyncio.run(run())


def test_everforest_snapshot_has_palette_colors() -> None:
    """Snapshot of everforest-dark-hard should contain its signature colours."""
    app = ColorDemoApp()

    async def run() -> None:
        async with app.run_test(size=(100, 60)) as pilot:
            await pilot.pause()
            app.theme = "everforest-dark-hard"
            await pilot.pause()

            svg = app.export_screenshot()
            hex_colors = {c.lower() for c in re.findall(r"#[0-9a-fA-F]{6}", svg)}

            # Expect to find key Everforest palette colours in the rendered SVG
            expected_present = [
                "#272e33",  # bg0 (hard)
                "#2e383c",  # bg1 (hard)
            ]
            for expected in expected_present:
                assert expected in hex_colors, (
                    f"Expected palette colour {expected} in snapshot. "
                    f"Found: {sorted(hex_colors)[:30]}"
                )

            # Should have many distinct colors from the shade overrides
            assert len(hex_colors) >= 15, (
                f"Expected at least 15 distinct colours, got {len(hex_colors)}"
            )

    asyncio.run(run())


def test_everforest_light_hard_snapshot() -> None:
    """Snapshot of everforest-light-hard should contain light palette backgrounds."""
    app = ColorDemoApp()

    async def run() -> None:
        async with app.run_test(size=(100, 60)) as pilot:
            await pilot.pause()
            app.theme = "everforest-light-hard"
            await pilot.pause()

            svg = app.export_screenshot()
            hex_colors = {c.lower() for c in re.findall(r"#[0-9a-fA-F]{6}", svg)}

            # Light hard bg0 should be present
            assert "#fffbef" in hex_colors, (
                f"Expected light-hard bg0 #fffbef in snapshot. "
                f"Found: {sorted(hex_colors)[:30]}"
            )

    asyncio.run(run())
