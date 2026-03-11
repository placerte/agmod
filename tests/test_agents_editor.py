from pathlib import Path

from agmod.agents_editor import MANAGED_END, MANAGED_START, update_agents_file


def test_update_agents_inserts_section(tmp_path: Path) -> None:
    agents = tmp_path / "AGENTS.md"
    agents.write_text(
        "# AGENTS.md\n# Guidance for agentic coders working in this repo.\n\n## Other\n",
        encoding="utf-8",
    )

    update_agents_file(agents, [Path("llm/toolboxes/python_toolbox.md")])
    content = agents.read_text(encoding="utf-8")

    assert "### LLM Context Blocks" in content
    assert MANAGED_START in content
    assert MANAGED_END in content
    assert "- llm/toolboxes/python_toolbox.md" in content


def test_update_agents_replaces_between_markers(tmp_path: Path) -> None:
    agents = tmp_path / "AGENTS.md"
    agents.write_text(
        """# AGENTS.md
# Guidance for agentic coders working in this repo.

### LLM Context Blocks

These files contain reusable instructions and workflows
that may be relevant when working in this repository.

<!-- agmod:start -->

- llm/old.md

<!-- agmod:end -->

## Tail
""",
        encoding="utf-8",
    )

    update_agents_file(agents, [Path("llm/new.md")])
    content = agents.read_text(encoding="utf-8")

    assert "- llm/old.md" not in content
    assert "- llm/new.md" in content
    assert "## Tail" in content
