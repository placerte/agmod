"""Command-line dispatch for agmod."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import sys

from agmod.tui.app import run
from agmod.updater import UpdateError, update_agmod


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agmod")
    parser.add_argument(
        "--update",
        action="store_true",
        help="download and install the latest agmod release",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the TUI or update the installed agmod release.

    Args:
        argv: Optional arguments excluding the executable name.

    Returns:
        Process exit status: zero on success, one when updating fails.
    """

    # [S-260803-5] [I-260803-5]
    arguments = _build_parser().parse_args(argv)
    if not arguments.update:
        run()
        return 0

    try:
        update_agmod()
    except UpdateError as exc:
        print(f"Update failed: {exc}", file=sys.stderr)
        return 1
    return 0
