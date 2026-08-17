#!/usr/bin/env python3
"""Bounded GOX runtime/revenue readiness loop."""
from __future__ import annotations
import json,os,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;STATE=Path(os.environ.get("GOX_FINISH_STATE","/var/lib/gox/finish-gox"));STATUS=STATE/"status.json";HEALTH=os.environ.get("GOX_HEALTH_URL","http://127.0.0.1:8081/health");MAX_SECONDS=int(os.environ.get("GOX_FINISH_MAX_SECONDS","120"))
def run(cmd,timeout=30):
 try:
  p=subprocess.run(cmd,cwd=str(ROOT),text=True,capture_output=True,timeout=timeout,check=False);return {"ok":p.returncode==0,"code":p.returncode,"stdout":p.stdout[-4000:],"stderr":p.stderr[-4000:]}
 except Exception as exc:return {"ok":False,"code":None,"stdout":"","stderr":str(exc)}
def audit():
 checks={"chatdev_health":run(["curl","-fsS","--max-time","5",HEALTH],10),"worker_active":run(["systemctl","is-active","gox-chat-worker.service"],10),"deploy_timer_active":run(["systemctl","is-active","gox-pull-deploy.timer"],10),"revenue_scout_timer_active":run(["systemctl","is-active","gox-revenue-scout.timer"],10)}
 q=Path(os.environ.get("GOX_REVENUE_STATE","/var/lib/gox/revenue"))/"opportunities.json";checks["revenue_queue_exists"]={"ok":q.exists(),"path":str(q)}
 try:
  from sales import readiness
  pr=readiness();checks["payment_ready"]={"ok":bool(pr.get("ready")),**pr}
 except Exception as exc:checks["payment_ready"]={"ok":False,"error":str(exc),"missing":["payment_readiness_check"]}
 return checks
def choose_gap(c):
 if not c["chatdev_health"]["ok"]:return {"id":"chatdev_unhealthy","action":"restart_chatdev","priority":100,"human_required":False}
 if not c["worker_active"]["ok"]:return {"id":"worker_down","action":"restart_worker","priority":95,"human_required":False}
 if not c["deploy_timer_active"]["ok"]:return {"id":"deploy_timer_down","action":"enable_deploy_timer","priority":90,"human_required":False}
 if not c["revenue_scout_timer_active"]["ok"]:return {"id":"revenue_scout_down","action":"enable_revenue_scout","priority":85,"human_required":False}
 if not c["revenue_queue_exists"]["ok"]:return {"id":"revenue_queue_missing","action":"refresh_revenue_queue","priority":80,"human_required":False}
 if not c["payment_ready"]["ok"]:return {"id":"payment_not_ready","action":"payment_human_gate","priority":110,"human_required":True,"missing":c["payment_ready"].get("missing",[])}
 return None
def execute(action):
 m={"restart_chatdev":["systemctl","restart","gox-chat-dev.service"],"restart_worker":["systemctl","restart","gox-chat-worker.service"],"enable_deploy_timer":["systemctl","enable","--now","gox-pull-deploy.timer"],"enable_revenue_scout":["systemctl","enable","--now","gox-revenue-scout.timer"],"refresh_revenue_queue":["python3",str(ROOT/"revenue_engine"/"pipeline.py")]}
 if action=="payment_human_gate":return {"ok":False,"human_required":True,"stderr":"Hosted checkout and/or public support contact must be configured; processor identity/account review may require owner action."}
 return run(m.get(action,["false"]),60)
def write_status(p):
 STATE.mkdir(parents=True,exist_ok=True);tmp=STATUS.with_suffix('.tmp');tmp.write_text(json.dumps(p,indent=2,sort_keys=True));os.replace(tmp,STATUS)
def cycle():
 started=time.time();history=[]
 for _ in range(10):
  checks=audit();gap=choose_gap(checks)
  if not gap:
   p={"state":"REVENUE_RUNTIME_CLEAR","updated_at":time.time(),"checks":checks,"history":history,"human_required":False};write_status(p);return p
  if gap.get("human_required"):
   p={"state":"HUMAN_GATE","updated_at":time.time(),"checks":checks,"history":history,"human_required":True,"blocker":gap};write_status(p);return p
  result=execute(gap["action"]);history.append({"gap":gap,"result":result,"at":time.time()})
  if not result.get("ok") or time.time()-started>MAX_SECONDS:
   p={"state":"BLOCKED","updated_at":time.time(),"checks":audit(),"history":history,"human_required":False,"blocker":gap};write_status(p);return p
  time.sleep(2)
 p={"state":"BOUNDED_STOP","updated_at":time.time(),"checks":audit(),"history":history,"human_required":False};write_status(p);return p
if __name__=="__main__":print(json.dumps(cycle(),indent=2))
