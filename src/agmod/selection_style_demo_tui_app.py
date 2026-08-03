"""Standalone comparison app for agmod tree selection styles.

Run with: ``uv run python -m agmod.selection_style_demo_tui_app``.
"""

from __future__ import annotations

from dataclasses import dataclass

from rich.segment import Segment
from rich.style import Style
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.strip import Strip
from textual.widgets import Footer, Header, Static, Tree
from textual.widgets._tree import TreeNode

from agmod.tui.app import StyledTree
from agmod.tui.themes import register_everforest_themes


@dataclass(frozen=True, slots=True)
class SelectionOption:
    """Theme-token combination used for focused and blurred selection."""

    name: str
    focused_background: str
    focused_foreground: str
    blurred_background: str
    blurred_foreground: str
    description: str


SELECTION_OPTIONS: tuple[SelectionOption, ...] = (
    SelectionOption(
        "option_1",
        "surface-darken-1",
        "foreground",
        "background",
        "foreground",
        "Current production baseline.",
    ),
    SelectionOption(
        "option_2",
        "surface-lighten-1",
        "foreground",
        "surface",
        "foreground",
        "A lighter neutral surface with normal text.",
    ),
    SelectionOption(
        "option_3",
        "panel-lighten-1",
        "foreground",
        "panel",
        "foreground",
        "A stronger neutral panel highlight.",
    ),
    SelectionOption(
        "option_4",
        "primary-muted",
        "foreground",
        "surface-lighten-1",
        "foreground",
        "A muted Everforest green selection.",
    ),
    SelectionOption(
        "option_5",
        "secondary-muted",
        "foreground",
        "surface-lighten-1",
        "foreground",
        "A muted Everforest blue selection.",
    ),
    SelectionOption(
        "option_6",
        "block-cursor-background",
        "block-cursor-foreground",
        "block-cursor-blurred-background",
        "block-cursor-blurred-foreground",
        "The highest-contrast cursor treatment from the theme.",
    ),
)


class OptionTree(StyledTree):
    """Tree that paints each selected row using that row's candidate style."""

    def render_line(self, y: int) -> Strip:
        strip = super().render_line(y)
        line_index = y + self.scroll_offset.y
        if line_index != self.cursor_line:
            return strip
        node = self.cursor_node
        if node is None or not isinstance(node.data, SelectionOption):
            return strip

        option = node.data
        if self.has_focus:
            background_name = option.focused_background
            foreground_name = option.focused_foreground
        else:
            background_name = option.blurred_background
            foreground_name = option.blurred_foreground
        variables = self.app.get_css_variables()
        background = variables.get(background_name)
        foreground = variables.get(foreground_name)
        selection_style = Style(color=foreground, bgcolor=background)
        segments = list(
            Segment.apply_style(strip._segments, post_style=selection_style)
        )
        return Strip(segments, strip.cell_length)


class FocusableExplanation(Static):
    """Explanation panel that can receive focus to preview blurred cursors."""

    can_focus = True


class SelectionStyleDemoApp(App[None]):
    """Compare six cursor treatments in the production dark theme."""

    TITLE = "agmod Selection Contrast Lab"
    BINDINGS = [("q", "quit", "Quit"), ("tab", "focus_next", "Switch focus")]

    DEFAULT_CSS = """
    #main {
        height: 1fr;
    }

    .panel {
        width: 1fr;
        min-width: 30;
        height: 1fr;
        border: round $accent;
        padding: 0 1;
    }

    #details {
        width: 2fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main"):
            with Container(classes="panel"):
                yield OptionTree("Selection options", id="options")
            with Container(id="details", classes="panel"):
                yield FocusableExplanation(id="explanation")
        yield Footer()

    def on_mount(self) -> None:
        # [S-260803-2] [I-260803-2] The lab stays on the production dark theme.
        register_everforest_themes(self)
        self.theme = "everforest-dark-hard"
        tree = self.query_one("#options", Tree)
        tree.show_root = False
        tree.root.expand()
        for option in SELECTION_OPTIONS:
            tree.root.add_leaf(option.name, data=option)
        if tree.root.children:
            tree.select_node(tree.root.children[0])
        tree.focus()

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted) -> None:
        option = event.node.data
        if not isinstance(option, SelectionOption):
            return
        explanation = self.query_one("#explanation", Static)
        explanation.update(
            f"{option.name}\n\n{option.description}\n\n"
            f"Focused: ${option.focused_background} / "
            f"${option.focused_foreground}\n"
            f"Blurred: ${option.blurred_background} / "
            f"${option.blurred_foreground}\n\n"
            "Use Up/Down to compare. Press Tab to inspect the blurred state."
        )


if __name__ == "__main__":
    SelectionStyleDemoApp().run()
