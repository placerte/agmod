from __future__ import annotations

from pathlib import Path

import pytest

from agmod.block_model import Block
from agmod.copy_engine import list_project_blocks
from agmod.presets import (
    PresetInstallError,
    PresetResolutionError,
    install_preset,
    parse_preset,
    preset_is_installed,
    resolve_preset,
)
from agmod.scanner import scan_sources


def _canonical_text(block_id: str, block_type: str, body: str = "") -> str:
    return f"""---
id: {block_id}
name: {block_id}
type: {block_type}
scope: core
version: 1.0
status: active
revised: 2026-08-03
summary: Test block.
---

{body}"""


def _catalog(tmp_path: Path, files: dict[str, str]) -> tuple[Path, list[Block]]:
    source = tmp_path / "source"
    source.mkdir()
    for relative_path, content in files.items():
        path = source / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return source, scan_sources({"local": source})


def _find(blocks: list[Block], filename: str) -> Block:
    return next(block for block in blocks if block.relative_path.name == filename)


def test_parse_and_resolve_preset_in_declared_order(tmp_path: Path) -> None:
    # [T-260803-3]
    _, blocks = _catalog(
        tmp_path,
        {
            "presets/starter.md": _canonical_text(
                "PRESET-STARTER", "preset", "## Includes (ordered)\n- BLK-B\n- BLK-A\n"
            ),
            "a.md": _canonical_text("BLK-A", "toolbox"),
            "b.md": _canonical_text("BLK-B", "workflow"),
        },
    )
    preset = _find(blocks, "starter.md")

    definition = parse_preset(preset)
    assert definition is not None
    assert definition.includes == ("BLK-B", "BLK-A")
    assert [block.relative_path.name for block in resolve_preset(preset, blocks)] == [
        "starter.md",
        "b.md",
        "a.md",
    ]


@pytest.mark.parametrize(
    ("files", "message"),
    [
        (
            {
                "preset.md": _canonical_text(
                    "PRESET", "preset", "## Includes (ordered)\n- MISSING\n"
                )
            },
            "missing block MISSING",
        ),
        (
            {
                "preset.md": _canonical_text(
                    "PRESET", "preset", "## Includes (ordered)\n- PRESET\n"
                )
            },
            "includes itself",
        ),
        (
            {
                "preset.md": _canonical_text(
                    "PRESET", "preset", "## Includes (ordered)\n- CHILD\n"
                ),
                "child.md": _canonical_text(
                    "CHILD", "preset", "## Includes (ordered)\n"
                ),
            },
            "nested preset CHILD",
        ),
        (
            {
                "preset.md": _canonical_text(
                    "PRESET", "preset", "## Includes (ordered)\n- DUPLICATE\n"
                ),
                "a.md": _canonical_text("DUPLICATE", "toolbox"),
                "nested/b.md": _canonical_text("DUPLICATE", "workflow"),
            },
            "Duplicate block ID DUPLICATE",
        ),
    ],
)
def test_resolution_rejects_invalid_catalogs(
    tmp_path: Path, files: dict[str, str], message: str
) -> None:
    # [T-260803-3]
    _, blocks = _catalog(tmp_path, files)
    preset = _find(blocks, "preset.md")

    with pytest.raises(PresetResolutionError, match=message):
        resolve_preset(preset, blocks)


def test_install_preset_copies_definition_and_repairs_missing_blocks(
    tmp_path: Path,
) -> None:
    # [T-260803-3]
    _, blocks = _catalog(
        tmp_path,
        {
            "preset.md": _canonical_text(
                "PRESET", "preset", "## Includes (ordered)\n- A\n- B\n"
            ),
            "a.md": _canonical_text("A", "toolbox"),
            "b.md": _canonical_text("B", "workflow"),
        },
    )
    project = tmp_path / "project"
    project.mkdir()
    preset = _find(blocks, "preset.md")

    created = install_preset(preset, blocks, project)
    assert [path.name for path in created] == ["preset.md", "a.md", "b.md"]
    assert preset_is_installed(preset, blocks, list_project_blocks(project))

    (project / "llm" / "b.md").unlink()
    repaired = install_preset(preset, blocks, project)
    assert [path.name for path in repaired] == ["b.md"]


def test_install_preset_preflights_filename_collisions(tmp_path: Path) -> None:
    # [T-260803-3]
    _, blocks = _catalog(
        tmp_path,
        {
            "preset.md": _canonical_text(
                "PRESET", "preset", "## Includes (ordered)\n- A\n"
            ),
            "a.md": _canonical_text("A", "toolbox"),
        },
    )
    project = tmp_path / "project"
    llm_dir = project / "llm"
    llm_dir.mkdir(parents=True)
    (llm_dir / "a.md").write_text("# Different block\n", encoding="utf-8")

    with pytest.raises(PresetInstallError, match="occupied by a different block"):
        install_preset(_find(blocks, "preset.md"), blocks, project)
    assert not (llm_dir / "preset.md").exists()


def test_install_preset_rolls_back_new_files_on_io_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # [T-260803-3]
    _, blocks = _catalog(
        tmp_path,
        {
            "preset.md": _canonical_text(
                "PRESET", "preset", "## Includes (ordered)\n- A\n"
            ),
            "a.md": _canonical_text("A", "toolbox"),
        },
    )
    project = tmp_path / "project"
    project.mkdir()
    calls = 0

    def fail_second_copy(source: Path, destination: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated copy failure")
        destination.write_bytes(source.read_bytes())

    monkeypatch.setattr("agmod.presets.shutil.copy2", fail_second_copy)

    with pytest.raises(PresetInstallError, match="simulated copy failure"):
        install_preset(_find(blocks, "preset.md"), blocks, project)
    assert list((project / "llm").iterdir()) == []
