#!/usr/bin/env bash
set -euo pipefail

APP_NAME="terminalchat"
BASE_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
TMUX_SOCKET="terminalchat"

ASSUME_YES=0
DRY_RUN=0
REMOVE_VENV=0
SELECTED=0
DO_CONFIG=1
DO_DATA=1
DO_LOGS=0
DO_CACHE=1

TARGETS=()
LOG_FILES=()
LOG_DIRS=()

usage() {
    cat <<EOF
Usage: ./purge.sh [options] [components]

Deletes what terminalchat stored outside the program folder. Without
components everything is deleted: configuration (including the stored
password), chat logs and other data, and the eicon and avatar cache.

Components (only the given ones are deleted):
  --config        configuration and stored password
  --data          all data: chat logs, pins, status, ad texts, genders
  --logs          only chat logs and debug.log, keep pins, status etc.
  --eicons        eicon and avatar cache

Options:
  --keep-config   keep the configuration
  --keep-data     keep chat logs and data
  --keep-cache    keep the eicon and avatar cache
  --venv          also delete ./venv (run ./setup.sh to recreate it)
  -n, --dry-run   only show what would be deleted
  -y, --yes       do not ask for confirmation
  -h, --help      show this help

Examples:
  ./purge.sh               delete everything after confirmation
  ./purge.sh -n --logs     show which logs would be deleted
  ./purge.sh -y --eicons   clear the image cache without asking
EOF
}

info() {
    printf '\033[1m==> %s\033[0m\n' "$*"
}

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

select_component() {
    if [[ ${SELECTED} -eq 0 ]]; then
        SELECTED=1
        DO_CONFIG=0
        DO_DATA=0
        DO_LOGS=0
        DO_CACHE=0
    fi
    case "$1" in
        config) DO_CONFIG=1 ;;
        data) DO_DATA=1 ;;
        logs) DO_LOGS=1 ;;
        eicons) DO_CACHE=1 ;;
    esac
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --config) select_component config ;;
            --data) select_component data ;;
            --logs) select_component logs ;;
            --eicons|--cache) select_component eicons ;;
            --keep-config) DO_CONFIG=0 ;;
            --keep-data) DO_DATA=0 ;;
            --keep-cache) DO_CACHE=0 ;;
            --venv) REMOVE_VENV=1 ;;
            -n|--dry-run) DRY_RUN=1 ;;
            -y|--yes) ASSUME_YES=1 ;;
            -h|--help) usage; exit 0 ;;
            *) usage >&2; fail "unknown option: $1" ;;
        esac
        shift
    done
    [[ ${DO_DATA} -eq 1 ]] && DO_LOGS=0
    return 0
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

data_dir() {
    local custom="$1"
    if [[ -n "${TERMINALCHAT_DATA:-}" || -n "${custom}" ]]; then
        expand_home "${TERMINALCHAT_DATA:-${custom}}"
    else
        printf '%s\n' "${XDG_DATA_HOME:-${HOME}/.local/share}/${APP_NAME}"
    fi
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
    dir="$(data_dir "${custom}")"
    if [[ -n "${TERMINALCHAT_DATA:-}" || -n "${custom}" ]]; then
        add_target "${dir}/chats"
        add_target "${dir}/debug.log"
    else
        add_target "${dir}"
    fi
    add_target "${BASE_DIR}/src/chats"
    collect_legacy_logs
}

collect_legacy_logs() {
    local log
    for log in "${BASE_DIR}"/src/*.log; do
        add_target "${log}"
    done
}

collect_logs() {
    local custom="$1"
    local dir chats file
    dir="$(data_dir "${custom}")"
    add_target "${dir}/debug.log"
    collect_legacy_logs
    for chats in "${dir}/chats" "${BASE_DIR}/src/chats"; do
        [[ -d "${chats}" ]] || continue
        is_safe_path "${chats}" || fail "refusing to delete unsafe path: ${chats}"
        LOG_DIRS+=("${chats}")
        while IFS= read -r -d '' file; do
            LOG_FILES+=("${file}")
        done < <(find "${chats}" -type f \( -name '*.log' -o -name '*.log.bak' \) -print0)
    done
}

collect_cache() {
    add_target "${XDG_CACHE_HOME:-${HOME}/.cache}/${APP_NAME}"
}

show_targets() {
    local target chats count size
    for target in "${TARGETS[@]}"; do
        printf '  %s  (%s)\n' "${target}" "$(du -sh "${target}" 2>/dev/null | cut -f1)"
    done
    [[ ${#LOG_FILES[@]} -gt 0 ]] || return 0
    for chats in "${LOG_DIRS[@]}"; do
        count=0
        size=0
        for target in "${LOG_FILES[@]}"; do
            if [[ "${target}" == "${chats}/"* ]]; then
                count=$((count + 1))
                size=$((size + $(stat -c %s "${target}")))
            fi
        done
        [[ ${count} -gt 0 ]] || continue
        printf '  %s: %d chat log files  (%s)\n' "${chats}" "${count}" "$(numfmt --to=iec --suffix=B "${size}")"
    done
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

delete_all() {
    local custom="$1"
    local target chats
    for target in "${TARGETS[@]}"; do
        rm -rf -- "${target}"
    done
    if [[ ${#LOG_FILES[@]} -gt 0 ]]; then
        rm -f -- "${LOG_FILES[@]}"
        for chats in "${LOG_DIRS[@]}"; do
            find "${chats}" -mindepth 1 -type d -empty -delete
        done
    fi
    if [[ ${DO_DATA} -eq 1 && -n "${TERMINALCHAT_DATA:-}${custom}" ]]; then
        rmdir -- "$(data_dir "${custom}")" 2>/dev/null || true
    fi
}

main() {
    parse_args "$@"

    local file custom
    file="$(config_file)"
    custom="$(configured_data_dir "${file}")"
    [[ -z "${custom}" ]] && custom="$(configured_data_dir "${BASE_DIR}/src/config.json")"

    [[ ${DO_CONFIG} -eq 1 ]] && collect_config "${file}"
    [[ ${DO_DATA} -eq 1 ]] && collect_data "${custom}"
    [[ ${DO_LOGS} -eq 1 ]] && collect_logs "${custom}"
    [[ ${DO_CACHE} -eq 1 ]] && collect_cache
    [[ ${REMOVE_VENV} -eq 1 ]] && add_target "${BASE_DIR}/venv"

    if [[ ${#TARGETS[@]} -eq 0 && ${#LOG_FILES[@]} -eq 0 ]]; then
        info "Nothing to delete"
        exit 0
    fi

    info "The following will be deleted:"
    show_targets
    stop_running_client

    if [[ ${DRY_RUN} -eq 1 ]]; then
        info "Dry run, nothing deleted"
        exit 0
    fi
    confirm || { echo "Aborted"; exit 1; }

    delete_all "${custom}"
    info "Done"
}

main "$@"
