import unittest

from creator_engine.stack import AGENT_SOPS, build_creator_plan


class CreatorStackTests(unittest.TestCase):
    def test_complete_creator_plan(self):
        plan = build_creator_plan({
            "creator": "Pilot Creator",
            "goal": "Turn one long-form video into a validated content package",
            "platform": "YouTube",
            "topic": "AI automation",
        })
        self.assertTrue(plan["accepted"])
        self.assertEqual(plan["capability"], "creator_plan")
        self.assertEqual(plan["workflow"][0], "creator_ceo")
        self.assertEqual(plan["workflow"][-1], "memory")
        self.assertEqual(plan["human_gates"], ["reviewer", "publisher"])
        self.assertIn("exploration_rule", plan)

    def test_required_fields(self):
        with self.assertRaisesRegex(ValueError, "creator is required"):
            build_creator_plan({"goal": "grow", "platform": "youtube"})
        with self.assertRaisesRegex(ValueError, "goal is required"):
            build_creator_plan({"creator": "x", "platform": "youtube"})
        with self.assertRaisesRegex(ValueError, "platform is required"):
            build_creator_plan({"creator": "x", "goal": "grow"})

    def test_every_workflow_agent_has_acceptance_criteria(self):
        plan = build_creator_plan({"creator": "x", "goal": "grow", "platform": "youtube"})
        for name in plan["workflow"]:
            self.assertIn(name, AGENT_SOPS)
            self.assertTrue(AGENT_SOPS[name].inputs)
            self.assertTrue(AGENT_SOPS[name].outputs)
            self.assertTrue(AGENT_SOPS[name].acceptance)


if __name__ == "__main__":
    unittest.main()
