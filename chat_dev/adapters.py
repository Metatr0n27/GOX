#!/usr/bin/env python3
"""Allowlisted GOX capability adapters.

Adapters are named capabilities with validation and structured results. They never
receive an implicit shell. Privileged integrations must be added explicitly.
Each adapter executes in an isolated child process so its timeout is enforceable.
"""
import json
import multiprocessing as mp


class AdapterError(Exception):
    pass


class ValidationError(AdapterError):
    pass


