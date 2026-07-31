#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
REPOPILOT_ROOT="$(cd -- "$PROJECT_ROOT/../RepoPilot" && pwd)"

if [[ ! -f "$REPOPILOT_ROOT/main.py" ]]; then
    echo "[ERROR] No se encontró RepoPilot:"
    echo "        $REPOPILOT_ROOT/main.py"
    exit 1
fi

if [[ ! -d "$PROJECT_ROOT/.git" ]]; then
    echo "[ERROR] El proyecto no contiene un repositorio Git:"
    echo "        $PROJECT_ROOT"
    exit 1
fi

python3 "$REPOPILOT_ROOT/main.py" "$PROJECT_ROOT"
EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
    echo
    echo "RepoPilot finalizó con código $EXIT_CODE."
fi

exit "$EXIT_CODE"