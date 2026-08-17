#!/bin/sh
set -eu
LIVE=${GOX_LIVE_DIR:-/opt/gox-live}
install -m 0644 "$LIVE/deploy/gox-revenue-scout.service" /etc/systemd/system/gox-revenue-scout.service
install -m 0644 "$LIVE/deploy/gox-revenue-scout.timer" /etc/systemd/system/gox-revenue-scout.timer
mkdir -p /var/lib/gox/revenue
systemctl daemon-reload
systemctl enable --now gox-revenue-scout.timer
systemctl start gox-revenue-scout.service
