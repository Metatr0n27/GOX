#!/usr/bin/env bash
set -euo pipefail

REPO="https://github.com/Metatr0n27/GOX.git"
BRANCH="gox/remote-steward"
MAILBOX="/var/lib/gox-steward/mailbox"
SERVICE="gox-remote-steward"

log(){ printf '\n=== %s ===\n' "$1"; }
fail(){ echo "GOX_OWNER_GATE_REPAIR=BLOCKED:$1"; exit 1; }

[ "$(id -u)" -eq 0 ] || fail "run_as_root"
command -v gh >/dev/null 2>&1 || fail "github_cli_missing"
command -v git >/dev/null 2>&1 || fail "git_missing"
command -v systemctl >/dev/null 2>&1 || fail "systemd_missing"

log "OWNER GATE: GITHUB AUTH"
if ! gh auth status >/dev/null 2>&1; then
  echo "GitHub approval is required once."
  echo "A device code/browser approval may appear next."
  gh auth login --hostname github.com --git-protocol https --web
fi

gh auth status >/dev/null 2>&1 || fail "github_auth_not_persisted"

log "CONFIGURE GIT TO USE GH AUTH"
gh auth setup-git

git config --global credential.helper ""
git config --global --add credential.helper "!gh auth git-credential"

log "VERIFY NONINTERACTIVE READ"
GIT_TERMINAL_PROMPT=0 git ls-remote "$REPO" HEAD >/dev/null || fail "github_read_failed"

log "SYNC MAILBOX"
if [ ! -d "$MAILBOX/.git" ]; then
  rm -rf "$MAILBOX"
  GIT_TERMINAL_PROMPT=0 git clone --branch "$BRANCH" --single-branch "$REPO" "$MAILBOX"
else
  git -C "$MAILBOX" remote set-url origin "$REPO"
  GIT_TERMINAL_PROMPT=0 git -C "$MAILBOX" fetch origin "$BRANCH"
  git -C "$MAILBOX" checkout "$BRANCH"
  git -C "$MAILBOX" reset --hard "origin/$BRANCH"
fi

log "VERIFY NONINTERACTIVE WRITE"
TEST_BRANCH="gox-steward-auth-test-$(date +%s)"
GIT_TERMINAL_PROMPT=0 git -C "$MAILBOX" push --dry-run origin "HEAD:$TEST_BRANCH" || fail "github_write_failed"

log "INSTALL LATEST STEWARD CODE"
mkdir -p /opt/gox-remote-steward
curl -fsSL "https://raw.githubusercontent.com/Metatr0n27/GOX/$BRANCH/remote_steward/steward.py" -o /opt/gox-remote-steward/steward.py
chmod 700 /opt/gox-remote-steward/steward.py

log "RESTART STEWARD"
systemctl daemon-reload
systemctl restart "$SERVICE"
sleep 3
systemctl is-active --quiet "$SERVICE" || fail "service_not_active"

log "FINAL HEALTH"
echo "GH_AUTH=PASS"
echo "GIT_READ=PASS"
echo "GIT_WRITE_DRY_RUN=PASS"
echo "STEWARD_SERVICE=ACTIVE"
echo "GOX_OWNER_GATE_REPAIR=PASS"
