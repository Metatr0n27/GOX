#!/usr/bin/env python3
"""GOX SSH/VPS connector.

Uses the local OpenSSH client so GOX can execute approved commands on an
owner-authorized VPS without embedding credentials in source.

Required environment variables:
  GOX_VPS_HOST
  GOX_VPS_USER
Optional:
  GOX_VPS_PORT (default 22)
  GOX_VPS_KEY_PATH
  GOX_VPS_KNOWN_HOSTS (default ~/.ssh/known_hosts)
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class RemoteResult:
    ok: bool
    host: str
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float


class SSHVPSConnector:
    def __init__(self) -> None:
        self.host = os.environ.get("GOX_VPS_HOST", "").strip()
        self.user = os.environ.get("GOX_VPS_USER", "").strip()
        self.port = os.environ.get("GOX_VPS_PORT", "22").strip() or "22"
        self.key_path = os.environ.get("GOX_VPS_KEY_PATH", "").strip()
        self.known_hosts = os.environ.get(
            "GOX_VPS_KNOWN_HOSTS", str(Path.home() / ".ssh" / "known_hosts")
        ).strip()
        if not self.host or not self.user:
            raise RuntimeError("GOX_VPS_HOST and GOX_VPS_USER are required")

    def _base_args(self) -> list[str]:
        args = [
            "ssh",
            "-o", "BatchMode=yes",
            "-o", "StrictHostKeyChecking=yes",
            "-o", f"UserKnownHostsFile={self.known_hosts}",
            "-p", self.port,
        ]
        if self.key_path:
            args.extend(["-i", self.key_path])
        args.append(f"{self.user}@{self.host}")
        return args

    def run(self, command: str, timeout: int = 120) -> RemoteResult:
        if not command.strip():
            raise ValueError("command cannot be empty")
        start = time.monotonic()
        proc = subprocess.run(
            self._base_args() + [command],
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return RemoteResult(
            ok=proc.returncode == 0,
            host=self.host,
            command=command,
            exit_code=proc.returncode,
            stdout=proc.stdout[-12000:],
            stderr=proc.stderr[-12000:],
            duration_seconds=round(time.monotonic() - start, 3),
        )

    def health(self) -> RemoteResult:
        return self.run("printf 'GOX_SSH_OK\\n'; uname -a; uptime; df -h / | tail -1", timeout=30)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="GOX SSH/VPS connector")
    parser.add_argument("--health", action="store_true", help="run harmless VPS health check")
    parser.add_argument("--command", help="remote command to execute")
    args = parser.parse_args()

    connector = SSHVPSConnector()
    if args.health:
        result = connector.health()
    elif args.command:
        result = connector.run(args.command)
    else:
        parser.error("use --health or --command")

    print(json.dumps(asdict(result), indent=2))
    return 0 if result.ok else result.exit_code or 1


if __name__ == "__main__":
    raise SystemExit(main())
