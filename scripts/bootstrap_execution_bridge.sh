#!/usr/bin/env bash
set -euo pipefail

BRANCH="gox/execution-bridge-v1"
REPO_URL="https://github.com/Metatr0n27/GOX.git"
TARGET="${GOX_DIR:-$HOME/GOX}"
REPORT_DIR="$HOME/gox-bootstrap-report"
mkdir -p "$REPORT_DIR"
REPORT="$REPORT_DIR/report-$(date +%Y%m%d-%H%M%S).txt"

exec > >(tee "$REPORT") 2>&1

echo "GOX EXECUTION BRIDGE BOOTSTRAP"
echo "timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "user=$(id -un 2>/dev/null || true)"
echo "uid=$(id -u 2>/dev/null || true)"
echo "home=$HOME"

echo
echo(){ builtin echo "$@"; }

echo "== OS =="
if [ -f /etc/os-release ]; then
  cat /etc/os-release
else
  uname -a
fi

echo
echo "== Core tools =="
for x in git python3 node npm; do
  if command -v "$x" >/dev/null 2>&1; then
    echo "$x=$(command -v "$x")"
    "$x" --version 2>/dev/null | head -n 1 || true
  else
    echo "$x=MISSING"
  fi
done

echo
echo "== Agent runtimes =="
for x in herdr codex claude gemini opencode; do
  if command -v "$x" >/dev/null 2>&1; then
    echo "$x=$(command -v "$x")"
    "$x" --version 2>/dev/null | head -n 2 || true
  else
    echo "$x=MISSING"
  fi
done

echo
echo "== Repository =="
if [ -d "$TARGET/.git" ]; then
  echo "Using existing repo: $TARGET"
  cd "$TARGET"
  if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: existing GOX repo has uncommitted changes. No checkout/reset performed."
    echo "Please preserve or commit those changes before rerunning."
    exit 21
  fi
  git remote -v || true
  git fetch origin "$BRANCH"
  if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    git checkout "$BRANCH"
    git merge --ff-only "origin/$BRANCH"
  else
    git checkout -b "$BRANCH" "origin/$BRANCH"
  fi
else
  if [ -e "$TARGET" ]; then
    echo "ERROR: $TARGET exists but is not a git repository. No destructive action taken."
    exit 20
  fi
  git clone --branch "$BRANCH" --single-branch "$REPO_URL" "$TARGET"
  cd "$TARGET"
fi

echo "repo=$TARGET"
echo "commit=$(git rev-parse HEAD)"

echo
echo "== Python tests =="
python3 -m unittest discover -s execution_bridge/tests -v

echo
echo "== Dry-run compile test =="
python3 execution_bridge/bridge.py execution_bridge/examples/first_dollar_job.json \
  --config execution_bridge/config.json \
  --dry-run

echo
echo "== Runtime probe =="
set +e
python3 execution_bridge/bridge.py execution_bridge/examples/first_dollar_job.json \
  --config execution_bridge/config.json \
  --probe
PROBE_CODE=$?
set -e

echo "runtime_probe_exit=$PROBE_CODE"

echo
echo "== Safety status =="
if [ "$(id -u)" = "0" ]; then
  echo "WARNING: currently running as root. Do not launch paid-job autonomous agents as root."
  echo "NEXT: create/use a dedicated non-root gox service account before production execution."
else
  echo "non_root_execution=yes"
fi

echo
echo "== Result =="
if [ "$PROBE_CODE" -eq 0 ]; then
  echo "BRIDGE_CODE=PASS"
  echo "RUNTIME_CONFIG=AVAILABLE"
  echo "NEXT=verify exact configured runtime invocation with a disposable 3-agent ensemble"
else
  echo "BRIDGE_CODE=PASS"
  echo "RUNTIME_CONFIG=BLOCKED"
  echo "NEXT=choose one detected runtime and set its exact executable/args in execution_bridge/config.json"
fi

echo "report=$REPORT"
