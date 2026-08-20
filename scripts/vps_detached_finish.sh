#!/usr/bin/env bash
set -euo pipefail

SESSION="gox-finish"
RUNNER="/root/gox-vps-finish-runner.sh"
LOG="/root/gox-vps-finish.log"
REMOTE="https://github.com/Metatr0n27/GOX/raw/refs/heads/gox/remote-steward/scripts/vps_finish_everything.sh"

if ! command -v tmux >/dev/null 2>&1; then
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y tmux >/dev/null
fi

cat > "$RUNNER" <<EOF
#!/usr/bin/env bash
set -o pipefail
curl -fsSL "$REMOTE" | bash 2>&1 | tee "$LOG"
code=\${PIPESTATUS[1]:-0}
echo "GOX_DETACHED_RUN_FINISHED=\$code" | tee -a "$LOG"
exec bash
EOF
chmod 700 "$RUNNER"

tmux kill-session -t "$SESSION" 2>/dev/null || true
tmux new-session -d -s "$SESSION" "$RUNNER"

echo "GOX_DETACHED_SESSION=STARTED"
echo "SESSION=$SESSION"
echo "LOG=$LOG"
echo "SAFE_TO_LEAVE_BROWSER=yes"
echo "Hostinger does not need to stay open."
echo "To check later: tmux has-session -t $SESSION 2>/dev/null && echo RUNNING || echo STOPPED; tail -n 80 $LOG"
exit 0
