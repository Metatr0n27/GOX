#!/usr/bin/env python3
"""Minimal GOX ChatDev cockpit API. Local-only by default."""
import json, os, sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parent
DB=Path(os.environ.get('GOX_STATE_DB','/var/lib/gox/state/gox.db'))
APPROVAL_ROOT=Path(os.environ.get('GOX_APPROVAL_ROOT','/var/lib/gox-approval'))
BIND=os.environ.get('GOX_CHATDEV_BIND','127.0.0.1')
PORT=int(os.environ.get('GOX_CHATDEV_PORT','8770'))

def rows(sql):
    if not DB.exists(): return []
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row
    try: return [dict(r) for r in con.execute(sql).fetchall()]
    except sqlite3.OperationalError: return []
    finally: con.close()

def money():
    if not DB.exists(): return {'earned':0,'expected':0}
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row
    try:
        earned=con.execute("SELECT COALESCE(SUM(net),0) v FROM revenue WHERE payout_status='verified_paid'").fetchone()['v']
        expected=con.execute("SELECT COALESCE(SUM(expected_net*probability),0) v FROM revenue WHERE payout_status!='verified_paid'").fetchone()['v']
        return {'earned':earned,'expected':expected}
    except sqlite3.OperationalError: return {'earned':0,'expected':0}
    finally: con.close()

def approvals():
    out=[]
    p=APPROVAL_ROOT/'pending'
    if p.exists():
        for f in sorted(p.glob('*.json')):
            try: out.append(json.loads(f.read_text()))
            except Exception: pass
    return out

def snapshot():
    jobs=rows("SELECT job_id,lane_id,kind,status,attempt_count,max_attempts,last_error,updated_at FROM jobs ORDER BY updated_at DESC LIMIT 100")
    ev=rows("SELECT event_id,event_type,lane_id,object_id,payload_json,created_at FROM events ORDER BY event_id DESC LIMIT 100")
    for e in ev:
        try:e['payload']=json.loads(e.pop('payload_json'))
        except Exception:e['payload']={}
    roles={'pm':'idle','developer':'idle','tester':'idle','reviewer':'idle'}
    for j in jobs:
        k=(j.get('kind') or '').lower(); s=j.get('status') or 'unknown'
        if any(x in k for x in ('plan','triage','coordinate')): roles['pm']=s
        if any(x in k for x in ('build','code','implement','repair')): roles['developer']=s
        if 'test' in k: roles['tester']=s
        if any(x in k for x in ('review','judge','qa')): roles['reviewer']=s
    return {'roles':roles,'jobs':jobs,'events':ev,'approvals':approvals(),'money':money()}

class H(BaseHTTPRequestHandler):
    def log_message(self,*a): return
    def send_json(self,obj,status=200):
        b=json.dumps(obj).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        p=urlparse(self.path).path
        if p=='/api/state': return self.send_json(snapshot())
        if p=='/health': return self.send_json({'status':'ok'})
        if p in ('/','/index.html'):
            b=(ROOT/'index.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(b)));self.end_headers();return self.wfile.write(b)
        return self.send_json({'error':'not_found'},404)

if __name__=='__main__':
    print(f'GOX_CHATDEV=LISTENING {BIND}:{PORT}',flush=True)
    ThreadingHTTPServer((BIND,PORT),H).serve_forever()
