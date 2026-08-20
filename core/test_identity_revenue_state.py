#!/usr/bin/env python3
import os
import tempfile
import unittest
from pathlib import Path

class StateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        os.environ['GOX_STATE_DB']=str(Path(self.tmp.name)/'gox.db')
        import importlib, core.identity_revenue_state as s
        self.s=importlib.reload(s)
        self.s.register_lane('ron','Ron')
        self.s.register_lane('patricia','Patricia')
    def tearDown(self): self.tmp.cleanup()
    def test_identity_separation_and_verified_money(self):
        self.s.record_revenue('r1','ron',gross=10,fees=1,payout_status='verified_paid',evidence_ref='receipt-1')
        self.s.record_revenue('r2','patricia',expected_net=20,probability=.5,payout_status='expected')
        d=self.s.dashboard()
        self.assertEqual(d['verified_net_earned'],9)
        self.assertEqual(d['probability_weighted_expected_net'],10)
        lanes={x['lane_id']:x for x in d['by_lane']}
        self.assertEqual(lanes['ron']['earned'],9)
        self.assertEqual(lanes['patricia']['expected'],10)
    def test_verified_paid_requires_evidence(self):
        with self.assertRaises(ValueError):
            self.s.record_revenue('bad','ron',gross=1,payout_status='verified_paid')
    def test_probability_bounds(self):
        with self.assertRaises(ValueError):
            self.s.record_revenue('bad2','ron',expected_net=1,probability=2)

if __name__=='__main__': unittest.main(verbosity=2)
