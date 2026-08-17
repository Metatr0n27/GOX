#!/usr/bin/env python3
"""GOX Chat Dev - persistent local control surface."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64, hmac, json, os, sqlite3, time, uuid, sys
from pathlib import Path
HOST=os.getenv("GOX_HOST","127.0.0.1"); PORT=int(os.getenv("GOX_PORT","8080")); DATA_DIR=os.getenv("GOX_DATA_DIR",os.path.join(os.path.dirname(__file__),"data")); DB_PATH=os.path.join(DATA_DIR,"chat_dev.sqlite3"); MAX_BODY=int(os.getenv("GOX_MAX_REQUEST_BYTES","16384")); STARTED=time.time(); os.makedirs(DATA_DIR,exist_ok=True); AUTH_USER=os.getenv("GOX_AUTH_USER","gox"); AUTH_PASSWORD=os.getenv("GOX_AUTH_PASSWORD",""); DAILY_TARGET=float(os.getenv("GOX_DAILY_REVENUE_TARGET","500")); LOOPBACK={"127.0.0.1","localhost","::1"}
if HOST not in LOOPBACK and not AUTH_PASSWORD: raise RuntimeError("Refusing non-loopback bind without GOX_AUTH_PASSWORD")
ROOT=Path(__file__).resolve().parent.parent
if str(ROOT/"revenue_engine") not in sys.path: sys.path.insert(0,str(ROOT/"revenue_engine"))
try:
 from pipeline import read_queue
 from capabilities import readiness
except Exception:
 def read_queue(): return {"generated_at":None,"count":0,"items":[]}
 def readiness(): return []
try:
 from easy_prompts import list_prompts
except Exception:
 def list_prompts(): return []
from revenue import init_revenue_schema, revenue_summary
from sales import render_buy_page
PAGE=r'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GOX Chat Dev</title><style>:root{font-family:system-ui;color-scheme:dark}body{margin:0;background:#07111f;color:#eaf2ff}.wrap{max-width:1200px;margin:auto;padding:24px}.grid{display:grid;grid-template-columns:2fr 1fr;gap:16px}.card{background:#0d1b2e;border:1px solid #203653;border-radius:16px;padding:18px;margin-bottom:16px}.chat{height:300px;overflow:auto}.msg,.job,.opp{margin:8px 0;padding:10px;border-radius:10px;background:#122641}.you{background:#17375d}.row{display:flex;gap:8px;flex-wrap:wrap}input{flex:1;padding:12px}button{padding:10px 14px}.metric{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #203653}.ok{color:#7ff0b5}.wait{color:#ffd27a}.bad{color:#ff9292}.small{font-size:.85rem;opacity:.8}@media(max-width:760px){.grid{grid-template-columns:1fr}}</style></head><body><div class="wrap"><h1>GOX // CHAT DEV</h1><div class="grid"><main><section class="card"><h2>Easy Prompts</h2><div id="prompts" class="row"></div></section><section class="card"><h2>Chat</h2><div id="chat" class="chat"><div class="msg">Chat Dev online. Requests are persisted and executed only through allowlisted capabilities.</div></div><div class="row"><input id="q" maxlength="8000" placeholder="Tell GOX what to do..."><button onclick="send()">Send</button></div></section><section class="card"><h2>Money opportunities</h2><div id="opps">Loading…</div></section></main><aside><section class="card"><h2>Live status</h2><div id="status">Loading…</div><h3>Recent jobs</h3><div id="jobs"></div></section></aside></div></div><script>function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}async function send(v){let q=document.getElementById('q'),t=(v??q.value).trim();if(!t)return;add(t,'you');q.value='';let r=await fetch('/api/chat',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({message:t})});let d=await r.json();add(d.reply||d.error||'No response');refresh()}function add(t,c=''){let d=document.createElement('div');d.className='msg '+c;d.textContent=t;document.getElementById('chat').appendChild(d)}async function refresh(){try{let [s,j,o,p]=await Promise.all([fetch('/api/status').then(r=>r.json()),fetch('/api/jobs').then(r=>r.json()),fetch('/api/opportunities').then(r=>r.json()),fetch('/api/easy-prompts').then(r=>r.json())]);let x=s.jobs,r=s.revenue;document.getElementById('status').innerHTML=`<div class=metric><span>Queue</span><b class=ok>${x.queued}</b></div><div class=metric><span>Running</span><b>${x.running}</b></div><div class=metric><span>Blocked</span><b class=wait>${x.blocked}</b></div><div class=metric><span>Complete</span><b class=ok>${x.complete}</b></div><div class=metric><span>Opportunities</span><b class=ok>${o.count||0}</b></div><div class=metric><span>Collected today</span><b>$${r.current} / $${r.target}</b></div><div class=metric><span>Still needed</span><b class=wait>$${r.remaining}</b></div>`;document.getElementById('jobs').innerHTML=j.jobs.slice(0,8).map(v=>`<div class=job><b>${esc(v.status).toUpperCase()}</b> · ${esc(v.id)}<br>${esc(v.message).slice(0,100)}</div>`).join('');document.getElementById('prompts').innerHTML=p.prompts.map(v=>`<button onclick='send(${JSON.stringify(v.name)})'>${esc(v.name)}</button>`).join('');document.getElementById('opps').innerHTML=o.items.length?o.items.slice(0,10).map(v=>`<div class=opp><b>${esc(v.title)}</b><br><span class=ok>Score ${esc(v.score)}</span> · ${esc(v.currency)} ${esc(v.budget_min)}–${esc(v.budget_max)} · ${esc(v.capability)}<br><span class=small>${esc(v.state)} · ${esc(v.source)}</span>${v.source_url?`<br><a href="${esc(v.source_url)}" target="_blank" rel="noopener">Open source</a>`:''}</div>`).join(''):'No qualified opportunities yet.'}catch(e){document.getElementById('status').textContent='Status unavailable'}}document.getElementById('q').addEventListener('keydown',e=>{if(e.key==='Enter')send()});refresh();setInterval(refresh,5000)</script></body></html>'''
def db():
 c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; c.execute("PRAGMA journal_mode=WAL"); return c
def init_db():
 with db() as c:
  c.execute("CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,message TEXT NOT NULL,kind TEXT NOT NULL DEFAULT 'plan',status TEXT NOT NULL DEFAULT 'queued',result TEXT,error TEXT,created_at REAL NOT NULL,updated_at REAL NOT NULL)"); cols={r['name'] for r in c.execute('PRAGMA table_info(jobs)')}
  for name,ddl in [('attempts','INTEGER NOT NULL DEFAULT 0'),('lease_until','REAL')]:
   if name not in cols:c.execute(f'ALTER TABLE jobs ADD COLUMN {name} {ddl}')
  c.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status_created ON jobs(status,created_at)"); init_revenue_schema(c)
def create_job(message):
 jid=uuid.uuid4().hex[:12]; now=time.time()
 with db() as c:c.execute("INSERT INTO jobs(id,message,created_at,updated_at) VALUES(?,?,?,?)",(jid,message,now,now))
 return jid
def get_jobs(limit=25):
 with db() as c:rows=c.execute("SELECT id,message,kind,status,result,error,attempts,lease_until,created_at,updated_at FROM jobs ORDER BY created_at DESC LIMIT ?",(limit,)).fetchall()
 return [dict(r) for r in rows]
def counts():
 out={k:0 for k in ('queued','running','testing','blocked','complete','failed','quarantined')}
 with db() as c:
  for r in c.execute("SELECT status,COUNT(*) n FROM jobs GROUP BY status"):out[r['status']]=r['n']
 return out
def revenue_status():
 with db() as c:return revenue_summary(c,DAILY_TARGET)
init_db()
class Handler(BaseHTTPRequestHandler):
 def send_json(self,obj,status=200,extra_headers=None):
  raw=json.dumps(obj).encode(); self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(raw))); self.send_header('Cache-Control','no-store')
  for k,v in (extra_headers or {}).items():self.send_header(k,v)
  self.end_headers(); self.wfile.write(raw)
 def authorized(self):
  if not AUTH_PASSWORD:return True
  raw=self.headers.get('Authorization','')
  if not raw.startswith('Basic '):return False
  try:decoded=base64.b64decode(raw[6:],validate=True).decode(); user,password=decoded.split(':',1)
  except Exception:return False
  return hmac.compare_digest(user,AUTH_USER) and hmac.compare_digest(password,AUTH_PASSWORD)
 def require_auth(self):
  if self.authorized():return True
  self.send_json({'error':'authentication required'},401,{'WWW-Authenticate':'Basic realm="GOX Chat Dev"'}); return False
 def do_GET(self):
  if self.path=='/health':return self.send_json({'ok':True,'service':'gox-chat-dev','uptime_s':int(time.time()-STARTED),'auth_enabled':bool(AUTH_PASSWORD)})
  if self.path.rstrip('/')=='/buy':
   raw=render_buy_page(); self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Content-Length',str(len(raw))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(raw); return
  if not self.require_auth():return
  if self.path=='/api/status':
   oq=read_queue(); return self.send_json({'interface':'running','persistence':'running','job_queue':'running','agent_bridge':'allowlisted','auth':'enabled' if AUTH_PASSWORD else 'loopback-only','jobs':counts(),'opportunities':oq.get('count',0),'revenue':revenue_status()})
  if self.path.startswith('/api/jobs'):return self.send_json({'jobs':get_jobs()})
  if self.path=='/api/opportunities':return self.send_json(read_queue())
  if self.path=='/api/capabilities':return self.send_json({'capabilities':readiness()})
  if self.path=='/api/easy-prompts':return self.send_json({'prompts':list_prompts()})
  if self.path!='/':return self.send_json({'error':'not found'},404)
  raw=PAGE.encode(); self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Content-Length',str(len(raw))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(raw)
 def do_POST(self):
  if not self.require_auth():return
  if self.path!='/api/chat':return self.send_json({'error':'not found'},404)
  try:n=int(self.headers.get('Content-Length','0'))
  except ValueError:return self.send_json({'error':'invalid content length'},400)
  if n<=0 or n>MAX_BODY:return self.send_json({'error':'request too large or empty'},413 if n>MAX_BODY else 400)
  try:data=json.loads(self.rfile.read(n)); message=str(data.get('message','')).strip()
  except Exception:return self.send_json({'error':'invalid json'},400)
  if not message:return self.send_json({'error':'message required'},400)
  if len(message)>8000:return self.send_json({'error':'message too long'},413)
  jid=create_job(message); return self.send_json({'job_id':jid,'status':'queued','reply':f'Queued as {jid}.'},202)
 def log_message(self,fmt,*args):pass
if __name__=='__main__':print(f'GOX Chat Dev: http://{HOST}:{PORT}'); ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
