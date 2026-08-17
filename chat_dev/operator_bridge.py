#!/usr/bin/env python3
"""GOX Operator Bridge.

Fetches a GitHub control branch, executes only allowlisted maintenance tasks, and
writes durable local receipts for ChatDev/Worker Room visibility.

No arbitrary shell commands are accepted from the control branch.
"""
from __future__ import annotations
import hashlib, json, os, subprocess, tempfile, time
from pathlib import Path

REPO=Path(os.environ.get("GOX_DEPLOY_REPO","/opt/gox-deploy/repo"))
CONTROL_REF=os.environ.get("GOX_OPERATOR_CONTROL_REF","refs/heads/operator/control")
REMOTE_REF="refs/remotes/origin/operator/control"
STATE=Path(os.environ.get("GOX_OPERATOR_STATE","/var/lib/gox/operator"))
RECEIPTS=STATE/"receipts"
PROCESSED=STATE/"processed.json"
LIVE=Path(os.environ.get("GOX_LIVE_DIR","/opt/gox-live"))

ALLOWED={
    "verify-n8n": ["/bin/sh", str(LIVE/"deploy"/"verify-n8n.sh")],
    "refresh-buyer-requests": ["/usr/bin/python3", str(LIVE/"revenue_engine"/"pipeline.py")],
    "finish-gox-cycle": ["/usr/bin/python3", str(LIVE/"chat_dev"/"finish_gox_runner.py")],
    "restart-chatdev": ["/usr/bin/systemctl","restart","gox-chat-dev.service"],
    "restart-worker": ["/usr/bin/systemctl","restart","gox-chat-worker.service"],
    "status-workers": ["/usr/bin/python3", str(LIVE/"chat_dev"/"worker_status.py")],
}

def _run(cmd, timeout=180):
    started=time.time()
    try:
        p=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout,check=False)
        return {"ok":p.returncode==0,"code":p.returncode,"stdout":p.stdout[-8000:],"stderr":p.stderr[-8000:],"duration_s":round(time.time()-started,3)}
    except Exception as exc:
        return {"ok":False,"code":None,"stdout":"","stderr":str(exc),"duration_s":round(time.time()-started,3)}

def _load_processed():
    try:return set(json.loads(PROCESSED.read_text()).get("ids",[]))
    except Exception:return set()

def _save_processed(ids):
    STATE.mkdir(parents=True,exist_ok=True)
    tmp=PROCESSED.with_suffix('.tmp'); tmp.write_text(json.dumps({"ids":sorted(ids)},indent=2)); os.replace(tmp,PROCESSED)

def _fetch_tasks():
    fetch=_run(["/usr/bin/git","-C",str(REPO),"fetch","origin",f"{CONTROL_REF}:{REMOTE_REF}"],60)
    if not fetch["ok"]: raise RuntimeError(fetch["stderr"] or "control fetch failed")
    show=_run(["/usr/bin/git","-C",str(REPO),"show",f"{REMOTE_REF}:operator_control/tasks.json"],30)
    if not show["ok"]: raise RuntimeError(show["stderr"] or "task file unavailable")
    payload=json.loads(show["stdout"])
    if payload.get("version")!=1 or not isinstance(payload.get("tasks"),list): raise ValueError("unsupported task manifest")
    return payload

def _valid_task(task):
    tid=str(task.get("id","")).strip(); action=str(task.get("action","")).strip()
    if not tid or len(tid)>100:return False,"invalid id"
    if action not in ALLOWED:return False,"action not allowlisted"
    if task.get("args") not in (None,{},[]):return False,"arguments are not accepted"
    return True,""

def _receipt(task,result,status):
    RECEIPTS.mkdir(parents=True,exist_ok=True)
    tid=str(task.get("id","unknown")); safe=hashlib.sha256(tid.encode()).hexdigest()[:16]
    payload={"id":tid,"action":task.get("action"),"status":status,"finished_at":time.time(),"result":result}
    tmp=RECEIPTS/f"{safe}.tmp"; final=RECEIPTS/f"{safe}.json"; tmp.write_text(json.dumps(payload,indent=2,sort_keys=True)); os.replace(tmp,final)
    latest=STATE/"latest.json"; latest_tmp=STATE/"latest.tmp"; latest_tmp.write_text(json.dumps(payload,indent=2,sort_keys=True)); os.replace(latest_tmp,latest)
    return payload

def cycle():
    STATE.mkdir(parents=True,exist_ok=True); processed=_load_processed(); manifest=_fetch_tasks(); receipts=[]
    for task in manifest["tasks"]:
        tid=str(task.get("id","")).strip()
        if tid in processed:continue
        valid,reason=_valid_task(task)
        if not valid:
            receipts.append(_receipt(task,{"ok":False,"stderr":reason},"REJECTED")); processed.add(tid); continue
        result=_run(ALLOWED[task["action"]],int(task.get("timeout_seconds",180) or 180))
        receipts.append(_receipt(task,result,"PASS" if result["ok"] else "FAIL")); processed.add(tid)
    _save_processed(processed)
    return {"ok":True,"processed_now":len(receipts),"receipts":receipts}

if __name__=="__main__": print(json.dumps(cycle(),indent=2))
