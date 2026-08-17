#!/usr/bin/env python3
"""Bounded runtime loop for the Finish GOX Easy Prompt.

This runner only performs local, reversible, allowlisted maintenance. It does not
edit source code, submit marketplace proposals, spend money, or use credentials.
Its job is to keep routine runtime gaps from waiting on the owner and to leave a
machine-readable status for ChatDev.
"""
from __future__ import annotations
import json, os, subprocess, time
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
STATE=Path(os.environ.get("GOX_FINISH_STATE","/var/lib/gox/finish-gox"))
STATUS=STATE/"status.json"
HEALTH=os.environ.get("GOX_HEALTH_URL","http://127.0.0.1:8081/health")
MAX_SECONDS=int(os.environ.get("GOX_FINISH_MAX_SECONDS","120"))


def run(cmd:list[str], timeout:int=30)->dict:
    try:
        p=subprocess.run(cmd,cwd=str(ROOT),text=True,capture_output=True,timeout=timeout,check=False)
        return {"ok":p.returncode==0,"code":p.returncode,"stdout":p.stdout[-4000:],"stderr":p.stderr[-4000:]}
    except Exception as exc:
        return {"ok":False,"code":None,"stdout":"","stderr":str(exc)}


def audit()->dict:
    checks={}
    checks["chatdev_health"]=run(["curl","-fsS","--max-time","5",HEALTH],10)
    checks["worker_active"]=run(["systemctl","is-active","gox-chat-worker.service"],10)
    checks["deploy_timer_active"]=run(["systemctl","is-active","gox-pull-deploy.timer"],10)
    checks["revenue_scout_timer_active"]=run(["systemctl","is-active","gox-revenue-scout.timer"],10)
    q=Path(os.environ.get("GOX_REVENUE_STATE","/var/lib/gox/revenue"))/"opportunities.json"
    checks["revenue_queue_exists"]={"ok":q.exists(),"path":str(q)}
    return checks


def choose_gap(checks:dict)->dict|None:
    if not checks["chatdev_health"]["ok"]:
        return {"id":"chatdev_unhealthy","action":"restart_chatdev","priority":100}
    if not checks["worker_active"]["ok"]:
        return {"id":"worker_down","action":"restart_worker","priority":95}
    if not checks["deploy_timer_active"]["ok"]:
        return {"id":"deploy_timer_down","action":"enable_deploy_timer","priority":90}
    if not checks["revenue_scout_timer_active"]["ok"]:
        return {"id":"revenue_scout_down","action":"enable_revenue_scout","priority":85}
    if not checks["revenue_queue_exists"]["ok"]:
        return {"id":"revenue_queue_missing","action":"refresh_revenue_queue","priority":80}
    return None


def execute(action:str)->dict:
    if action=="restart_chatdev": return run(["systemctl","restart","gox-chat-dev.service"],30)
    if action=="restart_worker": return run(["systemctl","restart","gox-chat-worker.service"],30)
    if action=="enable_deploy_timer": return run(["systemctl","enable","--now","gox-pull-deploy.timer"],30)
    if action=="enable_revenue_scout": return run(["systemctl","enable","--now","gox-revenue-scout.timer"],30)
    if action=="refresh_revenue_queue": return run(["python3",str(ROOT/"revenue_engine"/"pipeline.py")],60)
    return {"ok":False,"stderr":"action not allowlisted"}


def write_status(payload:dict)->None:
    STATE.mkdir(parents=True,exist_ok=True)
    tmp=STATUS.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload,indent=2,sort_keys=True))
    os.replace(tmp,STATUS)


def cycle()->dict:
    started=time.time(); history=[]
    for _ in range(10):
        checks=audit(); gap=choose_gap(checks)
        if not gap:
            payload={"state":"RUNTIME_CLEAR","updated_at":time.time(),"checks":checks,"history":history,"human_required":False}
            write_status(payload); return payload
        result=execute(gap["action"]); history.append({"gap":gap,"result":result,"at":time.time()})
        if not result.get("ok") or time.time()-started>MAX_SECONDS:
            payload={"state":"BLOCKED","updated_at":time.time(),"checks":audit(),"history":history,"human_required":False,"blocker":gap["id"]}
            write_status(payload); return payload
        time.sleep(2)
    payload={"state":"BOUNDED_STOP","updated_at":time.time(),"checks":audit(),"history":history,"human_required":False}
    write_status(payload); return payload

if __name__=="__main__": print(json.dumps(cycle(),indent=2))
