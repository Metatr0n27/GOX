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
BLOCKING_ACTIONS=(steward_self_test approval_health chief_of_staff_snapshot chatdev_smoke core_state_tests secret_guard bridge_tests runtime_status)
INFORMATIONAL_ACTIONS=(gap_scan)
ACTIONS=("${BLOCKING_ACTIONS[@]}" "${INFORMATIONAL_ACTIONS[@]}")

for ACTION in "${ACTIONS[@]}"; do
  ID="${STAMP}-${ACTION}"
  printf '{"id":"%s","action":"%s"}\n' "$ID" "$ACTION" > "$MAILBOX/remote_steward/commands/${ID}.json"
done
git -C "$MAILBOX" add remote_steward/commands
git -C "$MAILBOX" commit -m "queue pre-dollar readiness proofs $STAMP" >/dev/null

# The steward may push a result between our fetch and push. Rebase and retry instead of failing.
PUSHED=0
for ATTEMPT in 1 2 3 4 5; do
  if GIT_TERMINAL_PROMPT=0 git -C "$MAILBOX" push origin "HEAD:$BRANCH" >/tmp/gox-pre-dollar-push.log 2>&1; then
    PUSHED=1
    break
  fi
  GIT_TERMINAL_PROMPT=0 git -C "$MAILBOX" fetch origin "$BRANCH" >/dev/null 2>&1 || true
  if ! git -C "$MAILBOX" rebase "origin/$BRANCH" >/tmp/gox-pre-dollar-rebase.log 2>&1; then
    git -C "$MAILBOX" rebase --abort || true
    cat /tmp/gox-pre-dollar-rebase.log || true
    fail proof_queue_rebase_failed
  fi
  sleep 2
done
if [ "$PUSHED" -ne 1 ]; then
  cat /tmp/gox-pre-dollar-push.log || true
  fail proof_queue_push_race
fi

echo "PASS proof_queue_push"

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

is_blocking_action(){
  local target="$1"
  local item
  for item in "${BLOCKING_ACTIONS[@]}"; do
    [ "$item" = "$target" ] && return 0
  done
  return 1
}

FAILS=0
for ACTION in "${ACTIONS[@]}"; do
  FILE="$MAILBOX/remote_steward/results/${STAMP}-${ACTION}.json"
  if [ ! -f "$FILE" ]; then
    if is_blocking_action "$ACTION"; then
      echo "BLOCKED $ACTION no_result"
      FAILS=$((FAILS+1))
    else
      echo "INFO $ACTION no_result"
    fi
    continue
  fi

  STATUS="$(python3 - "$FILE" <<'PY'
import json,sys
p=json.load(open(sys.argv[1]))
print(p.get('status','unknown'))
PY
)"

  if [ "$STATUS" = complete ]; then
    if is_blocking_action "$ACTION"; then
      echo "PASS $ACTION"
    else
      echo "INFO $ACTION status=complete"
    fi
    continue
  fi

  if is_blocking_action "$ACTION"; then
    echo "BLOCKED $ACTION status=$STATUS"
    FAILS=$((FAILS+1))
  else
    echo "INFO $ACTION status=$STATUS global_completion_not_required_for_pre_dollar"
  fi

  python3 - "$FILE" <<'PY'
import json,sys
p=json.load(open(sys.argv[1]))
for r in p.get('runs',[]):
    if r.get('exit_code'):
        print((r.get('output') or '')[-2000:])
if p.get('error'):
    print(p['error'])
PY
done

log "PRE-FIRST-DOLLAR VERDICT"
if [ "$FAILS" -eq 0 ]; then
  echo "GOX_PRE_DOLLAR_TECH_READY=PASS"
  echo "GLOBAL_GAP_SCAN=INFORMATIONAL"
  echo "NEXT=QUALIFY_REAL_PAID_WORK"
  exit 0
fi

echo "GOX_PRE_DOLLAR_TECH_READY=BLOCKED"
echo "BLOCKED_COUNT=$FAILS"
exit 2
