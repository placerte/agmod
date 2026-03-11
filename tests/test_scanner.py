from pathlib import Path

from agmod.scanner import extract_metadata, scan_sources


def test_scan_sources_ignores_hidden_dirs(tmp_path: Path) -> None:
    source = tmp_path / "source"
    hidden = source / ".hidden"
    visible = source / "visible"
    hidden.mkdir(parents=True)
    visible.mkdir(parents=True)

    (hidden / "skip.md").write_text("# Hidden\n", encoding="utf-8")
    (visible / "doc.md").write_text("# Visible\n", encoding="utf-8")

    blocks = scan_sources({"local": source})

    assert len(blocks) == 1
    assert blocks[0].relative_path == Path("visible/doc.md")


def test_extract_metadata_prefers_frontmatter(tmp_path: Path) -> None:
    block = tmp_path / "block.md"
    block.write_text(
        """---\nname: Custom\ndescription: Desc\ntags: [alpha, beta]\n---\n# Heading\n""",
        encoding="utf-8",
    )

    name, description, tags = extract_metadata(block)

    assert name == "Custom"
    assert description == "Desc"
    assert tags == ("alpha", "beta")
