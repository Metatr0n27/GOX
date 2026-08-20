#!/usr/bin/env bash
set -euo pipefail

BRANCH="gox/execution-bridge-v1"
DIR="/root/GOX-bridge"
REPO="https://github.com/Metatr0n27/GOX.git"
REPORT_DIR="/root/gox-bootstrap-report"
mkdir -p "$REPORT_DIR"
REPORT="$REPORT_DIR/finish-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee "$REPORT") 2>&1

say(){ printf '\n=== %s ===\n' "$1"; }
fail(){ echo "GOX_BLOCKER=$1"; echo "report=$REPORT"; exit "${2:-1}"; }

say "GOX ONE-SHOT EXECUTION BRIDGE FINISHER"
echo "timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

say "OS + RUNTIME"
[ -f /etc/os-release ] && cat /etc/os-release || true
for x in git python3 herdr claude; do
  if command -v "$x" >/dev/null 2>&1; then
    echo "$x=$(command -v "$x")"
    "$x" --version 2>/dev/null | head -n 2 || true
  else
    echo "$x=MISSING"
  fi
done
command -v git >/dev/null 2>&1 || fail "git_missing"
command -v python3 >/dev/null 2>&1 || fail "python3_missing"
command -v claude >/dev/null 2>&1 || fail "claude_missing"

say "SYNC CLEAN BRIDGE CLONE"
if [ ! -d "$DIR/.git" ]; then
  rm -rf "$DIR"
  git clone --branch "$BRANCH" --single-branch "$REPO" "$DIR"
fi
cd "$DIR"
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git reset --hard "origin/$BRANCH"
echo "commit=$(git rev-parse HEAD)"

say "PYTHON TESTS"
PYTHONPATH="$DIR" python3 -m unittest execution_bridge.test_bridge -v

say "CLAUDE NONINTERACTIVE SMOKE"
set +e
SMOKE="$(printf 'Reply with exactly GOX_RUNTIME_OK and nothing else.' | claude -p --max-turns 1 2>&1)"
SMOKE_CODE=$?
set -e
echo "$SMOKE"
echo "claude_smoke_exit=$SMOKE_CODE"
[ "$SMOKE_CODE" -eq 0 ] || fail "claude_noninteractive_failed"
echo "$SMOKE" | grep -q "GOX_RUNTIME_OK" || fail "claude_unexpected_smoke_output"

say "WRITE VERIFIED RUNTIME CONFIG"
cat > execution_bridge/config.json <<'JSON'
{
  "runtime": {
    "executable": "claude",
    "args": ["-p", "--max-turns", "3", "--permission-mode", "plan"],
    "prompt_via_stdin": true
  },
  "limits": {
    "agent_timeout_seconds": 300,
    "max_parallel_agents": 3
  }
}
JSON
cat execution_bridge/config.json

say "CREATE DISPOSABLE SAFE ENSEMBLE JOB"
cat > /tmp/gox_bridge_smoke_job.json <<'JSON'
{
  "job_id": "execution-bridge-smoke-v1",
  "objective": "Independently inspect this prompt and return a concise readiness assessment for the GOX execution bridge. Do not edit files, run shell commands, access accounts, browse, purchase, submit, or perform external actions. Reason only.",
  "definition_of_done": "Return GOX_AGENT_READY plus three concise checks: objective understood, no external action taken, ready for synthesis.",
  "constraints": [
    "No side effects",
    "No external actions",
    "No credentials",
    "No purchases or submissions",
    "Do not modify any file"
  ],
  "approval_gates": ["Any external or consequential action requires Ron"],
  "evidence_required": ["Text response from each independent agent"]
}
JSON

say "DRY RUN"
python3 execution_bridge/bridge.py /tmp/gox_bridge_smoke_job.json --config execution_bridge/config.json --dry-run

say "RUNTIME PROBE"
python3 execution_bridge/bridge.py /tmp/gox_bridge_smoke_job.json --config execution_bridge/config.json --probe

say "REAL 3-AGENT SAFE ENSEMBLE"
python3 execution_bridge/bridge.py /tmp/gox_bridge_smoke_job.json --config execution_bridge/config.json --ensemble 3

say "VERIFY OUTPUTS"
LATEST="$(find .gox/runs -type f -name 'synthesis*.json' -o -name 'status.json' 2>/dev/null | xargs -r ls -1t | head -n 1 || true)"
find .gox/runs -maxdepth 4 -type f 2>/dev/null | tail -n 30 || true
[ -n "$LATEST" ] || fail "no_persistent_run_evidence"
echo "latest_evidence=$LATEST"

say "RESULT"
echo "GOX_EXECUTION_BRIDGE=PASS"
echo "CLAUDE_RUNTIME=PASS"
echo "IDENTICAL_AGENT_ENSEMBLE=PASS"
echo "PERSISTENT_EVIDENCE=PASS"
echo "HERDR=$(command -v herdr 2>/dev/null || echo MISSING)"
echo "NEXT_AUTOMATION=paper_stack_compiler+synthesizer_judge+repair_loop+easy_job_sources"
echo "report=$REPORT"
