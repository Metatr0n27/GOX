#!/bin/sh
set -eu
LIVE=${GOX_LIVE_DIR:-/opt/gox-live}
install -m 0644 "$LIVE/deploy/gox-operator-bridge.service" /etc/systemd/system/gox-operator-bridge.service
install -m 0644 "$LIVE/deploy/gox-operator-bridge.timer" /etc/systemd/system/gox-operator-bridge.timer
mkdir -p /var/lib/gox/operator/receipts
systemctl daemon-reload
systemctl enable --now gox-operator-bridge.timer
systemctl start gox-operator-bridge.service
