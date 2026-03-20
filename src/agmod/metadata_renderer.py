"""Markdown rendering for agmod's metadata viewer."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from agmod.block_model import Block, BlockMetadata
from agmod.scanner import parse_block_metadata, read_frontmatter

RenderMode = Literal["canonical", "markdown", "text"]

# [S-260320-7] simdoc optional; renderer uses pure string building.

PREVIEW_LINES = 30
REQUIRED_FIELDS = (
    "id",
    "name",
    "type",
    "scope",
    "version",
    "status",
    "revised",
    "summary",
)


def detect_mode(path: Path, has_frontmatter: bool) -> RenderMode:
    """Detect rendering mode for a file path.

    Args:
        path: Path to the selected file.
        has_frontmatter: Whether frontmatter was detected.

    Returns:
        The rendering mode for the viewer.
    """

    # [S-260320-1]
    # [I-260320-2]
    if path.suffix.lower() != ".md":
        return "text"
    if has_frontmatter:
        return "canonical"
    return "markdown"


def render_block(block: Block) -> str:
    """Render a block into viewer-ready markdown.

    Args:
        block: Selected block to render.

    Returns:
        Markdown string for the viewer widget.
    """

    # [S-260320-6]
    # [I-260320-3]
    frontmatter, remainder, has_frontmatter = read_frontmatter(block.absolute_path)
    mode = detect_mode(block.absolute_path, has_frontmatter)
    if mode == "canonical":
        metadata = parse_block_metadata(frontmatter)
        excerpt = _truncate_lines(remainder, PREVIEW_LINES)
        return _render_canonical(block, metadata, excerpt, has_frontmatter)
    if mode == "markdown":
        return render_markdown(block.absolute_path)
    return render_text(block.absolute_path, block.relative_path)


def render_markdown(path: Path) -> str:
    """Render a markdown file with a fixed-size preview.

    Args:
        path: Path to the markdown file.

    Returns:
        Preview markdown content.
    """

    # [S-260320-1.2]
    # [S-260320-3]
    # [I-260320-3]
    excerpt = _read_preview_text(path, PREVIEW_LINES)
    return excerpt


def render_text(path: Path, relative_path: Path) -> str:
    """Render a non-markdown file as a markdown-wrapped preview.

    Args:
        path: Path to the file.
        relative_path: Path relative to the source root.

    Returns:
        Markdown wrapper with a text code block.
    """

    # [S-260320-1.3]
    # [S-260320-3]
    # [I-260320-3]
    excerpt = _read_preview_text(path, PREVIEW_LINES)
    filename = path.name
    return (
        f"# {filename}\n\n"
        f"_Path: {relative_path.as_posix()}_\n\n"
        "---\n\n"
        "```text\n"
        f"{excerpt}\n"
        "```"
    )


def _render_canonical(
    block: Block,
    metadata: BlockMetadata,
    excerpt: str,
    has_frontmatter: bool,
) -> str:
    """Render canonical metadata as structured markdown."""

    # [S-260320-1.1]
    # [S-260320-2]
    # [S-260320-4]
    # [I-260320-3]
    incomplete = has_frontmatter and not _has_required_fields(metadata)
    title = metadata.name or block.name
    sections: list[str] = []

    if incomplete:
        # [S-260320-2.2]
        sections.append("> ⚠ Incomplete metadata")

    sections.append(f"# {title}")

    blockquote_lines: list[str] = []
    if metadata.block_id:
        blockquote_lines.append(f"> ID: {metadata.block_id}  ")
    type_scope = _join_fields(("Type", metadata.block_type), ("Scope", metadata.scope))
    if type_scope:
        blockquote_lines.append(f"> {type_scope}")
    status_version = _join_fields(
        ("Status", metadata.status),
        ("Version", metadata.version),
        ("Revised", metadata.revised),
    )
    if status_version:
        blockquote_lines.append(f"> {status_version}")
    if blockquote_lines:
        sections.append("\n".join(blockquote_lines))

    sections.append("---")

    if metadata.summary:
        sections.append(metadata.summary)
        sections.append("---")

    if metadata.tags:
        tags_line = " ".join(f"`{tag}`" for tag in metadata.tags)
        sections.append("### Tags\n" + tags_line)
        sections.append("---")

    sections.append("### Preview\n" + excerpt)
    sections.append("---")
    sections.append(f"_Path: {block.relative_path.as_posix()}_")

    return "\n\n".join(sections)


def _has_required_fields(metadata: BlockMetadata) -> bool:
    """Return True when all canonical fields are present."""

    # [S-260320-2.1]
    required_values = (
        metadata.block_id,
        metadata.name,
        metadata.block_type,
        metadata.scope,
        metadata.version,
        metadata.status,
        metadata.revised,
        metadata.summary,
    )
    return all(value is not None for value in required_values)


def _join_fields(*pairs: tuple[str, str | None]) -> str | None:
    parts = [f"{label}: {value}" for label, value in pairs if value]
    if not parts:
        return None
    return " | ".join(parts)


def _truncate_lines(text: str, max_lines: int) -> str:
    if max_lines <= 0:
        return ""
    lines = text.splitlines()
    return "\n".join(lines[:max_lines])


def _read_preview_text(path: Path, max_lines: int) -> str:
    # [S-260320-3]
    # [I-260320-5]
    if max_lines <= 0:
        return ""
    try:
        with path.open("r", encoding="utf-8") as handle:
            lines: list[str] = []
            for _ in range(max_lines):
                line = handle.readline()
                if not line:
                    break
                lines.append(line.rstrip("\n"))
    except (OSError, UnicodeDecodeError):
        return ""
    return "\n".join(lines)
