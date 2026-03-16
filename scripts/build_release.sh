#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${ROOT_DIR}/dist"
WORK_DIR="${ROOT_DIR}/build"
RELEASE_DIR="${DIST_DIR}/release"
SPEC_FILE="${ROOT_DIR}/agmod.spec"

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

if [[ ! -f "${SPEC_FILE}" ]]; then
    echo "Missing ${SPEC_FILE}. Generate it with: uv run pyinstaller --onefile --name agmod --specpath . src/agmod/__main__.py" >&2
    exit 1
fi

rm -rf "${DIST_DIR}" "${WORK_DIR}"

uv run pyinstaller "${SPEC_FILE}" \
    --distpath "${DIST_DIR}" \
    --workpath "${WORK_DIR}" \
    --specpath "${WORK_DIR}"

mkdir -p "${RELEASE_DIR}"
tar -C "${DIST_DIR}" -czf "${RELEASE_DIR}/agmod-${OS}-${ARCH}.tar.gz" agmod
cp "${ROOT_DIR}/scripts/install.sh" "${RELEASE_DIR}/install.sh"

echo "Release assets written to ${RELEASE_DIR}"
