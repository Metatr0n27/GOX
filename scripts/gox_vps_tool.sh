#!/usr/bin/env bash
set -euo pipefail

SESSION="gox-finish"
LOG="/root/gox-vps-finish.log"
DETACHED="https://raw.githubusercontent.com/Metatr0n27/GOX/gox/remote-steward/scripts/vps_detached_finish.sh"

cmd="${1:-start}"

case "$cmd" in
  start)
    exec bash -c "curl -fsSL '$DETACHED' | bash"
    ;;
  status)
    echo "=== GOX VPS TOOL STATUS ==="
    if command -v tmux >/dev/null 2>&1 && tmux has-session -t "$SESSION" 2>/dev/null; then
      echo "SESSION=RUNNING"
    else
      echo "SESSION=NOT_RUNNING"
    fi
    if [ -f "$LOG" ]; then
      echo "--- LAST 60 LOG LINES ---"
      tail -n 60 "$LOG"
    else
      echo "LOG=NOT_CREATED_YET"
    fi
    ;;
  resume)
    if command -v tmux >/dev/null 2>&1 && tmux has-session -t "$SESSION" 2>/dev/null; then
      exec tmux attach -t "$SESSION"
    fi
    echo "No running GOX session. Use: gox-vps start"
    exit 1
    ;;
  stop)
    tmux kill-session -t "$SESSION" 2>/dev/null || true
    echo "GOX VPS detached session stopped."
    ;;
  *)
    echo "Usage: gox-vps {start|status|resume|stop}"
    exit 2
    ;;
esac
