#!/usr/bin/env python3
"""Repeatable Chat Dev persistence, limits, and lease-recovery tests."""
import json, os, sqlite3, subprocess, sys, tempfile, time, urllib.error, urllib.request
HERE=os.path.dirname(__file__)

def get(url): return json.load(urllib.request.urlopen(url))
def post(url,payload):
    req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={'content-type':'application/json'},method='POST')
    return json.load(urllib.request.urlopen(req))

with tempfile.TemporaryDirectory() as d:
    env=os.environ.copy(); env.update(GOX_DATA_DIR=d,GOX_HOST='127.0.0.1',GOX_PORT='18080',GOX_WORKER_POLL='0.05',GOX_JOB_LEASE_SECONDS='0.25',GOX_JOB_MAX_ATTEMPTS='2',GOX_MAX_REQUEST_BYTES='256')
    app=subprocess.Popen([sys.executable,os.path.join(HERE,'app.py')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE); worker=None
    try:
        time.sleep(.35); assert get('http://127.0.0.1:18080/health')['ok'] is True
        queued=post('http://127.0.0.1:18080/api/chat',{'message':'smoke test'}); jid=queued['job_id']
        con=sqlite3.connect(os.path.join(d,'chat_dev.sqlite3')); assert con.execute('select status from jobs where id=?',(jid,)).fetchone()[0]=='queued'
        # Simulate a dead worker holding an expired lease. The real worker must recover it.
        con.execute("update jobs set status='running',attempts=1,lease_until=? where id=?",(time.time()-.1,jid)); con.commit(); con.close()
        worker=subprocess.Popen([sys.executable,os.path.join(HERE,'worker.py')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        deadline=time.time()+3; job=None
        while time.time()<deadline:
            job=next(x for x in get('http://127.0.0.1:18080/api/jobs')['jobs'] if x['id']==jid)
            if job['status']=='complete': break
            time.sleep(.05)
        assert job['status']=='complete',job; assert job['attempts']==2,job
        status=get('http://127.0.0.1:18080/api/status'); assert status['jobs']['complete']==1
        # Oversized request is rejected before JSON parsing/persistence.
        big=urllib.request.Request('http://127.0.0.1:18080/api/chat',data=b'x'*300,headers={'content-type':'application/json'},method='POST')
        try: urllib.request.urlopen(big); raise AssertionError('oversized request accepted')
        except urllib.error.HTTPError as exc: assert exc.code==413
        print('PASS: health -> persistence -> expired lease recovery -> completion -> live status -> request limit')
    finally:
        app.terminate()
        if worker: worker.terminate()
