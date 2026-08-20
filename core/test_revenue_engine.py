import sqlite3
import tempfile
import unittest
from pathlib import Path

from core import revenue_engine as re
from core.tedium_absorber import connect


class RevenueEngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / 'gox.db'
        self.db = connect(self.db_path)
        re.ensure_schema(self.db)

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def test_time_to_cash_zero_is_preserved(self):
        op = re.parse_opportunity({'id': 'x', 'time_to_cash_hours': 0})
        self.assertEqual(op.time_to_cash_hours, 0.0)

    def test_unclear_rules_are_rejected(self):
        op = re.parse_opportunity({'id': 'x', 'rules_verdict': 'UNCLEAR'})
        self.assertLess(re.score(op), -1_000_000)

    def test_blocker_is_rejected(self):
        op = re.parse_opportunity({'id': 'x', 'rules_verdict': 'ALLOWED', 'blocker': 'human-only assessment'})
        self.assertLess(re.score(op), -1_000_000)

    def test_funded_bonus_increases_score(self):
        base = {
            'id': 'x', 'rules_verdict': 'ALLOWED', 'expected_cents': 1000,
            'payout_probability': 0.5, 'owner_minutes': 10,
        }
        a = re.parse_opportunity(base)
        b = re.parse_opportunity({**base, 'funding_status': 'funded'})
        self.assertGreater(re.score(b), re.score(a))

    def test_settled_is_not_qualified(self):
        op = re.parse_opportunity({'id': 'x', 'rules_verdict': 'ALLOWED', 'settlement_status': 'settled'})
        re.upsert_opportunity(self.db, op)
        self.assertEqual(re.qualified(self.db), [])

    def test_record_outcome_calibrates_actual_owner_hour(self):
        op = re.parse_opportunity({
            'id': 'x', 'rules_verdict': 'ALLOWED', 'expected_cents': 2000,
            'payout_probability': 1.0, 'owner_minutes': 30,
        })
        re.upsert_opportunity(self.db, op)
        re.record_outcome(
            self.db, opportunity_id='x', actual_net_cents=1500,
            actual_owner_minutes=30, settlement_status='settled',
            payment_evidence='external:test',
        )
        summary = re.calibration_summary(self.db)
        self.assertEqual(summary['settled_samples'], 1)
        self.assertEqual(summary['mean_actual_owner_hour'], 30.0)

    def test_schema_migration_adds_money_evidence_columns(self):
        raw_path = Path(self.tmp.name) / 'legacy.db'
        raw = sqlite3.connect(raw_path)
        raw.execute('CREATE TABLE opportunities(id TEXT PRIMARY KEY)')
        raw.commit()
        re.ensure_schema(raw)
        cols = re._columns(raw, 'opportunities')
        for name in ('funding_status', 'verification_status', 'settlement_status', 'payment_evidence', 'predicted_owner_hour'):
            self.assertIn(name, cols)
        raw.close()


if __name__ == '__main__':
    unittest.main()
