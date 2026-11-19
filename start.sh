#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

case "${1:-web}" in
    web) shift || true; exec python3 -m cursed_descent.web "$@" ;;
    -*) exec python3 -m cursed_descent.web "$@" ;;
    console) shift; exec python3 -m cursed_descent.console "$@" ;;
    test) shift; exec python3 -m pytest "$@" ;;
    reset) shift; exec python3 -m cursed_descent.reset_dungeon "$@" ;;
    *) echo "usage: ./start.sh [web|console|test|reset] [args]"; exit 1 ;;
esac
