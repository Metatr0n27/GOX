#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/Metatr0n27/GOX.git"
BRANCH="gox/remote-steward"
ROOT="/var/lib/gox-steward"
MAILBOX="$ROOT/mailbox"
APP="/opt/gox-remote-steward"
SERVICE="/etc/systemd/system/gox-remote-steward.service"

log(){ printf '\n=== %s ===\n' "$1"; }
fail(){ echo "GOX_STEWARD_BLOCKER=$1"; exit 1; }

[ "$(id -u)" -eq 0 ] || fail "installer_requires_root"
command -v git >/dev/null 2>&1 || fail "git_missing"
command -v python3 >/dev/null 2>&1 || fail "python3_missing"
command -v systemctl >/dev/null 2>&1 || fail "systemd_missing"
command -v gh >/dev/null 2>&1 || fail "github_cli_missing"

gh auth status >/dev/null 2>&1 || fail "github_auth_missing"

log "NORMALIZE GIT AUTH"
git config --global --unset-all credential.helper 2>/dev/null || true
gh auth setup-git >/dev/null 2>&1 || true
git config --global --unset-all credential.helper 2>/dev/null || true
git config --global --add credential.helper "!gh auth git-credential"

log "STOP OLD STEWARD"
systemctl stop gox-remote-steward 2>/dev/null || true

log "BACKUP"
mkdir -p /root/gox-steward-backups
if [ -d "$APP" ] || [ -d "$ROOT" ]; then
  tar -czf "/root/gox-steward-backups/steward-$(date +%Y%m%d-%H%M%S).tar.gz" "$APP" "$ROOT" 2>/dev/null || true
fi

log "SETUP MAILBOX"
if [ ! -d "$MAILBOX/.git" ]; then
  rm -rf "$MAILBOX"
  GIT_TERMINAL_PROMPT=0 git clone --branch "$BRANCH" --single-branch "$REPO_URL" "$MAILBOX"
else
  git -C "$MAILBOX" remote set-url origin "$REPO_URL"
  GIT_TERMINAL_PROMPT=0 git -C "$MAILBOX" fetch origin "$BRANCH"
  git -C "$MAILBOX" checkout "$BRANCH"
  if ! git -C "$MAILBOX" rebase "origin/$BRANCH"; then
    git -C "$MAILBOX" rebase --abort || true
    fail "mailbox_rebase_failed"
  fi
fi
mkdir -p "$MAILBOX/remote_steward/commands" "$MAILBOX/remote_steward/results"

log "INSTALL CODE"
mkdir -p "$APP" "$ROOT"
cp "$MAILBOX/remote_steward/steward.py" "$APP/steward.py"
chmod 700 "$APP/steward.py"

log "VERIFY PUSH CAPABILITY"
TEST_BRANCH="gox-steward-push-test-$(date +%s)"
if ! HOME=/root XDG_CONFIG_HOME=/root/.config GIT_TERMINAL_PROMPT=0 git -C "$MAILBOX" push --dry-run origin "HEAD:$TEST_BRANCH" >/tmp/gox-steward-push-test.log 2>&1; then
  cat /tmp/gox-steward-push-test.log
  fail "github_push_auth_missing"
fi
rm -f /tmp/gox-steward-push-test.log

log "INSTALL SERVICE"
cat > "$SERVICE" <<'UNIT'
[Unit]
Description=GOX Remote Steward
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
Environment=HOME=/root
Environment=XDG_CONFIG_HOME=/root/.config
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/root/.local/bin:/root/.hermes/node/bin
Environment=GIT_TERMINAL_PROMPT=0
Environment=GOX_STEWARD_BRANCH=gox/remote-steward
Environment=GOX_STEWARD_POLL_SECONDS=30
ExecStart=/usr/bin/python3 /opt/gox-remote-steward/steward.py
Restart=always
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=read-only
ReadWritePaths=/var/lib/gox-steward /root/GOX-bridge /root/gox-bootstrap-report /tmp

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable gox-remote-steward >/dev/null

log "QUEUE SELF TEST BEFORE START"
STAMP="$(date -u +%Y%m%d-%H%M%S)"
CMD_REL="remote_steward/commands/${STAMP}-steward-self-test.json"
CMD="$MAILBOX/$CMD_REL"
printf '{"id":"%s-steward-self-test","action":"steward_self_test"}\n' "$STAMP" > "$CMD"
git -C "$MAILBOX" add "$CMD_REL"
git -C "$MAILBOX" commit -m "queue steward self test $STAMP" >/dev/null
GIT_TERMINAL_PROMPT=0 git -C "$MAILBOX" push origin "HEAD:$BRANCH" >/dev/null

log "START STEWARD"
systemctl restart gox-remote-steward
sleep 3
systemctl is-active --quiet gox-remote-steward || fail "service_not_active"

log "WAIT FOR AUTOMATIC RESULT"
RESULT="$MAILBOX/remote_steward/results/${STAMP}-steward-self-test.json"
for _ in $(seq 1 24); do
  [ -f "$RESULT" ] && break
  sleep 5
done

if [ ! -f "$RESULT" ]; then
  echo "--- steward log ---"
  tail -n 120 "$ROOT/steward.log" 2>/dev/null || true
  echo "--- steward last error ---"
  cat "$ROOT/last_error.txt" 2>/dev/null || true
  fail "automatic_return_not_proven"
fi
cat "$RESULT"

log "RESULT"
echo "GOX_REMOTE_STEWARD=PASS"
echo "MAILBOX_BRANCH=$BRANCH"
echo "POLL_SECONDS=30"
echo "AUTOMATIC_RETURN=PASS"
echo "SERVICE=gox-remote-steward"
