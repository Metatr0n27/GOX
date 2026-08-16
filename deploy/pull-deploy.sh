#!/bin/sh
set -eu

REPO_URL=${GOX_REPO_URL:-https://github.com/Metatr0n27/GOX.git}
RELEASE_BRANCH=${GOX_RELEASE_BRANCH:-release/chat-dev}
ROOT=${GOX_DEPLOY_ROOT:-/opt/gox-deploy}
LIVE=${GOX_LIVE_DIR:-/opt/gox}
STATE=${GOX_DEPLOY_STATE:-/var/lib/gox/deploy}
HEALTH=${GOX_HEALTH_URL:-http://127.0.0.1:8080/health}
mkdir -p "$ROOT" "$STATE"

if [ ! -d "$ROOT/repo/.git" ]; then
  git clone --filter=blob:none --branch "$RELEASE_BRANCH" "$REPO_URL" "$ROOT/repo"
else
  git -C "$ROOT/repo" fetch origin "$RELEASE_BRANCH"
  git -C "$ROOT/repo" checkout -f "$RELEASE_BRANCH"
  git -C "$ROOT/repo" reset --hard "origin/$RELEASE_BRANCH"
fi

NEW_SHA=$(git -C "$ROOT/repo" rev-parse HEAD)
OLD_SHA=$(cat "$STATE/deployed-sha" 2>/dev/null || true)
[ "$NEW_SHA" = "$OLD_SHA" ] && exit 0

STAGE="$ROOT/releases/$NEW_SHA"
mkdir -p "$STAGE"
# Copy only runtime/deployment assets; repository metadata and unrelated files never become live.
cp -R "$ROOT/repo/chat_dev" "$STAGE/chat_dev"
cp -R "$ROOT/repo/deploy" "$STAGE/deploy"

PREV=$(readlink -f "$LIVE" 2>/dev/null || true)
ln -sfn "$STAGE" "$ROOT/live.next"
mv -Tf "$ROOT/live.next" "$LIVE"

systemctl restart gox-chat-dev.service gox-chat-worker.service
if ! curl -fsS --max-time 5 "$HEALTH" >/dev/null; then
  if [ -n "$PREV" ] && [ -d "$PREV" ]; then
    ln -sfn "$PREV" "$ROOT/live.rollback"
    mv -Tf "$ROOT/live.rollback" "$LIVE"
    systemctl restart gox-chat-dev.service gox-chat-worker.service || true
  fi
  logger -t gox-deploy "deployment $NEW_SHA failed health check; rolled back"
  exit 1
fi

printf '%s\n' "$NEW_SHA" > "$STATE/deployed-sha"
printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$NEW_SHA" >> "$STATE/history.log"
logger -t gox-deploy "deployed $NEW_SHA successfully"
