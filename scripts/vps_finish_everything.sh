#!/usr/bin/env bash
set -euo pipefail

REPO="https://github.com/Metatr0n27/GOX.git"
BRANCH="gox/remote-steward"
MAILBOX="/var/lib/gox-steward/mailbox"
STEWARD_APP="/opt/gox-remote-steward"
APPROVAL_APP="/opt/gox-approval-bridge"
REPORT="/root/gox-bootstrap-report/final-stack-check.txt"

log(){ printf '\n=== %s ===\n' "$1"; }
pass(){ echo "PASS $1"; }
block(){ echo "BLOCKED $1"; }

mkdir -p /root/gox-bootstrap-report
: > "$REPORT"
exec > >(tee -a "$REPORT") 2>&1

log "PRECHECK"
[ "$(id -u)" -eq 0 ] || { block "run_as_root"; exit 1; }
for c in git curl python3 systemctl; do command -v "$c" >/dev/null 2>&1 || { block "$c missing"; exit 1; }; done
pass "base_tools"

log "OWNER GATE: GITHUB AUTH"
if ! command -v gh >/dev/null 2>&1; then
  block "github_cli_missing"
  exit 2
fi
if ! gh auth status >/dev/null 2>&1; then
  echo "One owner approval is required. Complete the GitHub device/browser authorization when shown."
  gh auth login --hostname github.com --git-protocol https --web
fi
gh auth status >/dev/null 2>&1 || { block "github_auth_not_persisted"; exit 3; }

# Normalize all old/broken credential helper entries before asking gh to configure Git.
git config --global --unset-all credential.helper 2>/dev/null || true
git config --system --unset-all credential.helper 2>/dev/null || true
gh auth setup-git >/dev/null 2>&1 || true
git config --global --unset-all credential.helper 2>/dev/null || true
git config --global --add credential.helper "!gh auth git-credential"
pass "github_auth"

log "NONINTERACTIVE GITHUB READ"
GIT_TERMINAL_PROMPT=0 git ls-remote "$REPO" HEAD >/dev/null
pass "github_read"

log "SYNC STEWARD MAILBOX"
if [ ! -d "$MAILBOX/.git" ]; then
  rm -rf "$MAILBOX"
  GIT_TERMINAL_PROMPT=0 git clone --branch "$BRANCH" --single-branch "$REPO" "$MAILBOX"
else
  git -C "$MAILBOX" remote set-url origin "$REPO"
  GIT_TERMINAL_PROMPT=0 git -C "$MAILBOX" fetch origin "$BRANCH"
  git -C "$MAILBOX" checkout "$BRANCH"
  git -C "$MAILBOX" reset --hard "origin/$BRANCH"
fi
pass "mailbox_sync"

log "NONINTERACTIVE GITHUB WRITE"
TEST_BRANCH="gox-steward-auth-test-$(date +%s)"
GIT_TERMINAL_PROMPT=0 git -C "$MAILBOX" push --dry-run origin "HEAD:$TEST_BRANCH" >/dev/null
pass "github_write_dry_run"

log "INSTALL STEWARD"
mkdir -p "$STEWARD_APP"
cp "$MAILBOX/remote_steward/steward.py" "$STEWARD_APP/steward.py"
chmod 700 "$STEWARD_APP/steward.py"
cat > /etc/systemd/system/gox-remote-steward.service <<'UNIT'
[Unit]
Description=GOX Remote Steward
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/gox-remote-steward/steward.py
Restart=always
RestartSec=5
Environment=GOX_STEWARD_BRANCH=gox/remote-steward
Environment=GOX_STEWARD_POLL_SECONDS=30
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=read-only
ReadWritePaths=/var/lib/gox-steward /root/GOX-bridge /root/gox-bootstrap-report /tmp

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --now gox-remote-steward >/dev/null
sleep 2
systemctl is-active --quiet gox-remote-steward
pass "steward_service"

log "INSTALL APPROVAL BRIDGE"
mkdir -p "$APPROVAL_APP"
cp "$MAILBOX/approval_bridge/server.py" "$APPROVAL_APP/server.py"
cp "$MAILBOX/approval_bridge/owner_wake_companion.html" "$APPROVAL_APP/owner_wake_companion.html" 2>/dev/null || true
chmod 700 "$APPROVAL_APP/server.py"
if [ -f "$MAILBOX/approval_bridge/install.sh" ]; then
  bash "$MAILBOX/approval_bridge/install.sh" || true
