"""Self-update support backed by agmod's official release installer."""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
from urllib.error import URLError
from urllib.request import urlopen

INSTALLER_URL = "https://github.com/placerte/agmod/releases/latest/download/install.sh"


class UpdateError(RuntimeError):
    """Raised when the official installer cannot complete an update."""


def update_agmod(installer_url: str = INSTALLER_URL) -> None:
    """Download and execute the official agmod release installer.

    Args:
        installer_url: HTTPS URL of the installer to execute.

    Raises:
        UpdateError: If downloading, writing, or executing the installer fails.
    """

    # [S-260803-5] [I-260803-5] Reuse the release installer as the single
    # installation workflow, including its config-preservation behavior.
    try:
        with urlopen(installer_url, timeout=30) as response:
            installer_bytes = response.read()
    except (OSError, URLError) as exc:
        raise UpdateError(f"Could not download the agmod installer: {exc}") from exc

    if not installer_bytes:
        raise UpdateError("Downloaded agmod installer was empty.")

    try:
        with tempfile.TemporaryDirectory(prefix="agmod-update-") as temp_dir:
            installer_path = Path(temp_dir) / "install.sh"
            installer_path.write_bytes(installer_bytes)
            installer_path.chmod(0o700)
            subprocess.run([str(installer_path)], check=True)
    except subprocess.CalledProcessError as exc:
        raise UpdateError(
            "The agmod installer failed. If agmod is installed in "
            "/usr/local/bin, rerun with: sudo agmod --update"
        ) from exc
    except OSError as exc:
        raise UpdateError(f"Could not execute the agmod installer: {exc}") from exc
