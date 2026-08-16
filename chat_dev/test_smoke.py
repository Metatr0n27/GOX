#!/usr/bin/env python3
"""Minimal repeatable tests for Chat Dev storage/worker contract."""
import os
import sqlite3
import subprocess
import sys
import tempfile
import time

HERE=os.path.dirname(__file__)
with tempfile.TemporaryDirectory() as d:
    env=os.environ.copy(); env['GOX_DATA_DIR']=d; env['GOX_HOST']='127.0.0.1'; env['GOX_PORT']='18080'; env['GOX_WORKER_POLL']='0.05'
    app=subprocess.Popen([sys.executable,os.path.join(HERE,'app.py')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    worker=None
    try:
        time.sleep(.3)
        import urllib.request, json
        assert json.load(urllib.request.urlopen('http://127.0.0.1:18080/health'))['ok'] is True
        req=urllib.request.Request('http://127.0.0.1:18080/api/chat',data=json.dumps({'message':'smoke test'}).encode(),headers={'content-type':'application/json'},method='POST')
        queued=json.load(urllib.request.urlopen(req)); assert queued['status']=='queued'; jid=queued['job_id']
        con=sqlite3.connect(os.path.join(d,'chat_dev.sqlite3')); assert con.execute('select status from jobs where id=?',(jid,)).fetchone()[0]=='queued'; con.close()
        worker=subprocess.Popen([sys.executable,os.path.join(HERE,'worker.py')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        deadline=time.time()+3
        status=None
        while time.time()<deadline:
            jobs=json.load(urllib.request.urlopen('http://127.0.0.1:18080/api/jobs'))['jobs']; status=next(x for x in jobs if x['id']==jid)['status']
            if status=='complete': break
            time.sleep(.05)
        assert status=='complete', status
        print('PASS: health -> queued -> persisted -> worker -> complete')
    finally:
        app.terminate()
        if worker: worker.terminate()
