"""Copy and remove blocks in the project repository."""

from __future__ import annotations

from pathlib import Path
import shutil

from agmod.block_model import Block, ProjectBlock
from agmod.scanner import extract_metadata


def ensure_project_llm_dir(project_root: Path) -> Path:
    """Ensure the project's /llm directory exists.

    Args:
        project_root: Root of the project repository.

    Returns:
        Path to the llm directory.
    """

    llm_dir = project_root / "llm"
    llm_dir.mkdir(parents=True, exist_ok=True)
    return llm_dir


def copy_block(block: Block, project_root: Path, allow_overwrite: bool) -> Path:
    """Copy a block into the project /llm directory.

    Args:
        block: Source block to copy.
        project_root: Root of the project repository.
        allow_overwrite: Whether to overwrite existing files.

    Returns:
        Path to the copied block in the project.

    Raises:
        FileExistsError: If the target exists and overwrite is not allowed.
    """

    llm_dir = ensure_project_llm_dir(project_root)
    destination = llm_dir / block.relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists() and not allow_overwrite:
        raise FileExistsError(f"Block already exists: {destination}")

    shutil.copy2(block.absolute_path, destination)
    return destination


def remove_project_block(project_root: Path, relative_path: Path) -> None:
    """Remove a block from the project /llm directory.

    Args:
        project_root: Root of the project repository.
        relative_path: Path relative to /llm.
    """

    target = project_root / "llm" / relative_path
    target.unlink()


def list_project_blocks(project_root: Path) -> list[ProjectBlock]:
    """List blocks present in the project's /llm directory.

    Args:
        project_root: Root of the project repository.

    Returns:
        List of ProjectBlock entries.
    """

    llm_dir = ensure_project_llm_dir(project_root)
    blocks: list[ProjectBlock] = []
    for path in llm_dir.rglob("*.md"):
        relative_path = path.relative_to(llm_dir)
        name, description, tags = extract_metadata(path)
        blocks.append(
            ProjectBlock(
                source="project",
                relative_path=relative_path,
                absolute_path=path,
                name=name,
                description=description,
                tags=tags,
                project_root=project_root,
            )
        )

    return sorted(blocks, key=lambda block: str(block.relative_path))
