"""Standalone Textual TUI that displays all theme color tokens as styled swatches.

Run with:  uv run python color_demo_tui_app.py
Cycle themes with 't' (next) / 'T' (previous).
"""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Footer, Header, Static

from agmod.tui.themes import register_everforest_themes


# ---------------------------------------------------------------------------
# Colour groups to display
# ---------------------------------------------------------------------------

SHADE_BASES_SEMANTIC: list[str] = [
    "primary",
    "secondary",
    "accent",
    "success",
    "warning",
    "error",
    "foreground",
]

SHADE_BASES_SURFACE: list[str] = [
    "background",
    "primary-background",
    "secondary-background",
    "surface",
    "panel",
    "boost",
]

SHADE_SUFFIXES: list[str] = [
    "-darken-3",
    "-darken-2",
    "-darken-1",
    "",
    "-lighten-1",
    "-lighten-2",
    "-lighten-3",
]

TEXT_VARIANTS: list[str] = [
    "text",
    "text-muted",
    "text-disabled",
    "text-primary",
    "text-secondary",
    "text-warning",
    "text-error",
    "text-success",
    "text-accent",
]

MUTED_VARIANTS: list[str] = [
    "primary-muted",
    "secondary-muted",
    "accent-muted",
    "warning-muted",
    "error-muted",
    "success-muted",
]


def _shade_names(base: str) -> list[str]:
    """Return the 7 shade variable names for a given base colour."""
    return [f"{base}{suffix}" for suffix in SHADE_SUFFIXES]


# ---------------------------------------------------------------------------
# Widgets
# ---------------------------------------------------------------------------


class SectionTitle(Static):
    """A bold section heading."""

    DEFAULT_CSS = """
    SectionTitle {
        margin-top: 1;
        padding: 0 1;
        text-style: bold;
        color: $text;
    }
    """


class SwatchRow(Static):
    """A single colour swatch row."""

    DEFAULT_CSS = """
    SwatchRow {
        height: 1;
        padding: 0 1;
    }
    """


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------


class ColorDemoApp(App[None]):
    """Display every Textual theme colour token as a labelled swatch."""

    TITLE = "Textual Theme Color Demo"

    BINDINGS = [
        Binding("t", "next_theme", "Next theme"),
        Binding("T", "prev_theme", "Prev theme", key_display="shift+t"),
        Binding("q", "quit", "Quit"),
    ]

    DEFAULT_CSS = """
    Screen {
        background: $background;
    }
    #body {
        scrollbar-size: 1 1;
    }
    """

    # -- Theme cycling helpers -----------------------------------------------

    def _theme_list(self) -> list[str]:
        """Return sorted list of available theme names."""
        return sorted(self.available_themes.keys())

    def action_next_theme(self) -> None:
        """Switch to the next theme in alphabetical order."""
        themes = self._theme_list()
        idx = themes.index(self.theme) if self.theme in themes else 0
        self.theme = themes[(idx + 1) % len(themes)]
        self.sub_title = self.theme

    def action_prev_theme(self) -> None:
        """Switch to the previous theme in alphabetical order."""
        themes = self._theme_list()
        idx = themes.index(self.theme) if self.theme in themes else 0
        self.theme = themes[(idx - 1) % len(themes)]
        self.sub_title = self.theme

    # -- Compose UI ----------------------------------------------------------

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="body"):
            # 1) Semantic base colours with shades
            yield SectionTitle("Semantic Colours (with shades)")
            for base in SHADE_BASES_SEMANTIC:
                for var_name in _shade_names(base):
                    label = f"${var_name}"
                    yield SwatchRow(f"[auto on ${var_name}] {label:<40} [/]")
                yield Static(" ")

            # 2) Surface / background colours with shades
            yield SectionTitle("Background / Surface Colours (with shades)")
            for base in SHADE_BASES_SURFACE:
                for var_name in _shade_names(base):
                    label = f"${var_name}"
                    yield SwatchRow(f"[auto on ${var_name}] {label:<45} [/]")
                yield Static(" ")

            # 3) Text variants
            yield SectionTitle("Text Variants")
            for var_name in TEXT_VARIANTS:
                label = f"${var_name}"
                yield SwatchRow(
                    f"[${var_name}]{label:<40}"
                    f"  The quick brown fox jumps over the lazy dog[/]"
                )

            yield Static(" ")

            # 4) Muted variants
            yield SectionTitle("Muted Variants")
            for var_name in MUTED_VARIANTS:
                label = f"${var_name}"
                yield SwatchRow(f"[auto on ${var_name}] {label:<40} [/]")

        yield Footer()

    def on_mount(self) -> None:
        """Register custom themes and set the subtitle."""
        register_everforest_themes(self)
        self.sub_title = self.theme


if __name__ == "__main__":
    ColorDemoApp().run()
