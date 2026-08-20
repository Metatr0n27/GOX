#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True)
class AdapterResult:
    source: str
    opportunities: list[dict[str, Any]]
    evidence: list[str]
    errors: list[str]


class SourceAdapter(Protocol):
    name: str

    def poll(self) -> AdapterResult:
        ...


def _as_list(payload: Any) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        return [payload]
    raise ValueError('source payload must be a JSON object or array')


def normalize_opportunity(item: dict[str, Any], *, source: str) -> dict[str, Any]:
    if 'id' not in item:
        raise ValueError('opportunity is missing stable id')

    normalized = dict(item)
    normalized['id'] = str(item['id'])
    normalized['source'] = str(item.get('source') or source)
    normalized['title'] = str(item.get('title') or item['id'])

    # Conservative defaults. Adapters must not manufacture permission,
    # funding, payout certainty, or executability.
    normalized.setdefault('rules_verdict', 'UNCLEAR')
    normalized.setdefault('funding_status', 'unknown')
    normalized.setdefault('verification_status', 'unverified')
    normalized.setdefault('settlement_status', 'unsettled')
    normalized.setdefault('executable_now', False)
    normalized.setdefault('payout_probability', 0.0)
    normalized.setdefault('payout_certainty', 0.0)
    normalized.setdefault('gox_share', 0.0)
    normalized.setdefault('owner_minutes', 0.0)
    normalized.setdefault('expected_cents', 0)
    normalized.setdefault('repeatability', 0.0)
    normalized.setdefault('time_to_cash_hours', 9999.0)
    normalized.setdefault('blocker', '')
    normalized.setdefault('owner_gate_kind', '')
    normalized.setdefault('next_action', '')
    normalized.setdefault('evidence', '')
    normalized.setdefault('payment_evidence', '')
    return normalized


class JsonFileAdapter:
    """Reference/test adapter for a controlled JSON source."""

    def __init__(self, path: Path, name: str = 'json_file') -> None:
        self.path = path
        self.name = name

    def poll(self) -> AdapterResult:
        evidence: list[str] = []
        errors: list[str] = []
        opportunities: list[dict[str, Any]] = []
        try:
            payload = json.loads(self.path.read_text())
            for raw in _as_list(payload):
                if not isinstance(raw, dict):
                    errors.append('skipped non-object opportunity')
                    continue
                try:
                    opportunities.append(normalize_opportunity(raw, source=self.name))
                except Exception as exc:
                    errors.append(str(exc))
            evidence.append(f'file:{self.path}')
        except Exception as exc:
            errors.append(str(exc))
        return AdapterResult(self.name, opportunities, evidence, errors)


class HttpJsonAdapter:
    """Read-only public JSON adapter.

    It deliberately performs no login, claim, acceptance, submission, or payment
    side effects. Runtime configuration supplies the URL and optional public
    headers. Response mapping remains source-specific and must be verified
    before a source is promoted to production use.
    """

    def __init__(self, *, name: str, url: str, timeout_seconds: float = 15.0,
                 headers: dict[str, str] | None = None) -> None:
        self.name = name
        self.url = url
        self.timeout_seconds = timeout_seconds
        self.headers = headers or {}

    def poll(self) -> AdapterResult:
        opportunities: list[dict[str, Any]] = []
        evidence: list[str] = []
        errors: list[str] = []
        try:
            request = urllib.request.Request(self.url, headers=self.headers, method='GET')
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode('utf-8')
                payload = json.loads(body)
                evidence.append(f'http:{self.url} status={response.status}')
                for raw in _as_list(payload):
                    if not isinstance(raw, dict):
                        errors.append('skipped non-object opportunity')
                        continue
                    try:
                        opportunities.append(normalize_opportunity(raw, source=self.name))
                    except Exception as exc:
                        errors.append(str(exc))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
        except Exception as exc:
            errors.append(str(exc))
        return AdapterResult(self.name, opportunities, evidence, errors)


def adapters_from_env() -> list[SourceAdapter]:
    """Load explicitly configured read-only adapters.

    GOX_REVENUE_HTTP_SOURCES is JSON like:
      [{"name":"source_a","url":"https://example/api/tasks"}]
    No credentials are accepted here. Authenticated adapters should be separate,
    source-specific modules with explicit security/rules review.
    """
    raw = os.getenv('GOX_REVENUE_HTTP_SOURCES', '').strip()
    if not raw:
        return []
    config = json.loads(raw)
    if not isinstance(config, list):
        raise ValueError('GOX_REVENUE_HTTP_SOURCES must be a JSON array')
    adapters: list[SourceAdapter] = []
    for item in config:
        if not isinstance(item, dict):
            raise ValueError('each HTTP source config must be an object')
        name = str(item['name'])
        url = str(item['url'])
        adapters.append(HttpJsonAdapter(name=name, url=url))
    return adapters


def poll_all(adapters: list[SourceAdapter]) -> list[AdapterResult]:
    return [adapter.poll() for adapter in adapters]
