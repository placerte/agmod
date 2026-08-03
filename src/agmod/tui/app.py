"""Textual application for agmod."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import logging

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from rich.segment import Segment
from rich.style import Style
from rich.text import Text
from textual.widgets import Footer, Header, Tree
from textual.widgets._tree import TreeNode
from textual.strip import Strip

from agmod.agents_editor import update_agents_file
from agmod.block_model import Block, ProjectBlock
from agmod.config import load_sources
from agmod.copy_engine import (
    copy_block,
    list_project_blocks,
    remove_project_block,
)
from agmod.presets import (
    PresetError,
    block_identity,
    install_preset,
    installed_block_ids,
    parse_preset,
    preset_is_installed,
)
from agmod.scanner import scan_sources
from agmod.tui.panels import InfoPanel
from agmod.tui.themes import register_everforest_themes


@dataclass
class _NodeRefs:
    sources: Tree
    project: Tree
    info: InfoPanel


class StyledTree(Tree):
    BINDINGS = [
        *Tree.BINDINGS,
        Binding("g", "vim_top", show=False),
        Binding("G", "scroll_end", show=False),
    ]

    _awaiting_second_g = False

    def on_key(self, event: events.Key) -> None:
        if event.key != "g":
            self._awaiting_second_g = False

    def action_vim_top(self) -> None:
        """Move to the first visible node after a consecutive ``gg`` chord."""

        # [S-260803-4] [I-260803-4] A non-g key cancels the pending chord.
        if self._awaiting_second_g:
            self._awaiting_second_g = False
            self.action_scroll_home()
            return
        self._awaiting_second_g = True

    def render_label(self, node: TreeNode, base_style: Style, style: Style) -> Text:
        return super().render_label(node, base_style, style.without_color)

    def render_line(self, y: int) -> Strip:
        strip = super().render_line(y)
        line_index = y + self.scroll_offset.y
        if line_index == self.cursor_line:
            cursor_style = self.get_component_rich_style("tree--cursor", partial=False)
            if cursor_style.bgcolor is not None or cursor_style.color is not None:
                segments = list(
                    Segment.apply_style(
                        strip._segments,
                        post_style=Style(
                            color=cursor_style.color,
                            bgcolor=cursor_style.bgcolor,
                        ),
                    )
                )
                strip = Strip(segments, strip.cell_length)
        return strip


class AgmodApp(App):
    """Main Textual app for agmod."""

    DEFAULT_CSS = """
    #main {
        height: 1fr;
    }

    .panel {
        width: 1fr;
        min-width: 28;
        height: 1fr;
        border: round $accent;
        padding: 0 1;
        border-title-align: left;
    }


    .panel > Tree {
        height: 1fr;
    }

    #info {
        width: 2fr;
        min-width: 32;
    }

    Tree > .tree--cursor {
        background: $panel;
        color: $foreground;
    }

    Tree > .tree--highlight {
        background: $panel;
        color: $foreground;
    }

    Tree > .tree--highlight-line {
        background: $panel;
        color: $foreground;
    }

    Tree:focus > .tree--cursor {
        background: $panel-lighten-1;
        color: $foreground;
    }

    Tree:focus > .tree--highlight {
        background: $panel-lighten-1;
        color: $foreground;
    }

    Tree:focus > .tree--highlight-line {
        background: $panel-lighten-1;
        color: $foreground;
    }
    """

    BINDINGS = [
        Binding("a", "add_block", "Add block"),
        Binding("enter", "add_block", "Add block"),
        Binding("space", "context_action", "Add/Remove", priority=True),
        Binding("delete", "remove_block", "Remove block"),
        Binding("r", "refresh", "Refresh"),
        Binding("tab", "focus_next", "Switch panel"),
        Binding("q", "quit", "Quit"),
        Binding("j", "cursor_down", show=False),
        Binding("k", "cursor_up", show=False),
        Binding("h", "remove_block", show=False, priority=True),
        Binding("l", "add_block", show=False, priority=True),
    ]

    def __init__(
        self,
        project_root: Path | None = None,
        config_path: Path | None = None,
    ) -> None:
        super().__init__()
        self.project_root = project_root or Path.cwd()
        self.config_path = config_path
        self._ui: _NodeRefs | None = None
        self._project_names: set[str] = set()
        self._catalog_blocks: list[Block] = []
        self._project_blocks: list[ProjectBlock] = []
        self._project_ids: set[str] = set()

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main"):
            sources_tree = StyledTree("Sources", id="sources")
            project_tree = StyledTree("Project Blocks", id="project")
            info_panel = InfoPanel(id="info")
            sources_panel = Container(id="sources-panel", classes="panel")
            sources_panel.border_title = "Sources"
            project_panel = Container(id="project-panel", classes="panel")
            project_panel.border_title = "Project Blocks"
            with sources_panel:
                yield sources_tree
            with project_panel:
                yield project_tree
            yield info_panel
        yield Footer()

    def on_mount(self) -> None:
        register_everforest_themes(self)
        self.theme = "everforest-dark-hard"
        sources_tree = self.query_one("#sources", Tree)
        project_tree = self.query_one("#project", Tree)
        info_panel = self.query_one("#info", InfoPanel)
        self._ui = _NodeRefs(
            sources=sources_tree, project=project_tree, info=info_panel
        )
        self._refresh_views()
        sources_tree.focus()

    def _refresh_views(self) -> None:
        if self._ui is None:
            return
        sources = load_sources(self.config_path)
        blocks = scan_sources(sources)
        project_blocks = list_project_blocks(self.project_root)
        self._catalog_blocks = blocks
        self._project_blocks = project_blocks
        self._project_names = {block.relative_path.name for block in project_blocks}
        self._project_ids = installed_block_ids(project_blocks)
        self._populate_sources(self._ui.sources, blocks)
        self._populate_project(self._ui.project, project_blocks)
        self._ensure_cursor(self._ui.sources)
        self._ensure_cursor(self._ui.project)
        self._update_agents(project_blocks)

    def _theme_color(self, name: str) -> str | None:
        colors = self.current_theme.to_color_system()
        value = getattr(colors, name, None)
        if value is None:
            return None
        return value.hex

    def _text_with_style(self, value: str, style: Style | None) -> Text:
        if style is None:
            return Text(value)
        return Text(value, style=style)

    def _populate_sources(self, tree: Tree, blocks: list[Block]) -> None:
        tree.clear()
        root = tree.root
        root.label = ""
        tree.show_root = False
        root.expand()
        source_names = sorted({block.source for block in blocks})
        show_sources = len(source_names) > 1
        source_nodes: dict[str, TreeNode] = {}
        accent_color = self._theme_color("accent")
        success_color = self._theme_color("success")
        accent_style = Style(color=accent_color) if accent_color else None
        success_style = Style(color=success_color) if success_color else None

        for block in blocks:
            if show_sources:
                if block.source not in source_nodes:
                    source_nodes[block.source] = root.add(
                        self._text_with_style(block.source, accent_style),
                        expand=True,
                    )
                parent = source_nodes[block.source]
            else:
                parent = root
            for part in block.relative_path.parts[:-1]:
                child = self._find_child(parent, part)
                if child is None:
                    child = parent.add(
                        self._text_with_style(part, accent_style),
                        expand=True,
                        allow_expand=True,
                    )
                parent = child
            if self._is_source_block_present(block):
                label = self._text_with_style(block.relative_path.name, success_style)
            else:
                label = Text(block.relative_path.name)
            parent.add_leaf(label, data=block)

    def _populate_project(self, tree: Tree, blocks: list[ProjectBlock]) -> None:
        tree.clear()
        root = tree.root
        root.label = ""
        tree.show_root = False
        root.expand()
        for block in blocks:
            root.add_leaf(Text(block.relative_path.name), data=block)

    def _ensure_cursor(self, tree: Tree) -> None:
        if tree.cursor_node is not None:
            return
        if tree.root.children:
            tree.move_cursor(tree.root.children[0])

    def _find_child(self, node: TreeNode, label: str) -> TreeNode | None:
        for child in node.children:
            if str(child.label) == label:
                return child
        return None

    def _is_project_block_present(self, block_name: str) -> bool:
        return block_name in self._project_names

    def _is_source_block_present(self, block: Block) -> bool:
        try:
            preset = parse_preset(block)
            if preset is not None:
                return preset_is_installed(
                    block,
                    self._catalog_blocks,
                    self._project_blocks,
                )
        except PresetError:
            return False

        block_id, _ = block_identity(block)
        if block_id is not None:
            return block_id in self._project_ids
        return self._is_project_block_present(block.relative_path.name)

    def _add_source_block(self, block: Block) -> None:
        try:
            preset = parse_preset(block)
            if preset is not None:
                created = install_preset(
                    block,
                    self._catalog_blocks,
                    self.project_root,
                )
                self.notify(f"Installed {preset.block_id}: {len(created)} new file(s).")
                self._refresh_views()
                return
        except PresetError as exc:
            self.notify(str(exc), severity="error")
            return

        if self._is_source_block_present(block):
            return
        destination = self.project_root / "llm" / block.relative_path.name
        try:
            copy_block(block, self.project_root, allow_overwrite=False)
        except FileExistsError:
            self.notify(
                f"Duplicate filename detected: {destination.name}. Skipped.",
                severity="warning",
            )
            return
        self._refresh_views()

    def _remove_source_block(self, block: Block) -> None:
        block_id, _ = block_identity(block)
        if block_id is not None:
            for project_block in self._project_blocks:
                project_id, _ = block_identity(project_block)
                if project_id == block_id:
                    self._remove_project_block(project_block.relative_path.name)
                    return
        self._remove_project_block(block.relative_path.name)

    def _remove_project_block(self, block_name: str) -> None:
        if not self._is_project_block_present(block_name):
            return
        try:
            remove_project_block(self.project_root, Path(block_name))
        except FileNotFoundError:
            logging.warning("Block not found: %s", block_name)
        self._refresh_views()

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted) -> None:
        if self._ui is None:
            return
        data = event.node.data
        if isinstance(data, Block):
            # [I-260320-4]
            self._ui.info.show_block(data)

    def action_refresh(self) -> None:
        self._refresh_views()

    def action_cursor_down(self) -> None:
        if self.focused is None:
            return
        action = getattr(self.focused, "action_cursor_down", None)
        if action is not None:
            action()

    def action_cursor_up(self) -> None:
        if self.focused is None:
            return
        action = getattr(self.focused, "action_cursor_up", None)
        if action is not None:
            action()

    def action_add_block(self) -> None:
        if self._ui is None:
            return
        focused = self.focused
        if focused is not self._ui.sources:
            return
        node = self._ui.sources.cursor_node
        if node is None or not isinstance(node.data, Block):
            return
        self._add_source_block(node.data)

    def action_remove_block(self) -> None:
        if self._ui is None:
            return
        focused = self.focused
        if focused is self._ui.sources:
            node = self._ui.sources.cursor_node
            if node is None or not isinstance(node.data, Block):
                return
            self._remove_source_block(node.data)
            return
        if focused is self._ui.project:
            node = self._ui.project.cursor_node
            if node is None or not isinstance(node.data, ProjectBlock):
                return
            self._remove_project_block(node.data.relative_path.name)

    def _update_agents(self, project_blocks: list[ProjectBlock]) -> None:
        agents_path = self.project_root / "AGENTS.md"
        block_paths = [Path("llm") / block.relative_path for block in project_blocks]
        update_agents_file(agents_path, block_paths)

    def action_context_action(self) -> None:
        if self._ui is None:
            return
        if self.focused is self._ui.sources:
            node = self._ui.sources.cursor_node
            if node is None or not isinstance(node.data, Block):
                return
            if self._is_source_block_present(node.data):
                self._remove_source_block(node.data)
            else:
                self._add_source_block(node.data)
            return
        if self.focused is self._ui.project:
            node = self._ui.project.cursor_node
            if node is None or not isinstance(node.data, ProjectBlock):
                return
            self._remove_project_block(node.data.relative_path.name)

    def action_focus_sources(self) -> None:
        if self._ui is None:
            return
        self._ui.sources.focus()

    def action_focus_project(self) -> None:
        if self._ui is None:
            return
        self._ui.project.focus()

    def select_source_block(self, relative_path: Path) -> None:
        """Select a source block node by relative path."""

        if self._ui is None:
            return
        for line_number, tree_line in enumerate(self._ui.sources._tree_lines):
            node = tree_line.node
            if (
                isinstance(node.data, Block)
                and node.data.relative_path == relative_path
            ):
                self._ui.sources.move_cursor_to_line(line_number)
                return

    def select_project_block(self, relative_path: Path) -> None:
        """Select a project block node by relative path."""

        if self._ui is None:
            return
        for line_number, tree_line in enumerate(self._ui.project._tree_lines):
            node = tree_line.node
            if (
                isinstance(node.data, ProjectBlock)
                and node.data.relative_path == relative_path
            ):
                self._ui.project.move_cursor_to_line(line_number)
                return


def run() -> None:
    """Run the agmod Textual application."""

    AgmodApp().run()
