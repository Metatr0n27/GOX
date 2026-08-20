#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import secrets
import time
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(os.environ.get("GOX_APPROVAL_ROOT", "/var/lib/gox-approval"))
PENDING = ROOT / "pending"
DONE = ROOT / "done"
AUDIT = ROOT / "audit.jsonl"
TOKEN_FILE = ROOT / "owner_token"
INTERNAL_KEY_FILE = ROOT / "internal_key"
BIND = os.environ.get("GOX_APPROVAL_BIND", "127.0.0.1")
PORT = int(os.environ.get("GOX_APPROVAL_PORT", "8765"))


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    for p in (ROOT, PENDING, DONE):
        p.mkdir(parents=True, exist_ok=True)
    if not TOKEN_FILE.exists():
        TOKEN_FILE.write_text(secrets.token_urlsafe(32))
        TOKEN_FILE.chmod(0o600)
    if not INTERNAL_KEY_FILE.exists():
        INTERNAL_KEY_FILE.write_text(secrets.token_urlsafe(32))
        INTERNAL_KEY_FILE.chmod(0o600)


def owner_token() -> str:
    return TOKEN_FILE.read_text().strip()


def internal_key() -> str:
    return INTERNAL_KEY_FILE.read_text().strip()


def audit(event: dict) -> None:
    event = {"ts": now(), **event}
    with AUDIT.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, sort_keys=True) + "\n")


def safe_id(value: str) -> str:
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    return "".join(c for c in value if c in allowed)[:96]


def read_pending() -> list[dict]:
    items = []
    for path in sorted(PENDING.glob("*.json"), key=lambda p: p.stat().st_mtime):
        try:
            items.append(json.loads(path.read_text()))
        except Exception:
            continue
    return items


def html_page() -> bytes:
    return b"""<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>GOX Approvals</title><style>body{font-family:system-ui;margin:24px;max-width:720px}button{font-size:20px;padding:14px 20px;margin:6px;border-radius:12px}article{border:1px solid #bbb;padding:16px;margin:14px 0;border-radius:14px}.approve{background:#e8f7e8}.deny{background:#fdeaea}code{word-break:break-all}</style></head><body><h1>GOX Approval Queue</h1><div id='q'>Loading...</div><script>
const token=new URLSearchParams(location.search).get('token')||'';
async function load(){let r=await fetch('/api/approvals?token='+encodeURIComponent(token));if(!r.ok){document.getElementById('q').textContent='Authorization required';return;}let a=await r.json();let q=document.getElementById('q');q.innerHTML='';if(!a.length){q.textContent='No approvals waiting.';return;}for(const x of a){let e=document.createElement('article');e.innerHTML=`<h2>${x.title||x.id}</h2><p>${x.reason||''}</p><p><b>Site:</b> ${x.site||''}</p><p><b>Action:</b> ${x.action||''}</p><p><b>Job:</b> ${x.job_id||''}</p>`;for(const d of ['approve','deny']){let b=document.createElement('button');b.textContent=d==='approve'?'Approve':'Deny';b.className=d;b.onclick=async()=>{await fetch('/api/approvals/'+encodeURIComponent(x.id)+'/decision?token='+encodeURIComponent(token),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({decision:d})});load();};e.appendChild(b)}q.appendChild(e)}}load();setInterval(load,5000);
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    server_version = "GOXApproval/1.0"

    def _json(self, status: int, payload) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _auth_owner(self, parsed) -> bool:
        token = parse_qs(parsed.query).get("token", [""])[0]
        return secrets.compare_digest(token, owner_token())

    def _body(self) -> dict:
        n = int(self.headers.get("Content-Length", "0") or "0")
        if n > 65536:
            raise ValueError("body_too_large")
        raw = self.rfile.read(n) if n else b"{}"
        return json.loads(raw or b"{}")

    def log_message(self, fmt, *args):
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            return self._json(200, {"status": "ok", "pending": len(read_pending())})
        if parsed.path == "/":
            body = html_page()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return self.wfile.write(body)
        if parsed.path == "/api/approvals":
            if not self._auth_owner(parsed):
                return self._json(401, {"error": "unauthorized"})
            return self._json(200, read_pending())
        return self._json(404, {"error": "not_found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/approvals":
            supplied = self.headers.get("X-GOX-Internal-Key", "")
            if not secrets.compare_digest(supplied, internal_key()):
                return self._json(401, {"error": "unauthorized"})
            data = self._body()
            rid = safe_id(str(data.get("id") or f"approval-{int(time.time())}"))
            if not rid:
                return self._json(400, {"error": "bad_id"})
            item = {
                "id": rid,
                "job_id": str(data.get("job_id", ""))[:128],
                "title": str(data.get("title", "Owner approval required"))[:240],
                "reason": str(data.get("reason", ""))[:1200],
                "site": str(data.get("site", ""))[:300],
                "action": str(data.get("action", ""))[:600],
                "created_at": now(),
                "status": "pending",
            }
            (PENDING / f"{rid}.json").write_text(json.dumps(item, indent=2))
            audit({"event": "approval_created", "id": rid, "job_id": item["job_id"]})
            return self._json(201, item)
        prefix = "/api/approvals/"
        suffix = "/decision"
        if parsed.path.startswith(prefix) and parsed.path.endswith(suffix):
            if not self._auth_owner(parsed):
                return self._json(401, {"error": "unauthorized"})
            rid = safe_id(parsed.path[len(prefix):-len(suffix)].strip("/"))
            src = PENDING / f"{rid}.json"
            if not src.exists():
                return self._json(404, {"error": "not_found"})
            data = self._body()
            decision = data.get("decision")
            if decision not in ("approve", "deny"):
                return self._json(400, {"error": "invalid_decision"})
            item = json.loads(src.read_text())
            item.update({"status": "approved" if decision == "approve" else "denied", "decision": decision, "decided_at": now()})
            dst = DONE / f"{rid}.json"
            dst.write_text(json.dumps(item, indent=2))
            src.unlink()
            audit({"event": "approval_decided", "id": rid, "decision": decision, "job_id": item.get("job_id", "")})
            return self._json(200, item)
        return self._json(404, {"error": "not_found"})


def main() -> int:
    ensure_dirs()
    httpd = ThreadingHTTPServer((BIND, PORT), Handler)
    print(f"GOX_APPROVAL_BRIDGE=LISTENING {BIND}:{PORT}", flush=True)
    httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
