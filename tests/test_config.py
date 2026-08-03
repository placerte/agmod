from pathlib import Path

from agmod.config import DEFAULT_CONFIG_TEXT, ensure_config_file, load_sources


def test_ensure_config_file_writes_default_once(tmp_path: Path) -> None:
    # [T-260803-1]
    config_path = tmp_path / "nested" / "config.toml"

    assert ensure_config_file(config_path) == config_path
    assert config_path.read_text(encoding="utf-8") == DEFAULT_CONFIG_TEXT

    config_path.write_text("[sources]\ncustom = '/tmp'\n", encoding="utf-8")
    ensure_config_file(config_path)
    assert config_path.read_text(encoding="utf-8") == "[sources]\ncustom = '/tmp'\n"


def test_default_config_loads_existing_kb_source(tmp_path: Path) -> None:
    # [T-260803-1]
    source = tmp_path / "llm-blocks" / "blocks"
    source.mkdir(parents=True)
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        DEFAULT_CONFIG_TEXT.replace("~/llm-blocks/blocks/", source.as_posix()),
        encoding="utf-8",
    )

    assert load_sources(config_path) == {"kb_llm": source}
