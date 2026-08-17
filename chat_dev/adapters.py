#!/usr/bin/env python3
"""Allowlisted GOX capability adapters with validation and hard timeouts."""
import multiprocessing as mp
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from creator_engine import build_creator_plan


class AdapterError(Exception):
    pass


class ValidationError(AdapterError):
    pass


class UnknownCapability(AdapterError):
    pass


class AdapterTimeout(AdapterError):
    pass


class AdapterFailed(AdapterError):
    pass


def _plan(payload):
    message = str(payload.get("message", "")).strip()
    if not message:
        raise ValidationError("message is required")
    return {"accepted": True, "capability": "plan", "message": message}


def _creator_plan(payload):
    try:
        return build_creator_plan(payload)
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc


REGISTRY = {
    "plan": {
        "handler": _plan,
        "permission_class": "read-only",
        "timeout_seconds": 10.0,
        "side_effecting": False,
        "description": "Validate and acknowledge a planning request.",
    },
    "creator_plan": {
        "handler": _creator_plan,
        "permission_class": "read-only",
        "timeout_seconds": 10.0,
        "side_effecting": False,
        "description": "Build a bounded, paper-backed Creator Engine workflow plan.",
    },
}


def _child(handler, payload, conn):
    try:
        conn.send(("ok", handler(payload)))
    except Exception as exc:
        conn.send(("err", exc.__class__.__name__, str(exc)))
    finally:
        conn.close()


def execute(capability, payload):
    spec = REGISTRY.get(capability)
    if spec is None:
        raise UnknownCapability(capability)
    if not isinstance(payload, dict):
        raise ValidationError("payload must be an object")

    parent, child = mp.Pipe(duplex=False)
    proc = mp.Process(target=_child, args=(spec["handler"], payload, child))
    proc.start()
    child.close()
    timeout = max(0.01, float(spec.get("timeout_seconds", 10.0)))
    if not parent.poll(timeout):
        proc.terminate()
        proc.join(1)
        if proc.is_alive():
            proc.kill()
            proc.join(1)
        parent.close()
        raise AdapterTimeout(f"{capability} exceeded {timeout}s")

    result = parent.recv()
    parent.close()
    proc.join(1)
    if result[0] == "ok":
        return result[1]
    exc_name, message = result[1], result[2]
    if exc_name == "ValidationError":
        raise ValidationError(message)
    raise AdapterFailed(f"{capability}: {exc_name}: {message}")
