from pathlib import Path

import pytest

from agmod.block_model import Block
from agmod.copy_engine import copy_block, list_project_blocks, remove_project_block


def _make_block(source_root: Path, relative: Path, content: str) -> Block:
    absolute = source_root / relative
    absolute.parent.mkdir(parents=True, exist_ok=True)
    absolute.write_text(content, encoding="utf-8")
    return Block(
        source="local",
        relative_path=relative,
        absolute_path=absolute,
        name=relative.stem,
        description="",
        tags=(),
    )


def test_copy_block_and_overwrite(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    project_root = tmp_path / "project"
    source_root.mkdir()
    project_root.mkdir()

    block = _make_block(source_root, Path("tool.md"), "# Tool\n")
    destination = copy_block(block, project_root, allow_overwrite=False)

    assert destination.exists()
    assert destination.read_text(encoding="utf-8") == "# Tool\n"

    with pytest.raises(FileExistsError):
        copy_block(block, project_root, allow_overwrite=False)

    _make_block(source_root, Path("tool.md"), "# Tool v2\n")
    destination = copy_block(block, project_root, allow_overwrite=True)
    assert destination.read_text(encoding="utf-8") == "# Tool v2\n"


def test_remove_and_list_project_blocks(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    project_root = tmp_path / "project"
    source_root.mkdir()
    project_root.mkdir()

    block = _make_block(source_root, Path("nested/tool.md"), "# Tool\n")
    copy_block(block, project_root, allow_overwrite=False)

    blocks = list_project_blocks(project_root)
    assert len(blocks) == 1
    assert blocks[0].relative_path == Path("nested/tool.md")

    remove_project_block(project_root, Path("nested/tool.md"))
    assert not (project_root / "llm" / "nested" / "tool.md").exists()
