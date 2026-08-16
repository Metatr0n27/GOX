#!/usr/bin/env python3
"""GOX Chat Dev - persistent, zero-dependency local control surface."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import sqlite3
import time
import uuid

HOST = os.getenv("GOX_HOST", "127.0.0.1")
PORT = int(os.getenv("GOX_PORT", "8080"))
DATA_DIR = os.getenv("GOX_DATA_DIR", os.path.join(os.path.dirname(__file__), "data"))
DB_PATH = os.path.join(DATA_DIR, "chat_dev.sqlite3")
STARTED = time.time()
os.makedirs(DATA_DIR, exist_ok=True)

PAGE = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GOX Chat Dev</title><style>:root{font-family:Inter,system-ui,sans-serif;color-scheme:dark}body{margin:0;background:#07111f;color:#eaf2ff}.wrap{max-width:1000px;margin:auto;padding:24px}.top{display:flex;justify-content:space-between;gap:16px;align-items:center}.brand{font-size:28px;font-weight:800}.pill{border:1px solid #294568;border-radius:999px;padding:7px 11px}.grid{display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-top:20px}.card{background:#0d1b2e;border:1px solid #203653;border-radius:16px;padding:18px}.chat{height:420px;overflow:auto;background:#081423;border-radius:12px;padding:12px}.msg{margin:9px 0;padding:10px 12px;border-radius:12px;background:#122641}.you{background:#17375d}.row{display:flex;gap:8px;margin-top:10px}input{flex:1;background:#07111f;color:#fff;border:1px solid #294568;border-radius:10px;padding:12px}button{border:0;border-radius:10px;padding:12px 18px;font-weight:700;cursor:pointer}.metric{display:flex;justify-content:space-between;border-bottom:1px solid #203653;padding:10px 0}.ok{color:#7ff0b5}.wait{color:#ffd27a}@media(max-width:760px){.grid{grid-template-columns:1fr}}</style></head><body><div class="wrap"><div class="top"><div><div class="brand">GOX // CHAT DEV</div><div>Persistent control surface</div></div><div class="pill"><span class="ok">●</span> LOCAL RUNTIME</div></div><div class="grid"><section class="card"><h2>Chat</h2><div id="chat" class="chat"><div class="msg">GOX Chat Dev is online. Messages are now persisted as jobs. Execution remains gated behind an allowlisted bridge.</div></div><div class="row"><input id="q" placeholder="Tell GOX what to do..." autofocus><button onclick="send()">Send</button></div></section><aside class="card"><h2>Status</h2><div class="metric"><span>Interface</span><b class="ok">RUNNING</b></div><div class="metric"><span>Persistence</span><b class="ok">RUNNING</b></div><div class="metric"><span>Job queue</span><b class="ok">RUNNING</b></div><div class="metric"><span>Agent bridge</span><b class="wait">GATED</b></div><div class="metric"><span>Revenue</span><b>$0 / $750</b></div><h3>Release gate</h3><p>Next: worker claims allowlisted jobs, updates visible state, then authentication + VPS deployment.</p></aside></div></div><script>async function send(){const q=document.getElementById('q'),text=q.value.trim();if(!text)return;add(text,'you');q.value='';const r=await fetch('/api/chat',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({message:text})});const d=await r.json();add(d.reply||d.error||'No response','msg')}function add(t,c){const d=document.createElement('div');d.className='msg '+(c||'');d.textContent=t;document.getElementById('chat').appendChild(d);d.scrollIntoView()}document.getElementById('q').addEventListener('keydown',e=>{if(e.key==='Enter')send()});</script></body></html>'''


def db():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    return c


def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS jobs(
            id TEXT PRIMARY KEY,
            message TEXT NOT NULL,
            kind TEXT NOT NULL DEFAULT 'plan',
            status TEXT NOT NULL DEFAULT 'queued',
            result TEXT,
            error TEXT,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        )""")
        c.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status_created ON jobs(status, created_at)")


def create_job(message):
    jid = uuid.uuid4().hex[:12]
    now = time.time()
    with db() as c:
        c.execute("INSERT INTO jobs(id,message,created_at,updated_at) VALUES(?,?,?,?)", (jid, message, now, now))
    return jid


def get_jobs(limit=25):
    with db() as c:
        rows = c.execute("SELECT id,message,kind,status,result,error,created_at,updated_at FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]


def counts():
    out = {"queued": 0, "running": 0, "testing": 0, "blocked": 0, "complete": 0, "failed": 0}
    with db() as c:
        for r in c.execute("SELECT status,COUNT(*) n FROM jobs GROUP BY status"):
            out[r["status"]] = r["n"]
    return out

init_db()

class Handler(BaseHTTPRequestHandler):
    def send_json(self, obj, status=200):
        raw=json.dumps(obj).encode(); self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        if self.path == "/health": return self.send_json({"ok":True,"service":"gox-chat-dev","uptime_s":int(time.time()-STARTED),"db":DB_PATH})
        if self.path == "/api/status": return self.send_json({"interface":"running","persistence":"running","job_queue":"running","agent_bridge":"gated","jobs":counts(),"revenue":{"current":0,"target":750}})
        if self.path.startswith("/api/jobs"): return self.send_json({"jobs":get_jobs()})
        raw=PAGE.encode(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_POST(self):
        if self.path != "/api/chat": return self.send_json({"error":"not found"},404)
        try:
            n=int(self.headers.get("Content-Length","0")); data=json.loads(self.rfile.read(n) or b"{}"); message=str(data.get("message","")).strip()
        except Exception: return self.send_json({"error":"invalid json"},400)
        if not message: return self.send_json({"error":"message required"},400)
        jid=create_job(message)
        return self.send_json({"job_id":jid,"status":"queued","reply":f"Queued as {jid}. The request is persisted and waiting for the gated GOX worker."},202)
    def log_message(self, fmt, *args): pass

if __name__ == "__main__":
    print(f"GOX Chat Dev: http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
