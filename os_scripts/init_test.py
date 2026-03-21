#!/usr/bin/env python3

import unittest
import os
import tempfile
import importlib.util
import importlib.machinery
from unittest.mock import patch, MagicMock

# Mock FIXTURES ensuring tests are decoupled from changing repo files
MOCK_OS_TEMPLATE = """schema_version: "1"
project:
  name: "YOUR_PROJECT_NAME"
  owner: "YOUR_TEAM_OR_OWNER"
  description: ""
runtime:
  mode: "docker"
  docker_image: ""
"""

MOCK_README = """# Template Repo

> **YOUR_PROJECT_NAME** — YOUR_TEAM_OR_OWNER

## 2. Quickstart
./os_scripts/init \\
  --project-name YOUR_PROJECT_NAME \\
  --owner YOUR_TEAM_OR_OWNER
"""

MOCK_AI_CONTEXT = """# .ai-context.md
## 1. Status

| 項目 | 状態 |
|---|---|
| 全体 | `TODO: works / broken` |
| 補足 | `TODO: 状態の補足（例：CI緑、テスト未整備、etc.）` |

## 6. Commands
<!-- TODO: プロジェクトで使用するコマンドを記載する。project_config.yml の commands.* と対応させる -->
"""

class TestInitScript(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
        # Write isolated fixtures
        self.config_file = os.path.join(self.temp_dir, "project_config.yml")
        self.readme_file = os.path.join(self.temp_dir, "README.md")
        self.ai_context_file = os.path.join(self.temp_dir, ".ai-context.md")
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            f.write(MOCK_OS_TEMPLATE)
        with open(self.readme_file, 'w', encoding='utf-8') as f:
            f.write(MOCK_README)
        with open(self.ai_context_file, 'w', encoding='utf-8') as f:
            f.write(MOCK_AI_CONTEXT)
        
        # Load the init script module dynamically
        repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        loader = importlib.machinery.SourceFileLoader('init_module', os.path.join(repo_dir, 'os_scripts', 'init'))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        self.init_module = importlib.util.module_from_spec(spec)
        loader.exec_module(self.init_module)

        # Patch the file paths in the module
        self.init_module.CONFIG_FILE = self.config_file
        self.init_module.README_FILE = self.readme_file
        self.init_module.AI_CONTEXT_FILE = self.ai_context_file

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    @patch('sys.argv', ['init', '--project-name', 'TestApp\\Backslash"Quote', '--owner', 'testuser', '--description', 'my desc', '--runtime-mode', 'docker', '--docker-image', 'alpine:latest'])
    def test_normal_execution_with_escaping(self):
        with patch('sys.stdout', new_callable=MagicMock):
            self.init_module.main()
            
        with open(self.init_module.CONFIG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            # Escaping checks
            self.assertIn('name: "TestApp\\\\Backslash\\"Quote"', content)
            self.assertIn('owner: "testuser"', content)
            self.assertNotIn('YOUR_PROJECT_NAME', content)
            self.assertIn('docker_image: "alpine:latest"', content)
            self.assertIn('description: "my desc"', content)
            
        with open(self.init_module.README_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            # Ensures header was replaced
            self.assertIn('> **TestApp\\Backslash"Quote** — testuser', content)
            # Ensures Quickstart block wasn't replaced
            self.assertIn('--project-name YOUR_PROJECT_NAME', content)
            
        with open(self.init_module.AI_CONTEXT_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('| 全体 | `works` |', content)
            self.assertIn('INSTRUCTOR NOTE: os_scripts/init 経由で初期化されました', content)

    @patch('sys.argv', ['init', '--project-name', 'TestApp', '--owner', 'testuser', '--runtime-mode', 'docker'])
    def test_missing_docker_image(self):
        with patch('sys.stdout', new_callable=MagicMock):
            with self.assertRaises(SystemExit) as cm:
                self.init_module.main()
            self.assertEqual(cm.exception.code, 1)

    @patch('sys.argv', ['init', '--project-name', 'TestApp2', '--owner', 'testuser', '--runtime-mode', 'host'])
    def test_idempotency_and_force(self):
        with patch('sys.stdout', new_callable=MagicMock):
            self.init_module.main()
            
        # Try running again without force should fail
        with patch('sys.stdout', new_callable=MagicMock):
            with self.assertRaises(SystemExit) as cm:
                self.init_module.main()
            self.assertEqual(cm.exception.code, 1)

        # Try running again with force and NEW values
        with patch('sys.argv', ['init', '--project-name', 'ForcedApp', '--owner', 'testuser', '--runtime-mode', 'host', '--force']):
            with patch('sys.stdout', new_callable=MagicMock):
                try:
                    self.init_module.main()
                except SystemExit:
                    self.fail("main() raised SystemExit unexpectedly with --force!")
                    
        with open(self.init_module.CONFIG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            # Verify the file was actually updated
            self.assertIn('name: "ForcedApp"', content)

    @patch('builtins.input', side_effect=['InteractiveApp', 'owner', '', 'host'])
    def test_interactive_mode(self, mock_input):
        with patch('sys.argv', ['init']):
            with patch('sys.stdout', new_callable=MagicMock):
                self.init_module.main()
                
        with open(self.init_module.CONFIG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('name: "InteractiveApp"', content)
            self.assertIn('mode: "host"', content)

if __name__ == '__main__':
    unittest.main()
