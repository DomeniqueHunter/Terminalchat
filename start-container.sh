#!/usr/bin/env bash
set -euo pipefail

data="${CURSED_DATA:-/data}"
port="${CURSED_PORT:-6969}"

mkdir -p "$data"
if [ ! -w "$data" ]; then
    echo "error: $data is not writable for uid $(id -u)" >&2
    exit 1
fi

exec python -m cursed_descent.web --data "$data" --host 0.0.0.0 --port "$port"
