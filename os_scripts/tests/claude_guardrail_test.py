import json
import os
import subprocess
import sys
import unittest


class TestClaudeGuardrailHook(unittest.TestCase):
    def setUp(self):
        self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.guardrail_path = os.path.join(self.repo_root, ".claude", "hooks", "guardrail.py")

    def run_hook(self, payload):
        return subprocess.run(
            [sys.executable, self.guardrail_path],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
        )

    def test_read_blocks_env_file(self):
        result = self.run_hook({
            "tool_name": "Read",
            "tool_input": {"file_path": ".env"},
        })

        self.assertEqual(result.returncode, 2)
        self.assertIn("SECURITY BLOCK", result.stderr)

    def test_read_blocks_nested_secret_paths(self):
        for path in [
            "path/to/.env",
            "path/to/.env.local",
            "src/credentials.txt",
            "path/to/secret-prod.txt",
        ]:
            with self.subTest(path=path):
                result = self.run_hook({
                    "tool_name": "Read",
                    "tool_input": {"file_path": path},
                })

                self.assertEqual(result.returncode, 2)
                self.assertIn(path, result.stderr)

    def test_bash_blocks_env_file_reference(self):
        result = self.run_hook({
            "tool_name": "Bash",
            "tool_input": {"command": "cat .env"},
        })

        self.assertEqual(result.returncode, 2)
        self.assertIn(".env", result.stderr)

    def test_bash_blocks_secret_pattern_reference(self):
        result = self.run_hook({
            "tool_name": "Bash",
            "tool_input": {"command": "cat secret-prod.txt"},
        })

        self.assertEqual(result.returncode, 2)
        self.assertIn("secret-prod.txt", result.stderr)

    def test_bash_blocks_nested_secret_paths(self):
        for command, blocked_path in [
            ("cat path/to/.env", "path/to/.env"),
            ("cat src/credentials.txt", "src/credentials.txt"),
            ("cat path/to/secret-prod.txt", "path/to/secret-prod.txt"),
        ]:
            with self.subTest(command=command):
                result = self.run_hook({
                    "tool_name": "Bash",
                    "tool_input": {"command": command},
                })

                self.assertEqual(result.returncode, 2)
                self.assertIn(blocked_path, result.stderr)

    def test_bash_warns_on_external_network_request(self):
        result = self.run_hook({
            "tool_name": "Bash",
            "tool_input": {"command": "curl https://example.com"},
        })

        self.assertEqual(result.returncode, 0)
        self.assertIn("SECURITY WARNING", result.stderr)


if __name__ == "__main__":
    unittest.main()
