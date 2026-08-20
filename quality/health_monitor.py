#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> dict:
    p = subprocess.run(cmd, text=True, capture_output=True)
    return {
        "cmd": cmd,
        "exit_code": p.returncode,
        "output": ((p.stdout or "") + ("\n" + p.stderr if p.stderr else ""))[-8000:],
    }


def service(name: str) -> dict:
    if shutil.which("systemctl") is None:
        return {"name": name, "status": "unavailable"}
    p = subprocess.run(["systemctl", "is-active", name], text=True, capture_output=True)
    return {"name": name, "status": (p.stdout or p.stderr).strip(), "exit_code": p.returncode}


def main() -> int:
    gap = run(["python3", str(ROOT / "quality" / "gap_scanner.py")])
    try:
        gap_json = json.loads(gap["output"])
    except Exception:
        gap_json = {"parse_error": True, "raw": gap["output"]}

    snapshot = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "services": [
            service("gox-remote-steward"),
            service("gox-approval-bridge"),
            service("gox-approval"),
        ],
        "gap_scan": gap_json,
        "git_mailbox": run(["git", "-C", "/var/lib/gox-steward/mailbox", "status", "--short", "--branch"]),
        "approval_health": run(["curl", "-fsS", "http://127.0.0.1:8765/health"]),
        "steward_last_error": "",
    }

    err = Path("/var/lib/gox-steward/last_error.txt")
    if err.exists():
        snapshot["steward_last_error"] = err.read_text()[-4000:]

    print(json.dumps(snapshot, indent=2, sort_keys=True))
    critical_bad = any(
        s.get("status") not in {"active", "unavailable", "inactive"}
        for s in snapshot["services"]
    )
    return 2 if critical_bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
