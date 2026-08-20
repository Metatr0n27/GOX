#!/usr/bin/env bash
set -euo pipefail

MAILBOX="/var/lib/gox-steward/mailbox"
REPO_SSH="git@github.com:Metatr0n27/GOX.git"
SERVICE="gox-remote-steward"

log(){ printf '\n=== %s ===\n' "$1"; }
fail(){ echo "GOX_STEWARD_BLOCKER=$1"; exit 1; }

[ "$(id -u)" -eq 0 ] || fail "repair_requires_root"
[ -d "$MAILBOX/.git" ] || fail "mailbox_missing_reinstall_steward"
command -v ssh >/dev/null 2>&1 || fail "ssh_missing"

log "DISCOVER EXISTING GITHUB SSH AUTH"
mkdir -p /root/.ssh
chmod 700 /root/.ssh
ssh-keyscan -H github.com >> /root/.ssh/known_hosts 2>/dev/null || true
chmod 600 /root/.ssh/known_hosts 2>/dev/null || true

KEY=""
for candidate in \
  /root/.ssh/id_rsa_github_vps \
  /root/.ssh/id_ed25519_github \
  /root/.ssh/id_ed25519 \
  /root/.ssh/id_rsa; do
  [ -f "$candidate" ] || continue
  chmod 600 "$candidate" || true
  set +e
  OUT="$(ssh -T -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10 -i "$candidate" git@github.com 2>&1)"
  CODE=$?
  set -e
  if printf '%s' "$OUT" | grep -qi 'successfully authenticated'; then
    KEY="$candidate"
    echo "usable_key=$(basename "$candidate")"
    break
  fi
done

if [ -z "$KEY" ]; then
  if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    log "USE EXISTING GH AUTH"
    gh auth setup-git
    git -C "$MAILBOX" remote set-url origin "https://github.com/Metatr0n27/GOX.git"
  else
    fail "no_existing_github_ssh_or_gh_auth"
  fi
else
  log "CONFIGURE MAILBOX FOR SSH"
  git -C "$MAILBOX" remote set-url origin "$REPO_SSH"
  git -C "$MAILBOX" config core.sshCommand "ssh -i $KEY -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes"
fi

log "VERIFY WRITE ACCESS"
TEST_BRANCH="gox-steward-auth-test-$(date +%s)"
set +e
git -C "$MAILBOX" push --dry-run origin "HEAD:$TEST_BRANCH" >/tmp/gox-steward-auth-test.log 2>&1
PUSH_CODE=$?
set -e
if [ "$PUSH_CODE" -ne 0 ]; then
  cat /tmp/gox-steward-auth-test.log
  fail "github_write_access_still_missing"
fi
rm -f /tmp/gox-steward-auth-test.log

log "RESTART STEWARD"
systemctl restart "$SERVICE"
sleep 2
systemctl is-active --quiet "$SERVICE" || fail "service_not_active"

log "RESULT"
echo "GOX_REMOTE_STEWARD=CONNECTED"
echo "GITHUB_RETURN_CHANNEL=PASS"
echo "SERVICE_STATUS=ACTIVE"
echo "NEXT=assistant_can_use_github_mailbox"
