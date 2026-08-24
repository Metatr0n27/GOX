from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from revenue.money_runner import Evidence, MoneyRunner, Opportunity


class MoneyRunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "browser_stack").mkdir(parents=True)
        self.runner = MoneyRunner(self.root, dry_run=True)

    def tearDown(self):
        self.tmp.cleanup()

    def sample(self):
        return Opportunity(
            id="op-1",
            title="Sample Task",
            platform="Example",
            url="https://example.com/task",
            family_lane="member-1",
            expected_pay=50,
            expected_minutes=60,
            qualification_probability=0.8,
            availability_probability=0.5,
            payout_delay_hours=0,
        )

    def test_add_and_rank(self):
        self.runner.add(self.sample())
        ranked = self.runner.ranked()
        self.assertEqual(ranked[0].id, "op-1")
        self.assertGreater(ranked[0].score(), 0)

    def test_proof_required_for_claim_states(self):
        self.runner.add(self.sample())
        for state in ("SUBMITTED", "ACCEPTED", "COMPLETED", "PAID"):
            with self.assertRaises(ValueError):
                self.runner.transition("op-1", state)

    def test_paid_transition_with_evidence(self):
        self.runner.add(self.sample())
        proof = Evidence(self.runner.now(), "PAYMENT_RECEIPT", "PayPal receipt verified", "receipt-123")
        item = self.runner.transition("op-1", "PAID", evidence=proof)
        self.assertEqual(item.status, "PAID")
        self.assertEqual(self.runner.status()["verified_paid_total"], 50)

    def test_owner_gate_and_resume(self):
        self.runner.add(self.sample())
        gated = self.runner.require_owner("op-1", "MFA", "Enter the MFA code", "Platform requires owner MFA")
        self.assertEqual(gated.status, "OWNER_GATE")
        queue = json.loads(self.runner.owner_queue_file.read_text())
        self.assertEqual(queue[0]["type"], "MFA")
        resumed = self.runner.resolve_owner("op-1", "Owner completed MFA in browser")
        self.assertEqual(resumed.status, "IN_PROGRESS")

    def test_spend_always_becomes_owner_gate(self):
        self.runner.add(self.sample())
        self.runner.spend_preflight("op-1", 6.99, None, "premium subscription", "Example", True)
        item = self.runner.load()[0]
        self.assertEqual(item.status, "OWNER_GATE")
        self.assertEqual(item.owner_gate["type"], "SPEND")
        self.assertIn("$6.99", item.owner_gate["exact_action"])

    def test_unknown_variable_spend_rejected(self):
        self.runner.add(self.sample())
        with self.assertRaises(ValueError):
            self.runner.spend_preflight("op-1", None, None, "unknown", "Example", False)


if __name__ == "__main__":
    unittest.main()
