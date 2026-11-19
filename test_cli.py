import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent

def call(*arguments):
    return subprocess.run([sys.executable, str(ROOT / 'sipl.py'), *map(str, arguments)],
                          capture_output=True, text=True)

class CLITests(unittest.TestCase):
    def test_check_parse_run_trace(self):
        for command in ('check', 'parse', 'run', 'trace'):
            with self.subTest(command=command):
                result = call(command, ROOT / 'example.sipl', '--json')
                self.assertEqual(result.returncode, 0, result.stderr)
                data = json.loads(result.stdout)
                self.assertEqual(data['status'], 'ok')
                self.assertEqual(data['schema_version'], 1)
                if command == 'parse':
                    self.assertEqual(data['ast']['type'], 'Program')
                if command in ('run', 'trace'):
                    self.assertEqual(data['state']['y'], 5)
                if command == 'trace':
                    self.assertEqual(data['events'][-1]['event'], 'completed')

    def test_invalid_syntax_json(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'invalid.sipl'
            path.write_text('begin x := end', encoding='utf-8')
            result = call('check', path, '--json')
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)['error']['kind'], 'syntax')

    def test_missing_file_json(self):
        result = call('run', ROOT / 'nonexistent.sipl', '--json')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['error']['kind'], 'file')

if __name__ == '__main__':
    unittest.main()
