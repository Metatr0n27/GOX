from __future__ import annotations

import unittest

from revenue.easy_prompt_maximizer import Metrics, build_repair_prompt, detect_bottleneck


class EasyPromptMaximizerTests(unittest.TestCase):
    def test_no_opportunities(self):
        m = Metrics(actionable_opportunities=0)
        self.assertEqual(detect_bottleneck(m), "NO_OPPORTUNITIES")

    def test_low_pay_after_basic_health(self):
        m = Metrics(
            actionable_opportunities=3,
            qualification_rate=0.8,
            availability_rate=0.8,
            productive_dollars_per_hour=12,
            owner_minutes_per_paid_hour=5,
            payout_delay_hours=12,
            acceptance_rate=0.8,
            verified_samples=20,
        )
        self.assertEqual(detect_bottleneck(m), "LOW_PAY_RATE")

    def test_owner_time_bottleneck(self):
        m = Metrics(
            actionable_opportunities=3,
            qualification_rate=0.8,
            availability_rate=0.8,
            productive_dollars_per_hour=30,
            owner_minutes_per_paid_hour=30,
            payout_delay_hours=12,
            acceptance_rate=0.8,
            verified_samples=20,
        )
        self.assertEqual(detect_bottleneck(m), "HIGH_OWNER_TIME")

    def test_repair_prompt_has_tests_and_team(self):
        m = Metrics(actionable_opportunities=2, access_failures=1)
        p = build_repair_prompt(m)
        self.assertEqual(p.bottleneck, "ACCESS_BLOCKER")
        self.assertTrue(p.team)
        self.assertGreaterEqual(len(p.acceptance_tests), 5)
        self.assertIn("Diagnose the root cause", p.prompt)


if __name__ == "__main__":
    unittest.main()
