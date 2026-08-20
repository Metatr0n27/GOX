import json
import tempfile
import unittest
from pathlib import Path

try:
    from execution_bridge import bridge
except ImportError:
    import bridge


class BridgeTests(unittest.TestCase):
    def test_stable_id_is_repeatable(self):
        payload = {"b": 2, "a": 1}
        self.assertEqual(bridge.stable_id(payload, "x"), bridge.stable_id(payload, "x"))

    def test_canonical_prompt_requires_core_fields(self):
        with self.assertRaises(ValueError):
            bridge.canonical_prompt({"objective": "x"}, {})

    def test_canonical_prompt_includes_context_and_done(self):
        job = {
            "job_id": "job-1",
            "objective": "clean data",
            "definition_of_done": "validated csv",
            "constraints": ["no guessing"],
        }
        text = bridge.canonical_prompt(job, {"source": "paper-stack"})
        self.assertIn("clean data", text)
        self.assertIn("validated csv", text)
        self.assertIn("paper-stack", text)

    def test_render_command_substitutes_prompt_file(self):
        runtime = {
            "executable": "agent-cli",
            "args": ["run", "{prompt_file}"],
        }
        cmd = bridge.render_command(runtime, Path("/tmp/prompt.md"))
        self.assertEqual(cmd, ["agent-cli", "run", "/tmp/prompt.md"])

    def test_write_json_is_readable(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "state" / "status.json"
            bridge.write_json(path, {"state": "READY"})
            self.assertEqual(json.loads(path.read_text())["state"], "READY")


if __name__ == "__main__":
    unittest.main()
