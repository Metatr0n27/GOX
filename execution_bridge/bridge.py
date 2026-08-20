#!/usr/bin/env python3
"""GOX Agent Teams execution bridge.

Turns one job spec into a canonical prompt, runs an identical-agent ensemble,
collects outputs, and writes a machine-readable synthesis packet.

The bridge is deliberately runtime-agnostic. A concrete coding-agent CLI is
selected through config rather than hard-coded assumptions about Codex,
Claude, Gemini, OpenCode, Herdr, or any future runtime.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any

SAFE_STATES = {
    "READY",
    "WORKING",
    "TESTING",
    "REPAIRING",
    "BLOCKED_FOR_RON",
    "COMPLETE",
    "FAILED_WITH_EVIDENCE",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    tmp.replace(path)


def stable_id(payload: Any, prefix: str) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return f"{prefix}-{hashlib.sha256(raw).hexdigest()[:12]}"


def probe_runtime(config: dict[str, Any]) -> dict[str, Any]:
    """Detect configured and common agent CLIs without assuming invocation syntax."""
    configured = config.get("runtime", {}).get("executable")
    candidates = [configured, "codex", "claude", "gemini", "opencode", "herdr"]
    seen: set[str] = set()
    found: list[dict[str, str]] = []
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        resolved = shutil.which(candidate)
        if resolved:
            found.append({"name": candidate, "path": resolved})
    return {
        "configured": configured,
        "configured_available": bool(configured and shutil.which(configured)),
        "found": found,
    }


def canonical_prompt(job: dict[str, Any], context: dict[str, Any]) -> str:
    """Compile one canonical prompt from the job and Paper Stack context packet."""
    required = ["objective", "definition_of_done"]
    missing = [key for key in required if not job.get(key)]
    if missing:
        raise ValueError(f"Job is missing required fields: {', '.join(missing)}")

    parts = [
        "# GOX CANONICAL EXECUTION PROMPT",
        "",
        f"Job ID: {job.get('job_id', 'unassigned')}",
        f"Objective: {job['objective']}",
        "",
        "## Authoritative context",
        json.dumps(context, indent=2, ensure_ascii=False),
        "",
        "## Constraints",
        json.dumps(job.get("constraints", []), indent=2, ensure_ascii=False),
        "",
        "## Allowed actions",
        json.dumps(job.get("allowed_actions", []), indent=2, ensure_ascii=False),
        "",
        "## Approval-gated / forbidden actions",
        json.dumps(job.get("approval_gates", []), indent=2, ensure_ascii=False),
        "",
        "## Required evidence",
        json.dumps(job.get("required_evidence", []), indent=2, ensure_ascii=False),
        "",
        "## Tests",
        json.dumps(job.get("tests", []), indent=2, ensure_ascii=False),
        "",
        "## Definition of done",
        str(job["definition_of_done"]),
        "",
        "## Worker instructions",
        "Work independently. Do not assume another agent will fix omissions.",
        "Return a concrete result, evidence, discovered gaps, risks, and the exact next action.",
        "Do not claim completion without evidence. Do not perform approval-gated actions.",
    ]
    return "\n".join(parts).strip() + "\n"


def render_command(runtime: dict[str, Any], prompt_path: Path) -> list[str]:
    executable = runtime.get("executable")
    args = runtime.get("args", [])
    if not executable:
        raise ValueError("runtime.executable is required")
    if not isinstance(args, list) or not all(isinstance(x, str) for x in args):
        raise ValueError("runtime.args must be a list of strings")
    rendered = [str(x).replace("{prompt_file}", str(prompt_path)) for x in args]
    return [executable, *rendered]


def run_one_agent(
    index: int,
    prompt: str,
    runtime: dict[str, Any],
    run_dir: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    agent_id = f"agent-{index:02d}"
    agent_dir = run_dir / agent_id
    agent_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = agent_dir / "prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")
    stdout_path = agent_dir / "stdout.txt"
    stderr_path = agent_dir / "stderr.txt"

    command = render_command(runtime, prompt_path)
    stdin_mode = bool(runtime.get("prompt_via_stdin", False))
    started = time.monotonic()
    try:
        proc = subprocess.run(
            command,
            input=prompt if stdin_mode else None,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            cwd=str(agent_dir),
            env=os.environ.copy(),
            check=False,
        )
        elapsed = round(time.monotonic() - started, 3)
        stdout_path.write_text(proc.stdout or "", encoding="utf-8")
        stderr_path.write_text(proc.stderr or "", encoding="utf-8")
        return {
            "agent_id": agent_id,
            "command": command,
            "exit_code": proc.returncode,
            "elapsed_seconds": elapsed,
            "stdout_file": str(stdout_path),
            "stderr_file": str(stderr_path),
            "ok": proc.returncode == 0,
        }
    except subprocess.TimeoutExpired as exc:
        elapsed = round(time.monotonic() - started, 3)
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        stdout_path.write_text(stdout, encoding="utf-8")
        stderr_path.write_text(stderr, encoding="utf-8")
        return {
            "agent_id": agent_id,
            "command": command,
            "exit_code": None,
            "elapsed_seconds": elapsed,
            "stdout_file": str(stdout_path),
            "stderr_file": str(stderr_path),
            "ok": False,
            "error": "timeout",
        }


def run_ensemble(
    prompt: str,
    config: dict[str, Any],
    run_dir: Path,
    count: int,
) -> list[dict[str, Any]]:
    runtime = config["runtime"]
    timeout_seconds = int(config.get("limits", {}).get("agent_timeout_seconds", 900))
    max_parallel = max(1, int(config.get("limits", {}).get("max_parallel_agents", count)))
    workers = min(count, max_parallel)
    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(run_one_agent, i + 1, prompt, runtime, run_dir, timeout_seconds)
            for i in range(count)
        ]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    return sorted(results, key=lambda x: x["agent_id"])


def build_synthesis_packet(
    job: dict[str, Any],
    prompt_id: str,
    results: list[dict[str, Any]],
    run_dir: Path,
) -> dict[str, Any]:
    outputs = []
    for result in results:
        stdout = Path(result["stdout_file"]).read_text(encoding="utf-8", errors="replace")
        outputs.append({
            "agent_id": result["agent_id"],
            "ok": result["ok"],
            "exit_code": result["exit_code"],
            "output": stdout,
        })
    return {
        "schema": "gox.execution_bridge.synthesis.v1",
        "created_at": utc_now(),
        "job_id": job["job_id"],
        "prompt_id": prompt_id,
        "state": "TESTING" if any(x["ok"] for x in results) else "FAILED_WITH_EVIDENCE",
        "agent_results": outputs,
        "instructions_for_synthesizer": {
            "compare": [
                "agreements",
                "conflicts",
                "missing requirements",
                "strongest evidence",
                "risks",
                "best next action",
            ],
            "completion_rule": job["definition_of_done"],
            "do_not": "Mark complete only when required tests/evidence actually pass.",
        },
        "run_dir": str(run_dir),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="GOX Agent Teams execution bridge")
    parser.add_argument("job", type=Path, help="Path to job JSON")
    parser.add_argument("--config", type=Path, default=Path("execution_bridge/config.json"))
    parser.add_argument("--context", type=Path, help="Optional compiled Paper Stack context JSON")
    parser.add_argument("--ensemble", type=int, default=3, help="Number of identical agents")
    parser.add_argument("--runs-dir", type=Path, default=Path(".gox/runs"))
    parser.add_argument("--probe", action="store_true", help="Only report runtime availability")
    parser.add_argument("--dry-run", action="store_true", help="Compile prompt but do not execute agents")
    args = parser.parse_args()

    config = load_json(args.config)
    probe = probe_runtime(config)
    if args.probe:
        print(json.dumps(probe, indent=2))
        return 0 if probe["configured_available"] else 2

    job = load_json(args.job)
    if not job.get("job_id"):
        job["job_id"] = stable_id(job, "job")
    context = load_json(args.context) if args.context else {}
    prompt = canonical_prompt(job, context)
    prompt_id = stable_id({"job": job, "context": context, "prompt": prompt}, "prompt")
    run_id = f"run-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}-{prompt_id[-6:]}"
    run_dir = args.runs_dir / job["job_id"] / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "canonical_prompt.md").write_text(prompt, encoding="utf-8")
    write_json(run_dir / "job.json", job)
    write_json(run_dir / "runtime_probe.json", probe)

    if args.dry_run:
        write_json(run_dir / "status.json", {
            "state": "READY",
            "job_id": job["job_id"],
            "prompt_id": prompt_id,
            "run_id": run_id,
            "created_at": utc_now(),
            "dry_run": True,
        })
        print(run_dir)
        return 0

    if not probe["configured_available"]:
        write_json(run_dir / "status.json", {
            "state": "BLOCKED_FOR_RON",
            "reason": "Configured agent runtime executable is not available on PATH.",
            "probe": probe,
        })
        print(json.dumps(probe, indent=2), file=sys.stderr)
        return 2

    results = run_ensemble(prompt, config, run_dir, max(1, args.ensemble))
    packet = build_synthesis_packet(job, prompt_id, results, run_dir)
    write_json(run_dir / "synthesis_packet.json", packet)
    write_json(run_dir / "status.json", {
        "state": packet["state"],
        "job_id": job["job_id"],
        "prompt_id": prompt_id,
        "run_id": run_id,
        "updated_at": utc_now(),
    })
    print(run_dir)
    return 0 if any(r["ok"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
