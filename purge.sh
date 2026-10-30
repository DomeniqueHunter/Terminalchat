#!/usr/bin/env bash
set -euo pipefail

APP_NAME="terminalchat"
BASE_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
TMUX_SOCKET="terminalchat"

ASSUME_YES=0
DRY_RUN=0
REMOVE_VENV=0
KEEP_CONFIG=0
KEEP_DATA=0
KEEP_CACHE=0

TARGETS=()

usage() {
    cat <<EOF
Usage: ./purge.sh [options]

Deletes the configuration (including the stored password), chat logs and
other data, and the eicon cache of terminalchat. The program itself stays.

Options:
  --keep-config   keep the configuration
  --keep-data     keep chat logs and data
  --keep-cache    keep the eicon cache
  --venv          also delete ./venv (run ./setup.sh to recreate it)
  -n, --dry-run   only show what would be deleted
  -y, --yes       do not ask for confirmation
  -h, --help      show this help
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
            --keep-config) KEEP_CONFIG=1 ;;
            --keep-data) KEEP_DATA=1 ;;
            --keep-cache) KEEP_CACHE=1 ;;
            --venv) REMOVE_VENV=1 ;;
            -n|--dry-run) DRY_RUN=1 ;;
            -y|--yes) ASSUME_YES=1 ;;
            -h|--help) usage; exit 0 ;;
            *) usage >&2; fail "unknown option: $1" ;;
        esac
        shift
    done
}

expand_home() {
    local path="$1"
    # shellcheck disable=SC2088
    if [[ "${path}" == "~" || "${path}" == "~/"* ]]; then
        path="${HOME}${path:1}"
    fi
    printf '%s\n' "${path}"
}

is_safe_path() {
    local path
    path="$(readlink -m "$1")"
    case "${path}" in
        ""|"/"|"${HOME}"|"${HOME}/"|"/home"|"/root"|"/usr"*|"/etc"*|"/bin"*|"/var") return 1 ;;
    esac
    return 0
}

add_target() {
    local path="$1"
    [[ -e "${path}" || -L "${path}" ]] || return 0
    is_safe_path "${path}" || fail "refusing to delete unsafe path: ${path}"
    TARGETS+=("${path}")
}

config_file() {
    if [[ -n "${TERMINALCHAT_CONFIG:-}" ]]; then
        expand_home "${TERMINALCHAT_CONFIG}"
    else
        printf '%s\n' "${XDG_CONFIG_HOME:-${HOME}/.config}/${APP_NAME}/config.json"
    fi
}

configured_data_dir() {
    local file="$1"
    [[ -f "${file}" ]] || return 0
    python3 -c 'import json, sys; print(json.load(open(sys.argv[1])).get("data_dir") or "")' "${file}" 2>/dev/null || true
}

collect_config() {
    local file="$1"
    if [[ -n "${TERMINALCHAT_CONFIG:-}" ]]; then
        add_target "${file}"
        add_target "${file%.json}.tmp"
    else
        add_target "$(dirname "${file}")"
    fi
    add_target "${BASE_DIR}/src/config.json"
}

collect_data() {
    local custom="$1"
    local dir
    if [[ -n "${TERMINALCHAT_DATA:-}" || -n "${custom}" ]]; then
        dir="$(expand_home "${TERMINALCHAT_DATA:-${custom}}")"
        add_target "${dir}/chats"
        add_target "${dir}/debug.log"
    else
        add_target "${XDG_DATA_HOME:-${HOME}/.local/share}/${APP_NAME}"
    fi
    add_target "${BASE_DIR}/src/chats"
    local log
    for log in "${BASE_DIR}"/src/*.log; do
        add_target "${log}"
    done
}

collect_cache() {
    add_target "${XDG_CACHE_HOME:-${HOME}/.cache}/${APP_NAME}"
}

stop_running_client() {
    command -v tmux >/dev/null 2>&1 || return 0
    env -u TMUX tmux -L "${TMUX_SOCKET}" has-session 2>/dev/null || return 0
    info "terminalchat is still running in the background"
    if [[ ${DRY_RUN} -eq 1 ]]; then
        echo "would stop the background session"
        return 0
    fi
    if [[ ${ASSUME_YES} -eq 0 ]]; then
        read -r -p "Stop it now? [y/N] " answer
        [[ "${answer}" =~ ^[yYjJ] ]] || fail "stop the client first (/quit), then run this script again"
    fi
    env -u TMUX tmux -L "${TMUX_SOCKET}" kill-server
    echo "stopped"
}

confirm() {
    [[ ${ASSUME_YES} -eq 1 ]] && return 0
    read -r -p "Delete all of this? [y/N] " answer
    [[ "${answer}" =~ ^[yYjJ] ]]
}

main() {
    parse_args "$@"

    local file custom
    file="$(config_file)"
    custom="$(configured_data_dir "${file}")"
    [[ -z "${custom}" ]] && custom="$(configured_data_dir "${BASE_DIR}/src/config.json")"

    [[ ${KEEP_CONFIG} -eq 1 ]] || collect_config "${file}"
    [[ ${KEEP_DATA} -eq 1 ]] || collect_data "${custom}"
    [[ ${KEEP_CACHE} -eq 1 ]] || collect_cache
    [[ ${REMOVE_VENV} -eq 1 ]] && add_target "${BASE_DIR}/venv"

    if [[ ${#TARGETS[@]} -eq 0 ]]; then
        info "Nothing to delete"
        exit 0
    fi

    info "The following will be deleted:"
    local target
    for target in "${TARGETS[@]}"; do
        printf '  %s  (%s)\n' "${target}" "$(du -sh "${target}" 2>/dev/null | cut -f1)"
    done

    stop_running_client

    if [[ ${DRY_RUN} -eq 1 ]]; then
        info "Dry run, nothing deleted"
        exit 0
    fi
    confirm || { echo "Aborted"; exit 1; }

    for target in "${TARGETS[@]}"; do
        rm -rf -- "${target}"
    done
    if [[ -n "${TERMINALCHAT_DATA:-}${custom}" ]]; then
        rmdir -- "$(expand_home "${TERMINALCHAT_DATA:-${custom}}")" 2>/dev/null || true
    fi
    info "Done"
}

main "$@"
