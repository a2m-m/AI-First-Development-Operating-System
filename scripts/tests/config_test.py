import unittest
import os
import sys

# Add scripts/lib to path so config can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))
import config

TEST_YAML = """# This is a comment
project:
  name: "MyProject"
  owner: 'MyOwner'
  description: A project without quotes # inline comment
  
runtime:
  mode: docker
  docker_image: "alpine"
  host_setup_steps: ["step1", 'step2', step3]

commands:
  lint: "echo 'skip'"  # Should keep echo 'skip' intact
  typecheck: ""
  test: mypy .
  
features:
  ci: true
  lcg: false
  
policy:
  max_diff_warning: 1200
"""

class TestConfig(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.fd, self.path = tempfile.mkstemp(suffix=".yml")
        with os.fdopen(self.fd, "w", encoding="utf-8") as f:
            f.write(TEST_YAML)

    def tearDown(self):
        os.remove(self.path)

    def test_load_config(self):
        cfg = config.load_config(self.path)
        
        # Test basic parsing and quote stripping
        self.assertEqual(cfg['project']['name'], 'MyProject')
        self.assertEqual(cfg['project']['owner'], 'MyOwner')
        self.assertEqual(cfg['project']['description'], 'A project without quotes')
        
        # Test arrays
        self.assertEqual(cfg['runtime']['mode'], 'docker')
        self.assertEqual(cfg['runtime']['host_setup_steps'], ['step1', 'step2', 'step3'])
        
        # Test preserving inner quotes
        self.assertEqual(cfg['commands']['lint'], "echo 'skip'")
        self.assertEqual(cfg['commands']['typecheck'], "")
        
        # Test booleans and ints
        self.assertEqual(cfg['features']['ci'], True)
        self.assertEqual(cfg['features']['lcg'], False)
        self.assertEqual(cfg['policy']['max_diff_warning'], 1200)

    def test_get_value(self):
        self.assertEqual(config.get_value(self.path, 'project.name'), 'MyProject')
        self.assertEqual(config.get_value(self.path, 'policy.max_diff_warning'), 1200)
        self.assertEqual(config.get_value(self.path, 'nonexistent.key'), None)
        self.assertEqual(config.get_value(self.path, 'project.nonexistent'), None)

    def test_real_os_template(self):
        # Smoke test actual os-template.yml
        real_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'os-template.yml'))
        if os.path.exists(real_path):
            cfg = config.load_config(real_path)
            self.assertIsInstance(cfg['project']['name'], str)
            self.assertEqual(cfg['project']['name'], 'YOUR_PROJECT_NAME')
            self.assertEqual(cfg['runtime']['mode'], 'docker')
            self.assertEqual(cfg['runtime']['docker_image'], 'your-image:tag')
            self.assertEqual(cfg['runtime']['host_setup_steps'], [])
            self.assertEqual(cfg['commands']['lint'], "echo 'skip'")
            self.assertEqual(cfg['policy']['max_diff_warning'], 1200)
        else:
            self.skipTest("os-template.yml not found, skipping real file test")

if __name__ == '__main__':
    unittest.main()
