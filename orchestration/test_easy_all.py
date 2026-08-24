from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from orchestration.easy_all import DEFAULT_FUNCTIONS, launch_money_now
from orchestration.explain_mode import make_instruction
from orchestration.idea_vault import Idea, save_idea


class EasyAllTests(unittest.TestCase):
    def test_launch_money_now_has_core_functions(self):
        plan = launch_money_now()
        for name in ("Easy Prompts", "Easy Jobs", "Money Runner", "Paper Stack", "Explain Mode"):
            self.assertIn(name, plan.functions)
        self.assertIn("verified dollars collected per owner-hour", plan.objective)

    def test_explain_modes(self):
        text = make_instruction("simple", "GOX", "last hour")
        self.assertIn("last hour", text)
        self.assertIn("verified facts", text)
        with self.assertRaises(ValueError):
            make_instruction("unknown", "GOX")

    def test_idea_vault_persists(self):
        with tempfile.TemporaryDirectory() as d:
            path = save_idea(Path(d), Idea("Add Easy All", "prevents forgotten functions", ["orchestration"], "less owner effort", "NOW"))
            self.assertTrue(path.exists())
            self.assertIn("Add Easy All", path.read_text())

    def test_default_registry_is_not_tiny(self):
        self.assertGreaterEqual(len(DEFAULT_FUNCTIONS), 10)


if __name__ == "__main__":
    unittest.main()
