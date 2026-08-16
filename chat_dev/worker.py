#!/usr/bin/env python3
"""GOX Chat Dev worker.

Claims persistent jobs and handles only explicitly allowlisted job kinds.
No user message is ever passed to a shell.
"""
import json
import os
import sqlite3
import time

DATA_DIR = os.getenv("GOX_DATA_DIR", os.path.join(os.path.dirname(__file__), "data"))
DB_PATH = os.path.join(DATA_DIR, "chat_dev.sqlite3")
POLL = float(os.getenv("GOX_WORKER_POLL", "1"))


def db():
    c=sqlite3.connect(DB_PATH, timeout=10)
    c.row_factory=sqlite3.Row
    return c


def claim():
    with db() as c:
        c.execute("BEGIN IMMEDIATE")
        row=c.execute("SELECT * FROM jobs WHERE status='queued' ORDER BY created_at LIMIT 1").fetchone()
        if not row: return None
        now=time.time()
        c.execute("UPDATE jobs SET status='running',updated_at=? WHERE id=? AND status='queued'",(now,row['id']))
        return dict(row)


def finish(jid,status,result=None,error=None):
    with db() as c:
        c.execute("UPDATE jobs SET status=?,result=?,error=?,updated_at=? WHERE id=?",(status,result,error,time.time(),jid))


def handle(job):
    kind=job.get('kind','plan')
    if kind == 'plan':
        # Safe first bridge: convert the request into a durable execution envelope.
        # Future allowlisted adapters can dispatch named GOX capabilities here.
        result={
            "accepted": True,
            "kind": "plan",
            "request": job['message'],
            "next_gate": "specialist_adapter",
            "note": "No shell command or privileged action was executed."
        }
        finish(job['id'],'complete',json.dumps(result))
        return
    finish(job['id'],'blocked',error=f"Job kind not allowlisted: {kind}")


def main():
    print(f"GOX worker using {DB_PATH}")
    while True:
        job=claim()
        if not job:
            time.sleep(POLL); continue
        try: handle(job)
        except Exception as exc: finish(job['id'],'failed',error=str(exc))

if __name__ == '__main__': main()
