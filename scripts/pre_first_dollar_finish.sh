#!/usr/bin/env bash
set -euo pipefail

MAILBOX=/var/lib/gox-steward/mailbox
BRANCH=gox/remote-steward
STEWARD=/opt/gox-remote-steward/steward.py

log(){ printf '\n=== %s ===\n' "$1"; }
fail(){ echo "GOX_PRE_DOLLAR_BLOCKER=$1"; exit 1; }

[ "$(id -u)" -eq 0 ] || fail root_required
[ -d "$MAILBOX/.git" ] || fail steward_mailbox_missing
command -v gh >/dev/null 2>&1 || fail github_cli_missing
gh auth status >/dev/null 2>&1 || fail github_auth_missing

log "SYNC LATEST GOX"
GIT_TERMINAL_PROMPT=0 git -C "$MAILBOX" fetch origin "$BRANCH"
git -C "$MAILBOX" checkout "$BRANCH"
if ! git -C "$MAILBOX" rebase "origin/$BRANCH"; then
  git -C "$MAILBOX" rebase --abort || true
  fail mailbox_rebase_failed
fi

log "INSTALL APPROVAL BRIDGE"
bash "$MAILBOX/approval_bridge/install.sh" >/tmp/gox-approval-install.log
systemctl is-active --quiet gox-approval-bridge || { cat /tmp/gox-approval-install.log; fail approval_bridge_not_active; }
curl -fsS http://127.0.0.1:8765/health >/tmp/gox-approval-health.json || fail approval_health_failed
echo "PASS approval_bridge"

log "INSTALL LATEST STEWARD"
mkdir -p /opt/gox-remote-steward
cp "$MAILBOX/remote_steward/steward.py" "$STEWARD"
chmod 700 "$STEWARD"
systemctl restart gox-remote-steward
sleep 3
systemctl is-active --quiet gox-remote-steward || fail steward_not_active
echo "PASS steward_service"

log "QUEUE LIVE PROOFS"
STAMP="$(date -u +%Y%m%d-%H%M%S)"
ACTIONS=(steward_self_test approval_health chief_of_staff_snapshot chatdev_smoke core_state_tests secret_guard bridge_tests runtime_status gap_scan)
for ACTION in "${ACTIONS[@]}"; do
  ID="${STAMP}-${ACTION}"
  printf '{"id":"%s","action":"%s"}\n' "$ID" "$ACTION" > "$MAILBOX/remote_steward/commands/${ID}.json"
done
git -C "$MAILBOX" add remote_steward/commands
git -C "$MAILBOX" commit -m "queue pre-dollar readiness proofs $STAMP" >/dev/null
GIT_TERMINAL_PROMPT=0 git -C "$MAILBOX" push origin "HEAD:$BRANCH" >/dev/null

log "WAIT FOR AUTOMATIC RESULTS"
DEADLINE=$((SECONDS+240))
while [ "$SECONDS" -lt "$DEADLINE" ]; do
  sleep 5
  GIT_TERMINAL_PROMPT=0 git -C "$MAILBOX" fetch origin "$BRANCH" >/dev/null 2>&1 || true
  git -C "$MAILBOX" rebase "origin/$BRANCH" >/dev/null 2>&1 || true
  MISSING=0
  for ACTION in "${ACTIONS[@]}"; do
    [ -f "$MAILBOX/remote_steward/results/${STAMP}-${ACTION}.json" ] || MISSING=$((MISSING+1))
  done
  [ "$MISSING" -eq 0 ] && break
done

FAILS=0
for ACTION in "${ACTIONS[@]}"; do
  FILE="$MAILBOX/remote_steward/results/${STAMP}-${ACTION}.json"
  if [ ! -f "$FILE" ]; then
    echo "BLOCKED $ACTION no_result"
    FAILS=$((FAILS+1))
    continue
  fi
  STATUS="$(python3 - "$FILE" <<'PY'
import json,sys
p=json.load(open(sys.argv[1]))
print(p.get('status','unknown'))
PY
)"
  if [ "$STATUS" = complete ]; then
    echo "PASS $ACTION"
  else
    echo "BLOCKED $ACTION status=$STATUS"
    FAILS=$((FAILS+1))
    python3 - "$FILE" <<'PY'
import json,sys
p=json.load(open(sys.argv[1]))
for r in p.get('runs',[]):
    if r.get('exit_code'):
        print((r.get('output') or '')[-2000:])
if p.get('error'):
    print(p['error'])
PY
  fi
done

log "PRE-FIRST-DOLLAR VERDICT"
if [ "$FAILS" -eq 0 ]; then
  echo "GOX_PRE_DOLLAR_TECH_READY=PASS"
  echo "NEXT=QUALIFY_REAL_PAID_WORK"
  exit 0
fi

echo "GOX_PRE_DOLLAR_TECH_READY=BLOCKED"
echo "BLOCKED_COUNT=$FAILS"
exit 2
