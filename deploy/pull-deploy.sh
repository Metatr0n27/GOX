#!/bin/sh
set -eu
REPO_URL=${GOX_REPO_URL:-https://github.com/Metatr0n27/GOX.git}; RELEASE_BRANCH=${GOX_RELEASE_BRANCH:-release/chat-dev}; ROOT=${GOX_DEPLOY_ROOT:-/opt/gox-deploy}; LIVE=${GOX_LIVE_DIR:-/opt/gox-live}; STATE=${GOX_DEPLOY_STATE:-/var/lib/gox/deploy}; HEALTH=${GOX_HEALTH_URL:-http://127.0.0.1:8081/health}
mkdir -p "$ROOT/releases" "$STATE"
if [ ! -d "$ROOT/repo/.git" ]; then git clone --filter=blob:none --branch "$RELEASE_BRANCH" "$REPO_URL" "$ROOT/repo"; else git -C "$ROOT/repo" fetch origin "$RELEASE_BRANCH"; git -C "$ROOT/repo" checkout -f "$RELEASE_BRANCH"; git -C "$ROOT/repo" reset --hard "origin/$RELEASE_BRANCH"; fi
NEW_SHA=$(git -C "$ROOT/repo" rev-parse HEAD); OLD_SHA=$(cat "$STATE/deployed-sha" 2>/dev/null || true); [ "$NEW_SHA" = "$OLD_SHA" ] && exit 0
STAGE="$ROOT/releases/$NEW_SHA"; rm -rf "$STAGE"; mkdir -p "$STAGE"; cp -a "$ROOT/repo/chat_dev" "$STAGE/chat_dev"; cp -a "$ROOT/repo/deploy" "$STAGE/deploy"; [ ! -d "$ROOT/repo/revenue_engine" ] || cp -a "$ROOT/repo/revenue_engine" "$STAGE/revenue_engine"
PREV=""; if [ -L "$LIVE" ]; then PREV=$(readlink -f "$LIVE" 2>/dev/null || true); elif [ -d "$LIVE" ]; then PREV="$ROOT/releases/manual-before-$NEW_SHA"; [ -e "$PREV" ] || cp -a "$LIVE" "$PREV"; rm -rf "$LIVE"; fi
ln -s "$STAGE" "$ROOT/live.next"; mv -T "$ROOT/live.next" "$LIVE"; systemctl restart gox-chat-dev.service gox-chat-worker.service
healthy=0; attempt=1; while [ "$attempt" -le 15 ]; do if curl -fsS --max-time 3 "$HEALTH" >/dev/null 2>&1; then healthy=1; break; fi; sleep 1; attempt=$((attempt + 1)); done
if [ "$healthy" -ne 1 ]; then if [ -n "$PREV" ] && [ -d "$PREV" ]; then rm -f "$LIVE"; ln -s "$PREV" "$LIVE"; systemctl restart gox-chat-dev.service gox-chat-worker.service || true; fi; logger -t gox-deploy "deployment $NEW_SHA failed health check after retries; rolled back"; exit 1; fi
# Optional post-health bootstrap. Failure is logged but does not take ChatDev down.
if [ -x "$LIVE/deploy/install-revenue-scout.sh" ]; then "$LIVE/deploy/install-revenue-scout.sh" || logger -t gox-deploy "revenue scout bootstrap failed for $NEW_SHA"; fi
printf '%s\n' "$NEW_SHA" > "$STATE/deployed-sha"; printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$NEW_SHA" >> "$STATE/history.log"; logger -t gox-deploy "deployed $NEW_SHA successfully after health check attempt $attempt"
