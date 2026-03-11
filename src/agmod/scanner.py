"""Block discovery and metadata extraction."""

from __future__ import annotations

from pathlib import Path
import os
import re

from agmod.block_model import Block


_FRONTMATTER_RE = re.compile(r"^---\s*$")


def _parse_frontmatter(lines: list[str]) -> dict[str, str | list[str]]:
    metadata: dict[str, str | list[str]] = {}
    for line in lines:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if key.lower() == "tags":
            metadata[key] = _parse_tags(value)
        else:
            metadata[key] = value
    return metadata


def _parse_tags(value: str) -> list[str]:
    if not value:
        return []
    cleaned = value.strip()
    if cleaned.startswith("[") and cleaned.endswith("]"):
        inner = cleaned[1:-1]
        parts = [part.strip() for part in inner.split(",")]
        return [part for part in parts if part]
    parts = [part.strip() for part in cleaned.split(",")]
    return [part for part in parts if part]


def _extract_frontmatter(text: str) -> tuple[dict[str, str | list[str]], str]:
    lines = text.splitlines()
    if not lines or not _FRONTMATTER_RE.match(lines[0]):
        return {}, text

    frontmatter_lines: list[str] = []
    for idx in range(1, len(lines)):
        if _FRONTMATTER_RE.match(lines[idx]):
            remainder = "\n".join(lines[idx + 1 :])
            return _parse_frontmatter(frontmatter_lines), remainder
        frontmatter_lines.append(lines[idx])

    return {}, text


def _first_heading(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or None
    return None


def extract_metadata(path: Path) -> tuple[str, str, tuple[str, ...]]:
    """Extract name, description, and tags for a block file.

    Args:
        path: Path to the block file.

    Returns:
        Tuple of (name, description, tags).
    """

    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        stem = path.stem
        return stem, "", ()

    frontmatter, remainder = _extract_frontmatter(text)
    name = frontmatter.get("name") if isinstance(frontmatter.get("name"), str) else None
    description = (
        frontmatter.get("description")
        if isinstance(frontmatter.get("description"), str)
        else ""
    )
    tags_value = frontmatter.get("tags")
    tags: tuple[str, ...] = ()
    if isinstance(tags_value, list):
        tags = tuple(str(tag) for tag in tags_value)
    elif isinstance(tags_value, str):
        tags = tuple(_parse_tags(tags_value))

    if not name:
        heading = _first_heading(remainder)
        name = heading or path.stem

    return name, description, tags


def scan_sources(sources: dict[str, Path]) -> list[Block]:
    """Discover blocks in configured source directories.

    Args:
        sources: Mapping of source name to directory path.

    Returns:
        List of discovered Block objects.
    """

    blocks: list[Block] = []
    for source_name, source_path in sources.items():
        for root, dirs, files in os.walk(source_path):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for filename in files:
                if not filename.endswith(".md"):
                    continue
                absolute_path = Path(root) / filename
                relative_path = absolute_path.relative_to(source_path)
                name, description, tags = extract_metadata(absolute_path)
                blocks.append(
                    Block(
                        source=source_name,
                        relative_path=relative_path,
                        absolute_path=absolute_path,
                        name=name,
                        description=description,
                        tags=tags,
                    )
                )

    return sorted(blocks, key=lambda block: (block.source, str(block.relative_path)))