fi
if systemctl list-unit-files | grep -q '^gox-approval'; then
  systemctl restart gox-approval-bridge 2>/dev/null || systemctl restart gox-approval 2>/dev/null || true
fi
pass "approval_bridge_files"

log "CORE PYTHON SANITY"
python3 -m py_compile "$MAILBOX/core/tedium_absorber.py"
python3 "$MAILBOX/core/tedium_absorber.py" >/tmp/gox-core-state.json
pass "tedium_absorber"

log "SECRET LEAK CHECK"
if [ -f "$MAILBOX/quality/secret_scan.py" ]; then
  python3 "$MAILBOX/quality/secret_scan.py" "$MAILBOX"
  pass "secret_scan"
elif [ -f "$MAILBOX/security/secret_scan.py" ]; then
  python3 "$MAILBOX/security/secret_scan.py" "$MAILBOX"
  pass "secret_scan"
else
  echo "NOTE secret scanner script not found; manual repo patterns check only"
  if grep -RInE '(BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})' "$MAILBOX" --exclude-dir=.git >/tmp/gox-secret-hits.txt; then
    cat /tmp/gox-secret-hits.txt
    block "possible_secret_material_in_repo"
    exit 4
  fi
  pass "basic_secret_scan"
fi

log "DISCOVER AND RUN TESTS"
TEST_FAIL=0
while IFS= read -r f; do
  echo "RUN $f"
  if ! python3 "$f"; then TEST_FAIL=1; fi
done < <(find "$MAILBOX" -type f \( -name 'test_*.py' -o -name '*_test.py' \) -not -path '*/.git/*' | sort)
if [ "$TEST_FAIL" -eq 0 ]; then pass "python_tests"; else block "python_tests"; fi

log "EXECUTION BRIDGE"
if [ -d /root/GOX-bridge ]; then
  if PYTHONPATH=/root/GOX-bridge python3 -m unittest execution_bridge.test_bridge -v; then pass "execution_bridge_tests"; else block "execution_bridge_tests"; fi
else
  block "GOX-bridge_missing"
fi

log "CHATDEV SMOKE"
if [ -d "$MAILBOX/chatdev" ]; then
  find "$MAILBOX/chatdev" -maxdepth 2 -type f -print | sort | head -n 40
  pass "chatdev_files_present"
else
  block "chatdev_missing"
fi

log "QUEUE FRESH STEWARD PROOF"
NOW="$(date -u +%Y%m%d-%H%M%S)"
CMD="$MAILBOX/remote_steward/commands/${NOW}-system-status.json"
printf '{"id":"%s-system-status","action":"system_status"}\n' "$NOW" > "$CMD"
git -C "$MAILBOX" add "remote_steward/commands/$(basename "$CMD")"
git -C "$MAILBOX" commit -m "queue final stack steward proof $NOW" >/dev/null
GIT_TERMINAL_PROMPT=0 git -C "$MAILBOX" push origin "$BRANCH" >/dev/null
pass "steward_proof_queued"

log "WAIT FOR RESULT RETURN"
RESULT="$MAILBOX/remote_steward/results/${NOW}-system-status.json"
for _ in $(seq 1 18); do
  sleep 5
  GIT_TERMINAL_PROMPT=0 git -C "$MAILBOX" fetch origin "$BRANCH" >/dev/null 2>&1 || true
  git -C "$MAILBOX" reset --hard "origin/$BRANCH" >/dev/null 2>&1 || true
  [ -f "$RESULT" ] && break
done
if [ -f "$RESULT" ]; then
  cat "$RESULT"
  pass "steward_return_channel"
else
  block "steward_return_channel_no_result_within_90s"
fi

log "FINAL SUMMARY"
echo "REPORT=$REPORT"
echo "REBOOT_DEFERRED=yes"
echo "GOX_VPS_STACK_CHECK=COMPLETE"
echo "If any line above says BLOCKED, GOX should continue repairing that item before declaring completion."
