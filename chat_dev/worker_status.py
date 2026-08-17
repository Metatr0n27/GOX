#!/usr/bin/env python3
"""Read-only worker status collector for the ChatDev Worker Room."""
from __future__ import annotations
import json, subprocess, time
from pathlib import Path

FINISH_STATUS=Path('/var/lib/gox/finish-gox/status.json')
REVENUE_QUEUE=Path('/var/lib/gox/revenue/opportunities.json')
DEPLOY_HISTORY=Path('/var/lib/gox/deploy/history.log')


def _systemctl(unit:str)->dict:
    try:
        p=subprocess.run(['systemctl','is-active',unit],text=True,capture_output=True,timeout=3)
        raw=(p.stdout or p.stderr).strip()
        state='LIVE' if raw=='active' else ('WAITING' if raw in {'inactive','activating'} else 'DOWN')
        return {'unit':unit,'systemd':raw or 'unknown','state':state}
    except Exception as exc:
        return {'unit':unit,'systemd':'unknown','state':'DOWN','error':str(exc)}


def _mtime(path:Path):
    try:return path.stat().st_mtime
    except FileNotFoundError:return None


def _read_json(path:Path):
    try:return json.loads(path.read_text())
    except Exception:return None


def snapshot()->dict:
    now=time.time()
    worker=_systemctl('gox-chat-worker.service'); worker.update({'name':'ChatDev Worker','mission':'Execute queued allowlisted ChatDev jobs','last_activity':None})
    scout=_systemctl('gox-revenue-scout.timer'); scout.update({'name':'Revenue Scout','mission':'Refresh and rank buyer opportunities','last_activity':_mtime(REVENUE_QUEUE)})
    finish_data=_read_json(FINISH_STATUS) or {}
    finish=_systemctl('gox-finish-gox.timer'); finish.update({'name':'Finish GOX','mission':'Audit, repair, test, and re-audit routine runtime gaps','last_activity':finish_data.get('updated_at'),'detail':finish_data.get('state')})
    deploy=_systemctl('gox-pull-deploy.timer'); deploy.update({'name':'Deploy Bridge','mission':'Pull approved release, deploy, health-check, rollback if needed','last_activity':_mtime(DEPLOY_HISTORY)})
    rows=[worker,scout,finish,deploy]
    for row in rows:
        ts=row.get('last_activity'); row['age_seconds']=None if not ts else max(0,int(now-float(ts)))
        if row['state']=='LIVE' and row.get('detail')=='BLOCKED': row['state']='BLOCKED'
    return {'generated_at':now,'workers':rows}

if __name__=='__main__': print(json.dumps(snapshot(),indent=2))
