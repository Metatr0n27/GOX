#!/usr/bin/env bash
set -euo pipefail

APP=/opt/gox-approval-bridge
ROOT=/var/lib/gox-approval
SERVICE=/etc/systemd/system/gox-approval-bridge.service
LOCAL_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/server.py"

fail(){ echo "GOX_APPROVAL_BLOCKER=$1"; exit 1; }
[ "$(id -u)" -eq 0 ] || fail root_required
command -v python3 >/dev/null 2>&1 || fail python3_missing
command -v systemctl >/dev/null 2>&1 || fail systemd_missing
[ -f "$LOCAL_SRC" ] || fail local_server_source_missing

mkdir -p "$APP" "$ROOT"
cp "$LOCAL_SRC" "$APP/server.py"
chmod 700 "$APP/server.py"

cat > "$SERVICE" <<'UNIT'
[Unit]
Description=GOX Owner Approval Bridge
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/gox-approval-bridge/server.py
Restart=always
RestartSec=3
Environment=GOX_APPROVAL_BIND=127.0.0.1
Environment=GOX_APPROVAL_PORT=8765
Environment=GOX_APPROVAL_ROOT=/var/lib/gox-approval
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true
ReadWritePaths=/var/lib/gox-approval

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable gox-approval-bridge >/dev/null
systemctl restart gox-approval-bridge
sleep 2
systemctl is-active --quiet gox-approval-bridge || {
  journalctl -u gox-approval-bridge -n 80 --no-pager || true
  fail service_failed
}

curl -fsS http://127.0.0.1:8765/health >/tmp/gox-approval-health.json || {
  journalctl -u gox-approval-bridge -n 80 --no-pager || true
  fail health_check_failed
}

echo "GOX_APPROVAL_BRIDGE=PASS"
echo "HEALTH=$(cat /tmp/gox-approval-health.json)"
echo "OWNER_TOKEN_STORED=$ROOT/owner_token"
echo "OWNER_URL_NOT_PRINTED=yes"
