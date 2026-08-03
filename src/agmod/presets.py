"""Preset parsing, resolution, and installation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Iterable

from agmod.block_model import Block, ProjectBlock
from agmod.copy_engine import ensure_project_llm_dir, list_project_blocks
from agmod.scanner import parse_block_metadata, read_frontmatter

INCLUDES_HEADING = "## includes (ordered)"


class PresetError(RuntimeError):
    """Base error for invalid or unresolvable presets."""


class PresetResolutionError(PresetError):
    """Raised when preset IDs cannot be resolved unambiguously."""


class PresetInstallError(PresetError):
    """Raised when a resolved preset cannot be installed safely."""


@dataclass(frozen=True, slots=True)
class PresetDefinition:
    """A canonical preset and its ordered included block IDs.

    Args:
        block: Source file containing the preset definition.
        block_id: Canonical ID from YAML frontmatter.
        includes: Canonical block IDs in declared installation order.
    """

    block: Block
    block_id: str
    includes: tuple[str, ...]


def block_identity(block: Block) -> tuple[str | None, str | None]:
    """Return a block's canonical ID and type, when available.

    Args:
        block: Source or project block to inspect.

    Returns:
        Tuple of canonical ID and canonical type.
    """

    frontmatter, _, _ = read_frontmatter(block.absolute_path)
    metadata = parse_block_metadata(frontmatter)
    return metadata.block_id, metadata.block_type


def parse_preset(block: Block) -> PresetDefinition | None:
    """Parse a canonical preset block.

    Args:
        block: Block whose frontmatter and body should be inspected.

    Returns:
        A preset definition, or ``None`` when the block is not a preset.

    Raises:
        PresetResolutionError: If a preset is missing its ID or includes section.
    """

    # [S-260803-3] [I-260803-3]
    frontmatter, body, has_frontmatter = read_frontmatter(block.absolute_path)
    if not has_frontmatter:
        return None
    metadata = parse_block_metadata(frontmatter)
    if metadata.block_type != "preset":
        return None
    if metadata.block_id is None:
        raise PresetResolutionError(
            f"Preset {block.relative_path.as_posix()} has no canonical ID."
        )

    includes = _parse_includes(body)
    if includes is None:
        raise PresetResolutionError(
            f"Preset {metadata.block_id} has no '## Includes (ordered)' section."
        )
    return PresetDefinition(
        block=block,
        block_id=metadata.block_id,
        includes=includes,
    )


def build_block_id_index(blocks: Iterable[Block]) -> dict[str, Block]:
    """Index canonical blocks by ID and reject duplicate identities.

    Args:
        blocks: Catalog blocks from all configured sources.

    Returns:
        Mapping from canonical ID to its unique source block.

    Raises:
        PresetResolutionError: If two source blocks declare the same ID.
    """

    index: dict[str, Block] = {}
    for block in blocks:
        block_id, _ = block_identity(block)
        if block_id is None:
            continue
        previous = index.get(block_id)
        if previous is not None:
            raise PresetResolutionError(
                f"Duplicate block ID {block_id}: "
                f"{previous.relative_path.as_posix()} and "
                f"{block.relative_path.as_posix()}."
            )
        index[block_id] = block
    return index


def resolve_preset(preset: Block, catalog_blocks: Iterable[Block]) -> list[Block]:
    """Resolve a preset to itself followed by its ordered dependencies.

    Args:
        preset: Selected preset source block.
        catalog_blocks: All blocks available from configured sources.

    Returns:
        Ordered install list beginning with the preset definition.

    Raises:
        PresetResolutionError: If IDs are missing, duplicated, self-referential,
            or resolve to nested presets.
    """

    # [S-260803-3] [I-260803-3]
    definition = parse_preset(preset)
    if definition is None:
        raise PresetResolutionError(
            f"{preset.relative_path.as_posix()} is not a canonical preset."
        )
    index = build_block_id_index(catalog_blocks)

    resolved: list[Block] = [preset]
    seen: set[str] = {definition.block_id}
    for included_id in definition.includes:
        if included_id == definition.block_id:
            raise PresetResolutionError(
                f"Preset {definition.block_id} includes itself."
            )
        if included_id in seen:
            raise PresetResolutionError(
                f"Preset {definition.block_id} includes {included_id} more than once."
            )
        dependency = index.get(included_id)
        if dependency is None:
            raise PresetResolutionError(
                f"Preset {definition.block_id} references missing block {included_id}."
            )
        _, dependency_type = block_identity(dependency)
        if dependency_type == "preset":
            raise PresetResolutionError(
                f"Preset {definition.block_id} includes nested preset {included_id}; "
                "nested presets are not supported."
            )
        resolved.append(dependency)
        seen.add(included_id)
    return resolved


def installed_block_ids(project_blocks: Iterable[ProjectBlock]) -> set[str]:
    """Return canonical IDs found among installed project blocks."""

    ids: set[str] = set()
    for block in project_blocks:
        block_id, _ = block_identity(block)
        if block_id is not None:
            ids.add(block_id)
    return ids


def preset_is_installed(
    preset: Block,
    catalog_blocks: Iterable[Block],
    project_blocks: Iterable[ProjectBlock],
) -> bool:
    """Return whether a preset definition and all dependencies are installed."""

    resolved = resolve_preset(preset, catalog_blocks)
    required_ids: set[str] = set()
    for block in resolved:
        block_id, _ = block_identity(block)
        if block_id is None:
            return False
        required_ids.add(block_id)
    return required_ids <= installed_block_ids(project_blocks)


def install_preset(
    preset: Block,
    catalog_blocks: Iterable[Block],
    project_root: Path,
) -> list[Path]:
    """Install a preset definition and its ordered dependencies.

    Validation completes before writes begin. Existing blocks with matching
    canonical IDs are retained. On an I/O failure, only files created by this
    call are removed.

    Args:
        preset: Selected preset source block.
        catalog_blocks: All blocks available from configured sources.
        project_root: Project receiving the files under ``llm/``.

    Returns:
        Paths newly copied by this operation, in installation order.

    Raises:
        PresetError: If resolution or collision validation fails.
    """

    # [S-260803-3] [I-260803-3]
    install_blocks = resolve_preset(preset, catalog_blocks)
    project_blocks = list_project_blocks(project_root)
    existing_by_id: dict[str, ProjectBlock] = {}
    for project_block in project_blocks:
        block_id, _ = block_identity(project_block)
        if block_id is not None:
            previous = existing_by_id.get(block_id)
            if previous is not None:
                raise PresetInstallError(
                    f"Project contains duplicate block ID {block_id}: "
                    f"{previous.relative_path.as_posix()} and "
                    f"{project_block.relative_path.as_posix()}."
                )
            existing_by_id[block_id] = project_block

    llm_dir = ensure_project_llm_dir(project_root)
    pending: list[tuple[Block, Path]] = []
    pending_names: dict[str, str | None] = {}
    for block in install_blocks:
        block_id, _ = block_identity(block)
        if block_id is not None and block_id in existing_by_id:
            continue
        destination = llm_dir / block.relative_path.name
        other_id = pending_names.get(destination.name)
        if destination.name in pending_names:
            raise PresetInstallError(
                f"Preset contains a filename collision for {destination.name}: "
                f"{other_id or 'unidentified block'} and "
                f"{block_id or 'unidentified block'}."
            )
        if destination.exists():
            raise PresetInstallError(
                f"Cannot install {block_id or block.name}: "
                f"{destination.name} is occupied by a different block."
            )
        pending.append((block, destination))
        pending_names[destination.name] = block_id

    created: list[Path] = []
    try:
        for block, destination in pending:
            shutil.copy2(block.absolute_path, destination)
            created.append(destination)
    except OSError as exc:
        for destination in reversed(created):
            try:
                destination.unlink()
            except OSError:
                pass
        raise PresetInstallError(f"Preset installation failed: {exc}") from exc
    return created


def _parse_includes(body: str) -> tuple[str, ...] | None:
    lines = body.splitlines()
    heading_index: int | None = None
    for index, line in enumerate(lines):
        if line.strip().lower() == INCLUDES_HEADING:
            heading_index = index
            break
    if heading_index is None:
        return None

    includes: list[str] = []
    for line in lines[heading_index + 1 :]:
        stripped = line.strip()
        if stripped.startswith("#"):
            break
        if not stripped:
            continue
        if stripped.startswith("- "):
            included_id = stripped[2:].strip()
            if included_id:
                includes.append(included_id)
    return tuple(includes)
