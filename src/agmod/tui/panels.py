"""UI panels used by agmod's Textual app."""

from __future__ import annotations

from textual.widgets import Static

from agmod.block_model import Block


class InfoPanel(Static):
    """Panel that renders block metadata and preview."""

    def show_block(self, block: Block | None) -> None:
        if block is None:
            self.update("No block selected.")
            return

        description = block.description or "(no description)"
        tags = ", ".join(block.tags) if block.tags else "(none)"
        preview = block.preview(max_lines=20)
        content = (
            f"Name: {block.name}\n"
            f"Source: {block.source}\n"
            f"Path: {block.relative_path.as_posix()}\n"
            f"Description: {description}\n"
            f"Tags: {tags}\n\n"
            "Preview:\n"
            f"{preview}"
        )
        self.update(content)

    def show_message(self, message: str) -> None:
        self.update(message)
