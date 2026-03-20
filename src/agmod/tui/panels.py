"""UI panels used by agmod's Textual app."""

from __future__ import annotations

from textual.widgets import Markdown

from agmod.block_model import Block
from agmod.metadata_renderer import render_block


class InfoPanel(Markdown):
    """Panel that renders block metadata and preview."""

    def show_block(self, block: Block | None) -> None:
        # [S-260320-5]
        # [I-260320-4]
        if block is None:
            self.update("No block selected.")
            self.scroll_to(0, 0, animate=False)
            return

        content = render_block(block)
        self.update(content)
        self.scroll_to(0, 0, animate=False)

    def show_message(self, message: str) -> None:
        self.update(message)
        self.scroll_to(0, 0, animate=False)
