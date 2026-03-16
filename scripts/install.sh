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

echo "Installed agmod to ${INSTALL_DIR}/agmod"
echo "Ensure ${INSTALL_DIR} is on your PATH."
