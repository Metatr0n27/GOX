#!/usr/bin/env python3
"""Allowlisted GOX capability adapters.

Adapters are named capabilities with validation and structured results. They never
receive an implicit shell. Any privileged integration must be added explicitly.
"""
import json


class AdapterError(Exception):
    pass


class ValidationError(AdapterError):
    pass


class UnknownCapability(AdapterError):
    pass


def _validate_message(payload):
    if not isinstance(payload, dict):
        raise ValidationError("payload must be an object")
    message = payload.get("message")
    if not isinstance(message, str) or not message.strip():
        raise ValidationError("message must be a non-empty string")
    if len(message) > 8000:
        raise ValidationError("message exceeds 8000 characters")
    return message.strip()


def plan(payload):
    message = _validate_message(payload)
    return {
        "accepted": True,
        "capability": "plan",
        "permission_class": "local_safe",
        "request": message,
        "next_gate": "specialist_adapter",
        "note": "Request captured safely; no privileged action or shell command was executed.",
    }


REGISTRY = {
    "plan": {
        "handler": plan,
        "permission_class": "local_safe",
        "timeout_seconds": 5,
        "description": "Safely capture a request as an execution plan envelope.",
    },
}


def describe():
    return {
        name: {k: v for k, v in spec.items() if k != "handler"}
        for name, spec in REGISTRY.items()
    }


def execute(name, payload):
    spec = REGISTRY.get(name)
    if not spec:
        raise UnknownCapability(f"capability not allowlisted: {name}")
    result = spec["handler"](payload)
    # Force JSON-serializability at the boundary.
    json.dumps(result)
    return result
