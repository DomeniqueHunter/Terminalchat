#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

export CURSED_UID="${CURSED_UID:-1000}"
export CURSED_GID="${CURSED_GID:-1000}"

check_data() {
    mkdir -p game_data
    if [ "$(stat -c %u game_data)" != "$CURSED_UID" ]; then
        echo "game_data is not owned by $CURSED_UID:$CURSED_GID." >&2
        echo "Fix it once with: sudo chown -R $CURSED_UID:$CURSED_GID game_data" >&2
        exit 1
    fi
}

BACKUP_DIR="${CURSED_BACKUPS:-backups}"
BACKUP_KEEP="${CURSED_BACKUP_KEEP:-14}"

backup() {
    mkdir -p "$BACKUP_DIR"
    local file="$BACKUP_DIR/cursed_descent_backup_$(date +%Y-%m-%d_%H%M%S).tar.gz"
    if ! docker compose exec -T game python -m cursed_descent.backup create --data /data > "$file.part"; then
        rm -f "$file.part"
        echo "Backup failed. Is the server running (./console.sh start)?" >&2
        exit 1
    fi
    mv "$file.part" "$file"
    echo "Backup written: $file ($(du -h "$file" | cut -f1))"
    ls -1t "$BACKUP_DIR"/cursed_descent_backup_*.tar.gz | tail -n +$((BACKUP_KEEP + 1)) | xargs -r rm -f --
}

restore() {
    local file="${1:-}"
    if [ -z "$file" ] || [ ! -f "$file" ]; then
        echo "usage: ./console.sh restore <backup.tar.gz>" >&2
        exit 1
    fi
    if docker compose ps --status running --services | grep -q game; then
        backup
    fi
    docker compose stop game
    docker compose run --rm -T --no-deps --entrypoint python game -m cursed_descent.backup restore --data /data < "$file"
    docker compose up -d
    echo "Restored from $file"
}

backups() {
    ls -1t "$BACKUP_DIR"/cursed_descent_backup_*.tar.gz 2>/dev/null || echo "No backups yet."
}

usage() {
    echo "usage: ./console.sh [build|start|debug|stop|restart [--public]|status|logs|backup|backups|restore <file>|admin ...]"
    echo "       start, debug and restart accept --public (listen on 0.0.0.0 instead of 127.0.0.1)"
}

command="${1:-}"
if [ "$#" -gt 0 ]; then
    shift
fi
if [ "${1:-}" = "--public" ]; then
    case "$command" in
        start|debug|restart)
            export CURSED_BIND=0.0.0.0
            echo "Public mode: the game listens on 0.0.0.0:6969 (plain http, reachable from the network)."
            shift ;;
        *) usage; exit 1 ;;
    esac
fi

case "$command" in
    build) docker compose build ;;
    start) check_data &&  docker compose up -d --build ;;
    debug) check_data &&  CURSED_DEBUG=1 docker compose up -d --build --force-recreate ;;
    stop) docker compose down ;;
    restart) check_data &&  docker compose up -d --build --force-recreate ;;
    status) docker compose ps ;;
    logs) docker compose logs -f --tail 100 ;;
    backup) backup ;;
    backups) backups ;;
    restore) restore "${1:-}" ;;
    admin) docker compose exec game python -m cursed_descent.admin_cli --data /data "$@" ;;
    *) usage; exit 1 ;;
esac
