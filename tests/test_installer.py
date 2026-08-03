from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tarfile

from agmod.config import DEFAULT_CONFIG_TEXT


def test_installer_creates_config_once(tmp_path: Path) -> None:
    # [T-260803-1]
    payload_dir = tmp_path / "payload"
    payload_dir.mkdir()
    binary = payload_dir / "agmod"
    binary.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    binary.chmod(0o755)
    archive = tmp_path / "agmod-linux-x86_64.tar.gz"
    with tarfile.open(archive, "w:gz") as handle:
        handle.add(binary, arcname="agmod")

    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    fake_curl = fake_bin / "curl"
    fake_curl.write_text(
        '#!/usr/bin/env bash\n/bin/cp "${FAKE_ARCHIVE}" "${4}"\n',
        encoding="utf-8",
    )
    fake_curl.chmod(0o755)

    user_home = tmp_path / "home"
    user_home.mkdir()
    install_dir = tmp_path / "bin"
    environment = os.environ.copy()
    environment.pop("SUDO_USER", None)
    environment.update(
        {
            "AGMOD_INSTALL_DIR": str(install_dir),
            "FAKE_ARCHIVE": str(archive),
            "HOME": str(user_home),
            "PATH": f"{fake_bin}:{environment['PATH']}",
        }
    )
    installer = Path(__file__).parents[1] / "scripts" / "install.sh"

    subprocess.run([str(installer)], check=True, env=environment)
    config_path = user_home / ".config" / "agmod" / "config.toml"
    assert config_path.read_text(encoding="utf-8") == DEFAULT_CONFIG_TEXT
    assert (install_dir / "agmod").exists()

    custom = "[sources]\ncustom = '/var/lib/blocks'\n"
    config_path.write_text(custom, encoding="utf-8")
    subprocess.run([str(installer)], check=True, env=environment)
    assert config_path.read_text(encoding="utf-8") == custom
