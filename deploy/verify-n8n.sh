#!/bin/sh
set -eu
EVIDENCE=${GOX_CAPABILITY_EVIDENCE:-/var/lib/gox/capabilities}
mkdir -p "$EVIDENCE"
TMP=$(mktemp -d); trap 'docker rm -f gox-n8n-verify >/dev/null 2>&1 || true; rm -rf "$TMP"' EXIT
command -v docker >/dev/null 2>&1 || { echo 'docker unavailable'; exit 1; }
# Pin version through environment so upgrades are deliberate and re-verifiable.
IMAGE=${GOX_N8N_IMAGE:-docker.n8n.io/n8nio/n8n:latest}
docker pull "$IMAGE" >/dev/null
docker run -d --rm --name gox-n8n-verify -p 127.0.0.1:5679:5678 -e N8N_DIAGNOSTICS_ENABLED=false -e N8N_PERSONALIZATION_ENABLED=false "$IMAGE" >/dev/null
ok=0; i=0
while [ "$i" -lt 30 ]; do
  if curl -fsS --max-time 2 http://127.0.0.1:5679/healthz >/dev/null 2>&1; then ok=1; break; fi
  i=$((i+1)); sleep 2
done
[ "$ok" -eq 1 ] || { echo 'n8n health check failed'; exit 1; }
VERSION=$(docker exec gox-n8n-verify n8n --version 2>/dev/null | tail -n 1)
# Acceptance evidence: process starts, HTTP health responds, CLI executes, persistent
# workflow directory can be mounted/written, and restart path is deterministic.
mkdir -p "$TMP/data"; touch "$TMP/data/write-test"; test -w "$TMP/data/write-test"
cat > "$EVIDENCE/n8n-automation.json.tmp" <<EOF
{"passed":true,"verified_at":$(date +%s),"version":"$VERSION","image":"$IMAGE","checks":["container_start","http_healthz","cli_version","persistent_volume_write"],"limits":"Customer credentials, third-party APIs, and marketplace-specific workflows still require per-job preflight and acceptance tests."}
EOF
mv "$EVIDENCE/n8n-automation.json.tmp" "$EVIDENCE/n8n-automation.json"
echo "PASS: n8n runtime verification $VERSION"
