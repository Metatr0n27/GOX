#!/usr/bin/env bash
set -euo pipefail

APP=/opt/gox-approval-bridge
ROOT=/var/lib/gox-approval
SERVICE=/etc/systemd/system/gox-approval-bridge.service
BRANCH=gox/remote-steward
SRC=https://raw.githubusercontent.com/Metatr0n27/GOX/$BRANCH/approval_bridge/server.py

fail(){ echo "GOX_APPROVAL_BLOCKER=$1"; exit 1; }
[ "$(id -u)" -eq 0 ] || fail root_required
command -v python3 >/dev/null 2>&1 || fail python3_missing
command -v systemctl >/dev/null 2>&1 || fail systemd_missing
mkdir -p "$APP" "$ROOT"
curl -fsSL "$SRC" -o "$APP/server.py"
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
systemctl enable --now gox-approval-bridge
sleep 1
systemctl is-active --quiet gox-approval-bridge || fail service_failed
TOKEN=$(cat "$ROOT/owner_token")
echo "GOX_APPROVAL_BRIDGE=INSTALLED"
echo "LOCAL_URL=http://127.0.0.1:8765/?token=$TOKEN"
echo "NOTE=Keep this owner URL private. Pair it through the future Chrome/mobile companion; do not paste the token into chats or logs."
