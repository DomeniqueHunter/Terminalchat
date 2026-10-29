#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
VENV_DIR="${BASE_DIR}/venv"
MIN_PYTHON="3.10"

SKIP_PACKAGES=0
RECREATE_VENV=0
ASSUME_YES=0

usage() {
    cat <<EOF
Usage: ./setup.sh [options]

Installs system packages (tmux, Python with venv support) and creates
the Python environment in ./venv with all requirements.

Options:
  --skip-packages   do not install system packages
  --recreate-venv   delete and recreate ./venv
  -y, --yes         do not ask before installing system packages
  -h, --help        show this help
EOF
}

info() {
    printf '\033[1m==> %s\033[0m\n' "$*"
}

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --skip-packages) SKIP_PACKAGES=1 ;;
            --recreate-venv) RECREATE_VENV=1 ;;
            -y|--yes) ASSUME_YES=1 ;;
            -h|--help) usage; exit 0 ;;
            *) usage; fail "unknown option: $1" ;;
        esac
        shift
    done
}

as_root() {
    if [[ "$(id -u)" -eq 0 ]]; then
        "$@"
    elif command -v sudo >/dev/null 2>&1; then
        sudo "$@"
    else
        fail "need root rights for: $* (sudo not found)"
    fi
}

detect_package_command() {
    if command -v pacman >/dev/null 2>&1; then
        echo "pacman -S --needed tmux python"
    elif command -v apt-get >/dev/null 2>&1; then
        echo "apt-get install tmux python3 python3-venv python3-pip"
    elif command -v dnf >/dev/null 2>&1; then
        echo "dnf install tmux python3 python3-pip"
    elif command -v zypper >/dev/null 2>&1; then
        echo "zypper install tmux python3 python3-pip"
    elif command -v brew >/dev/null 2>&1; then
        echo "brew install tmux python"
    else
        echo ""
    fi
}

install_packages() {
    local package_command
    package_command="$(detect_package_command)"
    if [[ -z "${package_command}" ]]; then
        info "No supported package manager found - please install tmux and Python ${MIN_PYTHON}+ manually"
        return
    fi

    info "System packages: ${package_command}"
    if [[ "${ASSUME_YES}" -eq 0 ]]; then
        read -r -p "Install now? [Y/n] " answer
        if [[ "${answer,,}" == "n" ]]; then
            info "Skipping system packages"
            return
        fi
    fi

    read -r -a args <<< "${package_command}"
    case "${args[0]}" in
        brew)
            "${args[@]}"
            ;;
        apt-get)
            as_root apt-get update
            as_root "${args[@]}" -y
            ;;
        pacman)
            as_root "${args[@]}" --noconfirm
            ;;
        *)
            as_root "${args[@]}" -y
            ;;
    esac
}

find_python() {
    local candidate
    for candidate in python3 python; do
        if command -v "${candidate}" >/dev/null 2>&1 &&
            "${candidate}" -c "import sys; sys.exit(0 if sys.version_info >= (${MIN_PYTHON/./, }) else 1)"; then
            command -v "${candidate}"
            return
        fi
    done
    fail "Python ${MIN_PYTHON} or newer not found"
}

setup_venv() {
    local python
    python="$(find_python)"
    info "Using $(${python} --version) (${python})"

    if [[ "${RECREATE_VENV}" -eq 1 && -d "${VENV_DIR}" ]]; then
        info "Removing old venv"
        rm -rf "${VENV_DIR}"
    fi

    if [[ -x "${VENV_DIR}/bin/python" ]] && ! "${VENV_DIR}/bin/python" -c "" 2>/dev/null; then
        info "Existing venv is broken (Python was probably updated) - recreating"
        rm -rf "${VENV_DIR}"
    fi

    if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
        info "Creating venv in ${VENV_DIR}"
        "${python}" -m venv "${VENV_DIR}"
    fi

    if ! "${VENV_DIR}/bin/python" -m pip --version >/dev/null 2>&1; then
        info "pip missing in venv - installing via ensurepip"
        "${VENV_DIR}/bin/python" -m ensurepip --upgrade
    fi

    info "Installing Python requirements"
    "${VENV_DIR}/bin/python" -m pip install --upgrade pip
    "${VENV_DIR}/bin/python" -m pip install -r "${BASE_DIR}/requirements.txt"
}

check_result() {
    chmod +x "${BASE_DIR}/terminalchat"
    if command -v tmux >/dev/null 2>&1; then
        info "tmux: $(tmux -V)"
    else
        info "tmux not installed - the client works, but /minimize is unavailable"
    fi
    "${VENV_DIR}/bin/python" -c "import textual, textual_image, aiohttp, websockets, PIL" ||
        fail "Python packages could not be imported"
    info "Done. Start the client with: ./terminalchat"
}

main() {
    parse_args "$@"
    if [[ "${SKIP_PACKAGES}" -eq 0 ]]; then
        install_packages
    fi
    setup_venv
    check_result
}

main "$@"
