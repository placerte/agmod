#!/usr/bin/env bash
set -euo pipefail

REPO="placerte/agmod"
INSTALL_DIR="${AGMOD_INSTALL_DIR:-/usr/local/bin}"

OS_NAME="$(uname -s)"
ARCH_NAME="$(uname -m)"

case "${OS_NAME}" in
    Linux)
        OS="linux"
        ;;
    Darwin)
        OS="darwin"
        ;;
    *)
        echo "Unsupported OS: ${OS_NAME}" >&2
        exit 1
        ;;
esac

case "${ARCH_NAME}" in
    x86_64|amd64)
        ARCH="x86_64"
        ;;
    arm64|aarch64)
        ARCH="arm64"
        ;;
    *)
        echo "Unsupported architecture: ${ARCH_NAME}" >&2
        exit 1
        ;;
esac

ASSET="agmod-${OS}-${ARCH}.tar.gz"
URL="https://github.com/${REPO}/releases/latest/download/${ASSET}"

TMP_DIR="$(mktemp -d)"
cleanup() {
    rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

curl -fsSL "${URL}" -o "${TMP_DIR}/${ASSET}"
mkdir -p "${INSTALL_DIR}"
tar -xzf "${TMP_DIR}/${ASSET}" -C "${TMP_DIR}"
install -m 755 "${TMP_DIR}/agmod" "${INSTALL_DIR}/agmod"

TARGET_USER="${SUDO_USER:-}"
TARGET_HOME="${HOME}"
if [[ -n "${TARGET_USER}" && "${TARGET_USER}" != "root" ]]; then
    if [[ "${OS}" == "darwin" ]]; then
        TARGET_HOME="$(dscl . -read "/Users/${TARGET_USER}" NFSHomeDirectory | awk '{print $2}')"
    else
        TARGET_HOME="$(getent passwd "${TARGET_USER}" | cut -d: -f6)"
    fi
    if [[ -z "${TARGET_HOME}" ]]; then
        echo "Could not determine home directory for ${TARGET_USER}." >&2
        exit 1
    fi
fi

CONFIG_DIR="${TARGET_HOME}/.config/agmod"
CONFIG_PATH="${CONFIG_DIR}/config.toml"
if [[ ! -e "${CONFIG_PATH}" ]]; then
    # [S-260803-1] Seed a useful config once; never replace user configuration.
    mkdir -p "${CONFIG_DIR}"
    cat >"${CONFIG_PATH}" <<'EOF'
[sources]
kb_llm = "~/llm-blocks/blocks/"

# Additional source examples:
# personal = "/home/you/llm"
# workflows = "/home/you/workflows"
EOF
    if [[ -n "${TARGET_USER}" && "${TARGET_USER}" != "root" ]]; then
        TARGET_GROUP="$(id -gn "${TARGET_USER}")"
        chown "${TARGET_USER}:${TARGET_GROUP}" "${CONFIG_DIR}" "${CONFIG_PATH}"
    fi
    echo "Created default config at ${CONFIG_PATH}"
else
    echo "Kept existing config at ${CONFIG_PATH}"
fi

echo "Installed agmod to ${INSTALL_DIR}/agmod"
echo "Ensure ${INSTALL_DIR} is on your PATH."
