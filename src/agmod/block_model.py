"""Data models for source and project blocks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class BlockMetadata:
    """Represents canonical metadata extracted from frontmatter.

    Args:
        block_id: Canonical block identifier.
        name: Canonical display name.
        block_type: Block type (e.g., spec, impl, tool).
        scope: Scope classification.
        version: Version string.
        status: Status string.
        revised: Revision string or date.
        summary: Short summary of the block.
        tags: Canonical tags.
    """

    block_id: str | None
    name: str | None
    block_type: str | None
    scope: str | None
    version: str | None
    status: str | None
    revised: str | None
    summary: str | None
    tags: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Block:
    """Represents a block discovered in a source directory.

    Args:
        source: Source registry name.
        relative_path: Path relative to the source root.
        absolute_path: Absolute filesystem path to the block.
        name: Display name.
        description: Short description (may be empty).
        tags: Tags extracted from metadata.
    """

    source: str
    relative_path: Path
    absolute_path: Path
    name: str
    description: str
    tags: tuple[str, ...]

    def preview(self, max_lines: int = 20) -> str:
        """Return a preview string of the block content.

        Args:
            max_lines: Maximum number of lines to return.

        Returns:
            Preview content, or an empty string if unavailable.
        """

        if max_lines <= 0:
            return ""

        try:
            with self.absolute_path.open("r", encoding="utf-8") as handle:
                lines = []
                for _ in range(max_lines):
                    line = handle.readline()
                    if not line:
                        break
                    lines.append(line.rstrip("\n"))
        except OSError:
            return ""

        return "\n".join(lines)


@dataclass(frozen=True, slots=True)
class ProjectBlock(Block):
    """Represents a block present in the current project."""

    project_root: Path
