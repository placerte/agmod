"""Textual application for agmod."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import logging

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Footer, Header, Tree

from agmod.agents_editor import update_agents_file
from agmod.block_model import Block, ProjectBlock
from agmod.config import load_sources
from agmod.copy_engine import (
    copy_block,
    list_project_blocks,
    remove_project_block,
)
from agmod.scanner import scan_sources
from agmod.tui.panels import InfoPanel


@dataclass
class _NodeRefs:
    sources: Tree
    project: Tree
    info: InfoPanel


class AgmodApp(App):
    """Main Textual app for agmod."""

    BINDINGS = [
        Binding("enter", "add_block", "Add block"),
        Binding("delete", "remove_block", "Remove block"),
        Binding("r", "refresh", "Refresh"),
        Binding("tab", "focus_next", "Switch panel"),
        Binding("q", "quit", "Quit"),
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
        self._pending_overwrite: Path | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            sources_tree = Tree("Sources", id="sources")
            project_tree = Tree("Project Blocks", id="project")
            info_panel = InfoPanel(id="info")
            yield sources_tree
            yield project_tree
            yield info_panel
        yield Footer()

    def on_mount(self) -> None:
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
        self._populate_sources(self._ui.sources, blocks)
        project_blocks = list_project_blocks(self.project_root)
        self._populate_project(self._ui.project, project_blocks)
        self._update_agents(project_blocks)

    def _populate_sources(self, tree: Tree, blocks: list[Block]) -> None:
        tree.clear()
        root = tree.root
        root.label = "Sources"
        root.expand()
        source_nodes: dict[str, Tree.Node] = {}

        for block in blocks:
            if block.source not in source_nodes:
                source_nodes[block.source] = root.add(block.source, expand=True)
            parent = source_nodes[block.source]
            for part in block.relative_path.parts[:-1]:
                child = self._find_child(parent, part)
                if child is None:
                    child = parent.add(part, expand=True)
                parent = child
            parent.add(block.relative_path.name, data=block)

    def _populate_project(self, tree: Tree, blocks: list[ProjectBlock]) -> None:
        tree.clear()
        root = tree.root
        root.label = "Project Blocks"
        root.expand()
        for block in blocks:
            parent = root
            for part in block.relative_path.parts[:-1]:
                child = self._find_child(parent, part)
                if child is None:
                    child = parent.add(part, expand=True)
                parent = child
            parent.add(block.relative_path.name, data=block)

    def _find_child(self, node: Tree.Node, label: str) -> Tree.Node | None:
        for child in node.children:
            if str(child.label) == label:
                return child
        return None

    def _walk_nodes(self, node: Tree.Node) -> list[Tree.Node]:
        nodes = [node]
        for child in node.children:
            nodes.extend(self._walk_nodes(child))
        return nodes

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted) -> None:
        if self._ui is None:
            return
        data = event.node.data
        if isinstance(data, Block):
            self._ui.info.show_block(data)

    def action_refresh(self) -> None:
        self._pending_overwrite = None
        self._refresh_views()

    def action_add_block(self) -> None:
        if self._ui is None:
            return
        focused = self.focused
        if focused is not self._ui.sources:
            return
        node = self._ui.sources.cursor_node
        if node is None or not isinstance(node.data, Block):
            return
        block = node.data
        destination = self.project_root / "llm" / block.relative_path
        if destination.exists() and self._pending_overwrite != destination:
            self._pending_overwrite = destination
            self._ui.info.show_message(
                f"Block exists. Press Enter again to overwrite: {block.relative_path.as_posix()}"
            )
            return
        try:
            copy_block(block, self.project_root, allow_overwrite=destination.exists())
        except FileExistsError:
            self._ui.info.show_message(
                f"Block exists. Press Enter again to overwrite: {block.relative_path.as_posix()}"
            )
            return
        self._pending_overwrite = None
        project_blocks = list_project_blocks(self.project_root)
        self._populate_project(self._ui.project, project_blocks)
        self._update_agents(project_blocks)

    def action_remove_block(self) -> None:
        if self._ui is None:
            return
        focused = self.focused
        if focused is not self._ui.project:
            return
        node = self._ui.project.cursor_node
        if node is None or not isinstance(node.data, ProjectBlock):
            return
        block = node.data
        try:
            remove_project_block(self.project_root, block.relative_path)
        except FileNotFoundError:
            logging.warning("Block not found: %s", block.relative_path)
        project_blocks = list_project_blocks(self.project_root)
        self._populate_project(self._ui.project, project_blocks)
        self._update_agents(project_blocks)

    def _update_agents(self, project_blocks: list[ProjectBlock]) -> None:
        agents_path = self.project_root / "AGENTS.md"
        block_paths = [Path("llm") / block.relative_path for block in project_blocks]
        update_agents_file(agents_path, block_paths)

    def select_source_block(self, relative_path: Path) -> None:
        """Select a source block node by relative path."""

        if self._ui is None:
            return
        for node in self._walk_nodes(self._ui.sources.root):
            if (
                isinstance(node.data, Block)
                and node.data.relative_path == relative_path
            ):
                self._ui.sources.select_node(node)
                return

    def select_project_block(self, relative_path: Path) -> None:
        """Select a project block node by relative path."""

        if self._ui is None:
            return
        for node in self._walk_nodes(self._ui.project.root):
            if (
                isinstance(node.data, ProjectBlock)
                and node.data.relative_path == relative_path
            ):
                self._ui.project.select_node(node)
                return


def run() -> None:
    """Run the agmod Textual application."""

    AgmodApp().run()
