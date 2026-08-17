#!/usr/bin/env python3
"""GOX Chat Dev resilient, allowlisted worker."""
import json
import os
import sqlite3
import time
from adapters import AdapterError, UnknownCapability, ValidationError, execute

DATA_DIR=os.getenv("GOX_DATA_DIR",os.path.join(os.path.dirname(__file__),"data"))
DB_PATH=os.path.join(DATA_DIR,"chat_dev.sqlite3")
POLL=float(os.getenv("GOX_WORKER_POLL","1"))
LEASE=float(os.getenv("GOX_JOB_LEASE_SECONDS","30"))
MAX_ATTEMPTS=int(os.getenv("GOX_JOB_MAX_ATTEMPTS","3"))


def db():
    c=sqlite3.connect(DB_PATH,timeout=10); c.row_factory=sqlite3.Row; return c


def recover_stale():
    now=time.time()
    with db() as c:
        rows=c.execute("SELECT id,attempts FROM jobs WHERE status='running' AND lease_until IS NOT NULL AND lease_until < ?",(now,)).fetchall()
        for row in rows:
            status='quarantined' if row['attempts'] >= MAX_ATTEMPTS else 'queued'
            error='worker lease expired; retry limit reached' if status=='quarantined' else 'worker lease expired; recovered for retry'
            c.execute("UPDATE jobs SET status=?,lease_until=NULL,error=?,updated_at=? WHERE id=?",(status,error,now,row['id']))


def claim():
    recover_stale(); now=time.time()
    with db() as c:
        c.execute("BEGIN IMMEDIATE")
        row=c.execute("SELECT * FROM jobs WHERE status='queued' AND attempts < ? ORDER BY created_at LIMIT 1",(MAX_ATTEMPTS,)).fetchone()
        if not row: return None
        cur=c.execute("UPDATE jobs SET status='running',attempts=attempts+1,lease_until=?,updated_at=? WHERE id=? AND status='queued'",(now+LEASE,now,row['id']))
        if cur.rowcount != 1: return None
        return dict(c.execute("SELECT * FROM jobs WHERE id=?",(row['id'],)).fetchone())


def finish(jid,status,result=None,error=None):
    with db() as c:
        c.execute("UPDATE jobs SET status=?,result=?,error=?,lease_until=NULL,updated_at=? WHERE id=?",(status,result,error,time.time(),jid))


def retry_or_quarantine(job,error):
    status='quarantined' if job['attempts'] >= MAX_ATTEMPTS else 'queued'
    finish(job['id'],status,error=error)


def payload_for(job):
    kind=job.get('kind','plan')
    if kind=='creator_plan':
        try:
            payload=json.loads(job['message'])
        except Exception as exc:
            raise ValidationError(f"creator_plan payload is not valid JSON: {exc}") from exc
        if not isinstance(payload,dict):
            raise ValidationError("creator_plan payload must be an object")
        return payload
    return {"message":job['message']}


def handle(job):
    try:
        result=execute(job.get('kind','plan'),payload_for(job))
        finish(job['id'],'complete',json.dumps(result))
    except (UnknownCapability,ValidationError) as exc:
        finish(job['id'],'blocked',error=str(exc))
    except AdapterError as exc:
        retry_or_quarantine(job,str(exc))
    except Exception as exc:
        retry_or_quarantine(job,f"unexpected adapter failure: {exc}")


def main():
    print(f"GOX worker using {DB_PATH}")
    while True:
        job=claim()
        if not job: time.sleep(POLL); continue
        handle(job)

if __name__=='__main__': main()
