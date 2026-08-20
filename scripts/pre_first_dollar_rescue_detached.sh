#!/usr/bin/env bash
set -euo pipefail

SESSION="gox-pre-dollar"
LOG="/root/gox-pre-dollar.log"
RUNNER="/root/gox-pre-dollar-rescue-runner.sh"
MAILBOX="/var/lib/gox-steward/mailbox"
BRANCH="gox/remote-steward"

if ! command -v tmux >/dev/null 2>&1; then
  apt-get update -y >/dev/null 2>&1 || true
  apt-get install -y tmux >/dev/null 2>&1
fi

cat > "$RUNNER" <<'EOF'
#!/usr/bin/env bash
set +e
LOG="/root/gox-pre-dollar.log"
MAILBOX="/var/lib/gox-steward/mailbox"
BRANCH="gox/remote-steward"
exec > >(tee -a "$LOG") 2>&1

echo "=== GOX PRE-DOLLAR RESCUE ==="
echo "started=$(date -u +%FT%TZ)"

finish(){
  rc=$?
  echo "GOX_PRE_DOLLAR_EXIT=$rc"
  echo "finished=$(date -u +%FT%TZ)"
}
trap finish EXIT

if [ ! -d "$MAILBOX/.git" ]; then
  echo "BLOCKED steward_mailbox_missing"
  exit 10
fi

echo
echo "=== SYNC LATEST GOX ==="
GIT_TERMINAL_PROMPT=0 git -C "$MAILBOX" fetch origin "$BRANCH" || exit 11
git -C "$MAILBOX" checkout "$BRANCH" || exit 12
if ! git -C "$MAILBOX" rebase "origin/$BRANCH"; then
  git -C "$MAILBOX" rebase --abort || true
  echo "BLOCKED mailbox_rebase_failed"
  exit 13
fi

echo
echo "=== APPROVAL BRIDGE DIRECT TEST ==="
bash "$MAILBOX/approval_bridge/install.sh"
APP_RC=$?
if [ "$APP_RC" -ne 0 ]; then
  echo "BLOCKED approval_bridge_install rc=$APP_RC"
  echo "--- service file ---"
  systemctl cat gox-approval-bridge 2>&1 || true
  echo "--- service status ---"
  systemctl status gox-approval-bridge --no-pager -l 2>&1 || true
  echo "--- service journal ---"
  journalctl -u gox-approval-bridge -n 120 --no-pager 2>&1 || true
  echo "--- python syntax ---"
  python3 -m py_compile "$MAILBOX/approval_bridge/server.py" 2>&1 || true
  echo "--- local files ---"
  ls -la "$MAILBOX/approval_bridge" /opt/gox-approval-bridge /var/lib/gox-approval 2>&1 || true
  exit "$APP_RC"
fi

echo "PASS approval_bridge_direct"

echo
echo "=== FULL PRE-DOLLAR FINISH ==="
bash "$MAILBOX/scripts/pre_first_dollar_finish.sh"
RC=$?
if [ "$RC" -eq 0 ]; then
  echo "GOX_PRE_DOLLAR_RESCUE=PASS"
else
  echo "GOX_PRE_DOLLAR_RESCUE=BLOCKED"
fi
exit "$RC"
EOF
chmod 700 "$RUNNER"

tmux kill-session -t "$SESSION" 2>/dev/null || true
rm -f "$LOG"
tmux new-session -d -s "$SESSION" "bash $RUNNER"

echo "GOX_PRE_DOLLAR_RESCUE_SESSION=STARTED"
echo "SESSION=$SESSION"
echo "LOG=$LOG"
echo "SAFE_TO_LEAVE_BROWSER=yes"
echo "CHECK_LATER=tmux has-session -t $SESSION 2>/dev/null && echo RUNNING || echo STOPPED; tail -n 220 $LOG"
