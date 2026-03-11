"""Maintain the managed AGENTS.md section for project blocks."""

from __future__ import annotations

from pathlib import Path


MANAGED_START = "<!-- agmod:start -->"
MANAGED_END = "<!-- agmod:end -->"


def build_managed_section(block_paths: list[Path]) -> list[str]:
    """Build the managed section contents between markers.

    Args:
        block_paths: Paths relative to the project root.

    Returns:
        List of lines to place between managed markers.
    """

    sorted_paths = sorted({path.as_posix() for path in block_paths})
    return [f"- {path}" for path in sorted_paths]


def build_full_section(block_paths: list[Path]) -> list[str]:
    """Build the full managed section including header and markers."""

    lines = [
        "### LLM Context Blocks",
        "",
        "These files contain reusable instructions and workflows",
        "that may be relevant when working in this repository.",
        "",
        MANAGED_START,
        "",
    ]
    lines.extend(build_managed_section(block_paths))
    lines.extend(["", MANAGED_END])
    return lines


def update_agents_file(agents_path: Path, block_paths: list[Path]) -> None:
    """Update AGENTS.md with the managed LLM block section.

    Args:
        agents_path: Path to AGENTS.md.
        block_paths: Paths relative to the project root.
    """

    if not agents_path.exists():
        return

    lines = agents_path.read_text(encoding="utf-8").splitlines()
    managed_lines = build_managed_section(block_paths)

    start_index = None
    end_index = None
    for idx, line in enumerate(lines):
        if line.strip() == MANAGED_START:
            start_index = idx
        if line.strip() == MANAGED_END:
            end_index = idx
            break

    if start_index is not None and end_index is not None and start_index < end_index:
        new_lines = lines[: start_index + 1]
        new_lines.append("")
        new_lines.extend(managed_lines)
        new_lines.append("")
        new_lines.extend(lines[end_index:])
        agents_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return

    insert_at = _insertion_index(lines)
    updated = lines[:insert_at]
    if updated and updated[-1].strip() != "":
        updated.append("")
    updated.extend(build_full_section(block_paths))
    if insert_at < len(lines):
        updated.append("")
        updated.extend(lines[insert_at:])

    agents_path.write_text("\n".join(updated) + "\n", encoding="utf-8")


def _insertion_index(lines: list[str]) -> int:
    if not lines:
        return 0
    if lines[0].startswith("#"):
        if len(lines) > 1 and lines[1].startswith("#"):
            return 2
        return 1
    return 0
