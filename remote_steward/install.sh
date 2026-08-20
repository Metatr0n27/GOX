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

log "BACKUP"
mkdir -p /root/gox-steward-backups
if [ -d "$APP" ] || [ -d "$ROOT" ]; then
  tar -czf "/root/gox-steward-backups/steward-$(date +%Y%m%d-%H%M%S).tar.gz" "$APP" "$ROOT" 2>/dev/null || true
fi

log "INSTALL CODE"
mkdir -p "$APP" "$ROOT"
curl -fsSL "https://raw.githubusercontent.com/Metatr0n27/GOX/$BRANCH/remote_steward/steward.py" -o "$APP/steward.py"
chmod 700 "$APP/steward.py"

log "SETUP MAILBOX"
if [ ! -d "$MAILBOX/.git" ]; then
  rm -rf "$MAILBOX"
  git clone --branch "$BRANCH" --single-branch "$REPO_URL" "$MAILBOX"
else
  git -C "$MAILBOX" fetch origin "$BRANCH"
  git -C "$MAILBOX" checkout "$BRANCH"
  git -C "$MAILBOX" reset --hard "origin/$BRANCH"
fi
mkdir -p "$MAILBOX/remote_steward/commands" "$MAILBOX/remote_steward/results"

log "VERIFY PUSH CAPABILITY"
TEST_BRANCH="gox-steward-push-test-$(date +%s)"
set +e
git -C "$MAILBOX" push --dry-run origin "HEAD:$TEST_BRANCH" >/tmp/gox-steward-push-test.log 2>&1
PUSH_CODE=$?
set -e
if [ "$PUSH_CODE" -ne 0 ]; then
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
ExecStart=/usr/bin/python3 /opt/gox-remote-steward/steward.py
Restart=always
RestartSec=5
Environment=GOX_STEWARD_BRANCH=gox/remote-steward
Environment=GOX_STEWARD_POLL_SECONDS=30
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=read-only
ReadWritePaths=/var/lib/gox-steward /root/GOX-bridge /root/gox-bootstrap-report /tmp

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable --now gox-remote-steward
sleep 2
systemctl --no-pager --full status gox-remote-steward | head -n 30 || true

log "RESULT"
echo "GOX_REMOTE_STEWARD=INSTALLED"
echo "MAILBOX_BRANCH=$BRANCH"
echo "POLL_SECONDS=30"
echo "COMMANDS=remote_steward/commands/*.json"
echo "RESULTS=remote_steward/results/*.json"
echo "SERVICE=gox-remote-steward"
