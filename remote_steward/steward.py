#!/usr/bin/env python3
from __future__ import annotations

import fcntl
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
LOG = ROOT / "steward.log"
LOCK = ROOT / "steward.lock"

ALLOWED = {
    "system_status": [["uname", "-a"], ["df", "-h", "/"], ["free", "-h"]],
    "runtime_status": [["bash", "-lc", "command -v herdr || true; herdr --version 2>/dev/null || true; command -v claude || true; claude --version 2>/dev/null || true; python3 --version; git --version"]],
    "bridge_tests": [["bash", "-lc", "cd /root/GOX-bridge && PYTHONPATH=/root/GOX-bridge python3 -m unittest execution_bridge.test_bridge -v"]],
    "bridge_finisher": [["bash", "-lc", "cd /root/GOX-bridge && timeout 600s bash scripts/finish_execution_bridge.sh"]],
    "bridge_probe": [["bash", "-lc", "cd /root/GOX-bridge && python3 execution_bridge/bridge.py /tmp/gox_bridge_smoke_job.json --config execution_bridge/config.json --probe"]],
    "git_status_bridge": [["bash", "-lc", "cd /root/GOX-bridge && git status --short --branch"]],
    "latest_bootstrap_log": [["bash", "-lc", "tail -n 200 /root/gox-bootstrap-report/latest.log 2>/dev/null || true"]],
    "core_state_tests": [["bash", "-lc", "cd /var/lib/gox-steward/mailbox && PYTHONPATH=. python3 -m unittest core.test_identity_revenue_state core.test_recovery -v"]],
    "secret_guard": [["bash", "-lc", "cd /var/lib/gox-steward/mailbox && python3 security/secret_guard.py ."]],
    "gap_scan": [["bash", "-lc", "cd /var/lib/gox-steward/mailbox && python3 quality/gap_scanner.py"]],
    "approval_health": [["bash", "-lc", "systemctl is-active gox-approval-bridge && curl -fsS http://127.0.0.1:8765/health"]],
    "chief_of_staff_snapshot": [["bash", "-lc", "cd /var/lib/gox-steward/mailbox && python3 core/chief_of_staff.py"]],
    "chatdev_smoke": [["bash", "-lc", "cd /var/lib/gox-steward/mailbox && test -s chatdev/index.html && test -s chatdev/server.py && python3 -m py_compile chatdev/server.py"]],
    "steward_self_test": [["bash", "-lc", "systemctl is-active gox-remote-steward; git -C /var/lib/gox-steward/mailbox status --short --branch; gh auth status >/dev/null && echo github_auth=ok"]],
}

REDACT_KEYS = ("token", "secret", "password", "authorization", "cookie", "api_key", "apikey")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_log(message: str) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    line = f"{now()} {message}\n"
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(line)
    try:
        if LOG.stat().st_size > 2_000_000:
            LOG.write_text(LOG.read_text()[-1_000_000:])
    except Exception:
        pass


def redact(text: str | None) -> str:
    text = text or ""
    for key in REDACT_KEYS:
        text = text.replace(key.upper(), "[REDACTED_KEY]").replace(key, "[REDACTED_KEY]")
    return text


def child_env() -> dict:
    env = os.environ.copy()
    env.setdefault("HOME", "/root")
    env.setdefault("XDG_CONFIG_HOME", "/root/.config")
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["PATH"] = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/root/.local/bin:/root/.hermes/node/bin"
    return env


def run(cmd: list[str]) -> dict:
    p = subprocess.run(cmd, text=True, capture_output=True, timeout=620, env=child_env())
    text = (p.stdout or "") + ("\nSTDERR:\n" + p.stderr if p.stderr else "")
    return {"cmd": cmd, "exit_code": p.returncode, "output": redact(text)[-30000:]}


def git(*args: str, check: bool = True):
    return subprocess.run(["git", "-C", str(MAILBOX), *args], text=True, capture_output=True, check=check, env=child_env())


def load_state() -> dict:
    if STATE.exists():
        try:
            data = json.loads(STATE.read_text())
            if isinstance(data.get("processed"), list):
                return data
        except Exception:
            pass
    return {"processed": []}


def save_state(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    os.replace(tmp, STATE)


def sync_mailbox() -> None:
    fetch = git("fetch", "origin", BRANCH, check=False)
    if fetch.returncode != 0:
        raise RuntimeError("git fetch failed: " + redact(fetch.stderr or fetch.stdout)[-2000:])
    git("checkout", BRANCH)
    rebase = git("rebase", f"origin/{BRANCH}", check=False)
    if rebase.returncode != 0:
        git("rebase", "--abort", check=False)
        raise RuntimeError("git rebase failed: " + redact(rebase.stderr or rebase.stdout)[-2000:])


def push_result(path: Path) -> None:
    rel = str(path.relative_to(MAILBOX))
    git("add", rel)
    commit = git("commit", "-m", f"steward result {path.stem}", check=False)
    combined = (commit.stdout or "") + (commit.stderr or "")
    if commit.returncode != 0 and "nothing to commit" not in combined.lower():
        raise RuntimeError("git commit failed: " + redact(combined)[-2000:])
    for attempt in range(3):
        p = git("push", "origin", f"HEAD:{BRANCH}", check=False)
        if p.returncode == 0:
            write_log(f"push_result ok path={rel} attempt={attempt + 1}")
            return
        write_log("push_result retry " + redact(p.stderr or p.stdout)[-1000:])
        fetch = git("fetch", "origin", BRANCH, check=False)
        if fetch.returncode != 0:
            continue
        rebase = git("rebase", f"origin/{BRANCH}", check=False)
        if rebase.returncode != 0:
            git("rebase", "--abort", check=False)
            continue
        time.sleep(1 + attempt)
    raise RuntimeError("git push failed: " + redact(p.stderr or p.stdout)[-2000:])


def process_one(path: Path, state: dict) -> None:
    req = json.loads(path.read_text())
    command_id = str(req.get("id") or path.stem)
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
    except Exception as exc:
        result["status"] = "failed"
        result["error"] = redact(str(exc))
    result["finished_at"] = now()
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / f"{command_id}.json"
    out.write_text(json.dumps(result, indent=2))
    push_result(out)
    state["processed"].append(command_id)
    state["processed"] = state["processed"][-1000:]
    save_state(state)
    write_log(f"processed id={command_id} action={action} status={result['status']}")


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    lock_fh = LOCK.open("w")
    try:
        fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit("another steward instance is already running")
    write_log("steward starting")
    state = load_state()
    while True:
        try:
            sync_mailbox()
            COMMANDS.mkdir(parents=True, exist_ok=True)
            for path in sorted(COMMANDS.glob("*.json")):
                process_one(path, state)
        except Exception as exc:
            message = redact(str(exc))
            (ROOT / "last_error.txt").write_text(f"{now()} {message}\n")
            write_log("loop_error " + message[-2000:])
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
