from __future__ import annotations

from io import BytesIO
from pathlib import Path
import subprocess

import pytest

from agmod import cli, updater
from agmod.updater import UpdateError


def test_cli_runs_tui_without_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(cli, "run", lambda: calls.append("run"))

    assert cli.main([]) == 0
    assert calls == ["run"]


def test_cli_update_dispatches_without_starting_tui(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    monkeypatch.setattr(cli, "run", lambda: calls.append("run"))
    monkeypatch.setattr(cli, "update_agmod", lambda: calls.append("update"))

    # [T-260803-5]
    assert cli.main(["--update"]) == 0
    assert calls == ["update"]


def test_cli_reports_update_failure(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail_update() -> None:
        raise UpdateError("network unavailable")

    monkeypatch.setattr(cli, "update_agmod", fail_update)

    assert cli.main(["--update"]) == 1
    assert "Update failed: network unavailable" in capsys.readouterr().err


def test_updater_downloads_and_executes_official_installer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    installer = b"#!/usr/bin/env bash\nexit 0\n"
    executed: list[bytes] = []

    def fake_urlopen(url: str, timeout: int) -> BytesIO:
        assert url == updater.INSTALLER_URL
        assert timeout == 30
        return BytesIO(installer)

    def fake_run(command: list[str], check: bool) -> None:
        assert check
        installer_path = Path(command[0])
        executed.append(installer_path.read_bytes())
        assert installer_path.stat().st_mode & 0o700 == 0o700

    monkeypatch.setattr(updater, "urlopen", fake_urlopen)
    monkeypatch.setattr(updater.subprocess, "run", fake_run)

    updater.update_agmod()

    assert executed == [installer]


def test_updater_suggests_sudo_when_installer_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        updater,
        "urlopen",
        lambda url, timeout: BytesIO(b"#!/usr/bin/env bash\nexit 1\n"),
    )

    def fail_run(command: list[str], check: bool) -> None:
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(updater.subprocess, "run", fail_run)

    with pytest.raises(UpdateError, match="sudo agmod --update"):
        updater.update_agmod()
