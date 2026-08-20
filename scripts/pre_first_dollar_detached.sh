#!/usr/bin/env bash
set -euo pipefail

SESSION="gox-pre-dollar"
LOG="/root/gox-pre-dollar.log"
RUNNER="/root/gox-pre-dollar-runner.sh"
URL="https://raw.githubusercontent.com/Metatr0n27/GOX/4983905dd18318ee1f2d9335e3637f4f1020bbb9/scripts/pre_first_dollar_finish.sh"

if ! command -v tmux >/dev/null 2>&1; then
  apt-get update -y >/dev/null 2>&1 || true
  apt-get install -y tmux >/dev/null 2>&1
fi

cat > "$RUNNER" <<EOF
#!/usr/bin/env bash
set -euo pipefail
curl -fsSL "$URL" | bash > "$LOG" 2>&1
RC=\$?
echo "GOX_PRE_DOLLAR_EXIT=\$RC" >> "$LOG"
exit \$RC
EOF
chmod 700 "$RUNNER"

tmux kill-session -t "$SESSION" 2>/dev/null || true
rm -f "$LOG"
tmux new-session -d -s "$SESSION" "bash $RUNNER"

echo "GOX_PRE_DOLLAR_SESSION=STARTED"
echo "SESSION=$SESSION"
echo "LOG=$LOG"
echo "SAFE_TO_LEAVE_BROWSER=yes"
echo "STATUS_COMMAND=tmux has-session -t $SESSION 2>/dev/null && echo RUNNING || echo STOPPED; tail -n 160 $LOG"
