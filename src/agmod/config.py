"""Configuration loading for agmod sources."""

from __future__ import annotations

from pathlib import Path
import logging
import tomllib


DEFAULT_CONFIG_DIR = Path.home() / ".config" / "agmod"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.toml"


def ensure_config_file(config_path: Path | None = None) -> Path:
    """Ensure the config file exists and return its path.

    Args:
        config_path: Optional override for the config path.

    Returns:
        The path to the config file.
    """

    resolved_path = config_path or DEFAULT_CONFIG_PATH
    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    if not resolved_path.exists():
        resolved_path.write_text("[sources]\n", encoding="utf-8")

    return resolved_path


def load_sources(config_path: Path | None = None) -> dict[str, Path]:
    """Load and validate source directories from config.

    Args:
        config_path: Optional override for the config path.

    Returns:
        Mapping of source name to absolute Path.
    """

    resolved_path = ensure_config_file(config_path)
    try:
        raw = resolved_path.read_bytes()
    except OSError as exc:
        raise RuntimeError(f"Failed to read config file: {resolved_path}") from exc

    if not raw.strip():
        return {}

    try:
        data = tomllib.loads(raw.decode("utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise RuntimeError(f"Invalid TOML in config: {resolved_path}") from exc

    sources = data.get("sources", {})
    if not isinstance(sources, dict):
        raise RuntimeError("Config 'sources' must be a table")

    valid: dict[str, Path] = {}
    for name, value in sources.items():
        if not isinstance(name, str) or not isinstance(value, str):
            logging.warning("Ignoring invalid source entry: %s", name)
            continue

        path = Path(value).expanduser()
        if not path.is_dir():
            logging.warning("Ignoring missing source directory: %s", path)
            continue

        valid[name] = path

    return valid
