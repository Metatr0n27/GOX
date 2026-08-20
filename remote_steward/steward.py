#!/usr/bin/env python3
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("GOX_STEWARD_ROOT", "/var/lib/gox-steward"))
MAILBOX = ROOT / "mailbox"
STATE = ROOT / "state.json"
RESULTS = MAILBOX / "remote_steward" / "results"
COMMANDS = MAILBOX / "remote_steward" / "commands"
BRANCH = os.environ.get("GOX_STEWARD_BRANCH", "gox/remote-steward")
POLL_SECONDS = int(os.environ.get("GOX_STEWARD_POLL_SECONDS", "30"))

ALLOWED = {
    "system_status": [["uname", "-a"], ["df", "-h", "/"], ["free", "-h"]],
    "runtime_status": [["bash", "-lc", "command -v herdr || true; herdr --version 2>/dev/null || true; command -v claude || true; claude --version 2>/dev/null || true; python3 --version; git --version"]],
    "bridge_tests": [["bash", "-lc", "cd /root/GOX-bridge && PYTHONPATH=/root/GOX-bridge python3 -m unittest execution_bridge.test_bridge -v"]],
    "bridge_finisher": [["bash", "-lc", "cd /root/GOX-bridge && timeout 600s bash scripts/finish_execution_bridge.sh"]],
    "bridge_probe": [["bash", "-lc", "cd /root/GOX-bridge && python3 execution_bridge/bridge.py /tmp/gox_bridge_smoke_job.json --config execution_bridge/config.json --probe"]],
    "git_status_bridge": [["bash", "-lc", "cd /root/GOX-bridge && git status --short --branch"]],
    "latest_bootstrap_log": [["bash", "-lc", "tail -n 200 /root/gox-bootstrap-report/latest.log 2>/dev/null || true"]],
}

REDACT_KEYS = ("token", "secret", "password", "authorization", "cookie", "api_key", "apikey")


def now():
    return datetime.now(timezone.utc).isoformat()


def run(cmd):
    p = subprocess.run(cmd, text=True, capture_output=True, timeout=620)
    text = (p.stdout or "") + ("\nSTDERR:\n" + p.stderr if p.stderr else "")
    for key in REDACT_KEYS:
        text = text.replace(key.upper(), "[REDACTED_KEY]").replace(key, "[REDACTED_KEY]")
    return {"cmd": cmd, "exit_code": p.returncode, "output": text[-30000:]}


def git(*args, check=True):
    return subprocess.run(["git", "-C", str(MAILBOX), *args], text=True, capture_output=True, check=check)


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"processed": []}


def save_state(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2))


def sync_mailbox():
    git("fetch", "origin", BRANCH)
    git("checkout", BRANCH)
    git("reset", "--hard", f"origin/{BRANCH}")


def push_result(path):
    git("add", str(path.relative_to(MAILBOX)))
    git("commit", "-m", f"steward result {path.stem}")
    p = git("push", "origin", BRANCH, check=False)
    if p.returncode != 0:
        raise RuntimeError("git push failed: " + (p.stderr or p.stdout)[-2000:])


def process_one(path, state):
    req = json.loads(path.read_text())
    command_id = req.get("id") or path.stem
    action = req.get("action")
    if command_id in state["processed"]:
        return
    result = {"id": command_id, "action": action, "started_at": now(), "status": "rejected", "runs": []}
    try:
        if action not in ALLOWED:
            result["error"] = "action_not_allowlisted"
        else:
            result["status"] = "running"
            for cmd in ALLOWED[action]:
                result["runs"].append(run(cmd))
            result["status"] = "complete" if all(x["exit_code"] == 0 for x in result["runs"]) else "failed"
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
    result["finished_at"] = now()
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / f"{command_id}.json"
    out.write_text(json.dumps(result, indent=2))
    push_result(out)
    state["processed"].append(command_id)
    state["processed"] = state["processed"][-1000:]
    save_state(state)


def main():
    state = load_state()
    while True:
        try:
            sync_mailbox()
            COMMANDS.mkdir(parents=True, exist_ok=True)
            for path in sorted(COMMANDS.glob("*.json")):
                process_one(path, state)
        except Exception as e:
            (ROOT / "last_error.txt").write_text(f"{now()} {e}\n")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
