from __future__ import annotations

from pathlib import Path

from agmod.block_model import Block
from agmod.metadata_renderer import render_block


def _make_block(path: Path) -> Block:
    return Block(
        source="local",
        relative_path=Path(path.name),
        absolute_path=path,
        name=path.stem,
        description="",
        tags=(),
    )


def test_canonical_block_rendering(tmp_path: Path) -> None:
    # [T-260320-1]
    block_path = tmp_path / "block.md"
    block_path.write_text(
        """---
id: S-1
name: Canonical Block
scope: core
version: 1.0
status: draft
revised: 2026-03-20
summary: Canonical summary.
tags: [alpha, beta]
---
Line 1
Line 2
""",
        encoding="utf-8",
    )

    rendered = render_block(_make_block(block_path))

    assert "# Canonical Block" in rendered
    assert "ID: S-1" in rendered
    assert "Type: spec | Scope: core" in rendered
    assert "Status: draft | Version: 1.0 | Revised: 2026-03-20" in rendered
    assert "Canonical summary." in rendered
    assert "### Tags" in rendered
    assert "`alpha`" in rendered
    assert "`beta`" in rendered
    assert "### Preview" in rendered
    assert "Line 1" in rendered
    assert "Line 2" in rendered
    assert "_Path: block.md_" in rendered


def test_incomplete_metadata_warns(tmp_path: Path) -> None:
    # [T-260320-2]
    block_path = tmp_path / "incomplete.md"
    block_path.write_text(
        """---
id: S-2
name: Incomplete
scope: core
version: 1.0
revised: 2026-03-20
summary: Missing status.
---
Body
""",
        encoding="utf-8",
    )

    rendered = render_block(_make_block(block_path))

    assert "> ⚠ Incomplete metadata" in rendered
    assert "Status:" not in rendered
    assert "Missing status." in rendered


def test_plain_markdown_preview(tmp_path: Path) -> None:
    # [T-260320-3]
    block_path = tmp_path / "plain.md"
    lines = [f"Line {idx}" for idx in range(1, 36)]
    block_path.write_text("\n".join(lines), encoding="utf-8")

    rendered = render_block(_make_block(block_path))

    assert "Line 30" in rendered
    assert "Line 31" not in rendered


def test_text_file_wrapped(tmp_path: Path) -> None:
    # [T-260320-4]
    block_path = tmp_path / "notes.txt"
    block_path.write_text("Alpha\nBeta\nGamma\n", encoding="utf-8")

    rendered = render_block(_make_block(block_path))

    assert "# notes.txt" in rendered
    assert "_Path: notes.txt_" in rendered
    assert "```text" in rendered
    assert "Alpha" in rendered
    assert "Gamma" in rendered


def test_preview_is_capped(tmp_path: Path) -> None:
    # [T-260320-5]
    block_path = tmp_path / "large.md"
    lines = [f"Item {idx}" for idx in range(1, 80)]
    block_path.write_text("\n".join(lines), encoding="utf-8")

    rendered = render_block(_make_block(block_path))

    assert "Item 30" in rendered
    assert "Item 31" not in rendered
