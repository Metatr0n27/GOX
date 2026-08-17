#!/usr/bin/env python3
"""GOX Chat Dev - persistent local control surface."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64,hmac,json,os,sqlite3,time,uuid,sys
from pathlib import Path
HOST=os.getenv("GOX_HOST","127.0.0.1");PORT=int(os.getenv("GOX_PORT","8080"));DATA_DIR=os.getenv("GOX_DATA_DIR",os.path.join(os.path.dirname(__file__),"data"));DB_PATH=os.path.join(DATA_DIR,"chat_dev.sqlite3");MAX_BODY=int(os.getenv("GOX_MAX_REQUEST_BYTES","16384"));STARTED=time.time();os.makedirs(DATA_DIR,exist_ok=True);AUTH_USER=os.getenv("GOX_AUTH_USER","gox");AUTH_PASSWORD=os.getenv("GOX_AUTH_PASSWORD","");DAILY_TARGET=float(os.getenv("GOX_DAILY_REVENUE_TARGET","500"));LOOPBACK={"127.0.0.1","localhost","::1"};ALLOWED_KINDS={"plan","creator_plan"}
if HOST not in LOOPBACK and not AUTH_PASSWORD:raise RuntimeError("Refusing non-loopback bind without GOX_AUTH_PASSWORD")
ROOT=Path(__file__).resolve().parent.parent
if str(ROOT/"revenue_engine") not in sys.path:sys.path.insert(0,str(ROOT/"revenue_engine"))
try:
 from pipeline import read_queue
 from capabilities import readiness as capability_readiness
except Exception:
 def read_queue():return {"generated_at":None,"count":0,"items":[]}
 def capability_readiness():return []
try:
 from easy_prompts import list_prompts
except Exception:
 def list_prompts():return []
from revenue import init_revenue_schema,revenue_summary
from sales import render_buy_page,render_public_page,readiness as payment_readiness
PAGE=b'<!doctype html><html><head><meta charset="utf-8"><title>GOX Chat Dev</title></head><body style="font-family:system-ui;background:#07111f;color:#eef6ff;padding:30px"><h1>GOX // CHAT DEV</h1><p>Internal operator surface is online.</p><p><a style="color:#8fc5ff" href="/buy">Open public sales page</a></p></body></html>'
def db():
 c=sqlite3.connect(DB_PATH);c.row_factory=sqlite3.Row;c.execute("PRAGMA journal_mode=WAL");return c
def init_db():
 with db() as c:
  c.execute("CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,message TEXT NOT NULL,kind TEXT NOT NULL DEFAULT 'plan',status TEXT NOT NULL DEFAULT 'queued',result TEXT,error TEXT,created_at REAL NOT NULL,updated_at REAL NOT NULL)");cols={r['name'] for r in c.execute('PRAGMA table_info(jobs)')}
  for name,ddl in [('attempts','INTEGER NOT NULL DEFAULT 0'),('lease_until','REAL')]:
   if name not in cols:c.execute(f'ALTER TABLE jobs ADD COLUMN {name} {ddl}')
  c.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status_created ON jobs(status,created_at)");init_revenue_schema(c)
def create_job(message,kind="plan"):
 jid=uuid.uuid4().hex[:12];now=time.time()
 with db() as c:c.execute("INSERT INTO jobs(id,message,kind,created_at,updated_at) VALUES(?,?,?,?,?)",(jid,message,kind,now,now))
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
  raw=json.dumps(obj).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store')
  for k,v in (extra_headers or {}).items():self.send_header(k,v)
  self.end_headers();self.wfile.write(raw)
 def send_html(self,raw):
  self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(raw)
 def authorized(self):
  if not AUTH_PASSWORD:return True
  raw=self.headers.get('Authorization','')
  if not raw.startswith('Basic '):return False
  try:decoded=base64.b64decode(raw[6:],validate=True).decode();user,password=decoded.split(':',1)
  except Exception:return False
  return hmac.compare_digest(user,AUTH_USER) and hmac.compare_digest(password,AUTH_PASSWORD)
 def require_auth(self):
  if self.authorized():return True
  self.send_json({'error':'authentication required'},401,{'WWW-Authenticate':'Basic realm="GOX Chat Dev"'});return False
 def do_GET(self):
  path=self.path.split('?',1)[0].rstrip('/') or '/'
  if path=='/health':return self.send_json({'ok':True,'service':'gox-chat-dev','uptime_s':int(time.time()-STARTED),'auth_enabled':bool(AUTH_PASSWORD),'payment_readiness':payment_readiness()})
  if path=='/buy':return self.send_html(render_buy_page())
  public=render_public_page(path)
  if public:return self.send_html(public)
  if not self.require_auth():return
  if path=='/api/status':
   oq=read_queue();return self.send_json({'interface':'running','persistence':'running','job_queue':'running','agent_bridge':'allowlisted','allowed_job_kinds':sorted(ALLOWED_KINDS),'auth':'enabled' if AUTH_PASSWORD else 'loopback-only','jobs':counts(),'opportunities':oq.get('count',0),'revenue':revenue_status(),'payment_readiness':payment_readiness()})
  if path.startswith('/api/jobs'):return self.send_json({'jobs':get_jobs()})
  if path=='/api/opportunities':return self.send_json(read_queue())
  if path=='/api/capabilities':return self.send_json({'capabilities':capability_readiness()})
  if path=='/api/easy-prompts':return self.send_json({'prompts':list_prompts()})
  if path!='/':return self.send_json({'error':'not found'},404)
  return self.send_html(PAGE)
 def do_POST(self):
  if not self.require_auth():return
  if self.path!='/api/chat':return self.send_json({'error':'not found'},404)
  try:n=int(self.headers.get('Content-Length','0'))
  except ValueError:return self.send_json({'error':'invalid content length'},400)
  if n<=0 or n>MAX_BODY:return self.send_json({'error':'request too large or empty'},413 if n>MAX_BODY else 400)
  try:data=json.loads(self.rfile.read(n))
  except Exception:return self.send_json({'error':'invalid json'},400)
  kind=str(data.get('kind','plan')).strip()
  if kind not in ALLOWED_KINDS:return self.send_json({'error':'unsupported job kind'},400)
  if kind=='creator_plan':
   payload=data.get('payload')
   if not isinstance(payload,dict):return self.send_json({'error':'creator_plan payload object required'},400)
   message=json.dumps(payload,separators=(',',':'))
  else:
   message=str(data.get('message','')).strip()
   if not message:return self.send_json({'error':'message required'},400)
  jid=create_job(message,kind);return self.send_json({'job_id':jid,'kind':kind,'status':'queued','reply':f'Queued as {jid}.'},202)
 def log_message(self,fmt,*args):pass
if __name__=='__main__':print(f'GOX Chat Dev: http://{HOST}:{PORT}');ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
