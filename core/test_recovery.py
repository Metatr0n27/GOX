#!/usr/bin/env python3
import os,tempfile,unittest
from pathlib import Path
from datetime import timedelta

class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); os.environ['GOX_STATE_DB']=str(Path(self.tmp.name)/'gox.db')
        import importlib, core.recovery as r; self.r=importlib.reload(r)
    def tearDown(self): self.tmp.cleanup()
    def test_consequential_requires_idempotency(self):
        with self.assertRaises(ValueError): self.r.enqueue('j1','submit',consequential=True)
    def test_claim_and_complete(self):
        self.r.enqueue('j2','research'); j=self.r.claim('w1'); self.assertEqual(j['job_id'],'j2'); self.r.complete('j2')
        with self.r.connect() as c: self.assertEqual(c.execute("select status from jobs where job_id='j2'").fetchone()[0],'complete')
    def test_stale_nonconsequential_requeues(self):
        self.r.enqueue('j3','research'); self.r.claim('w1',lease_seconds=-1); out=self.r.recover_stale(); self.assertEqual(out[0]['status'],'queued')
    def test_stale_consequential_blocks(self):
        self.r.enqueue('j4','submit',consequential=True,idempotency_key='submit:1'); self.r.claim('w1',lease_seconds=-1); out=self.r.recover_stale(); self.assertEqual(out[0]['status'],'blocked')

if __name__=='__main__': unittest.main(verbosity=2)
