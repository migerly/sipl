import json
import subprocess
import sys
import unittest
from pathlib import Path
from check import parse_ast
from interpreter import Interpreter, RuntimeErrorSIPL

class TraceTests(unittest.TestCase):
    def test_events_and_state_snapshots(self):
        machine = Interpreter()
        machine.run(parse_ast('begin x := 1; x := x + 1 end'))
        changes = [e for e in machine.events if e['event'] == 'variable_changed']
        self.assertEqual([e['new_value'] for e in changes], [1, 2])
        self.assertEqual(changes[0]['state']['x'], 1)
        self.assertFalse(changes[0]['previously_defined'])
        self.assertEqual(changes[1]['old_value'], 1)
        self.assertEqual(machine.events[-1]['event'], 'completed')
        self.assertTrue(any(e['event'] == 'before_statement' for e in machine.events))
        self.assertTrue(any(e['event'] == 'after_statement' for e in machine.events))

    def test_loop_condition_and_error(self):
        machine = Interpreter(max_steps=3)
        with self.assertRaises(RuntimeErrorSIPL):
            machine.run(parse_ast('begin while 1 > 0 do skip end'))
        self.assertTrue(any(e['event'] == 'condition_checked' and e['result']
                            for e in machine.events))
        self.assertEqual(machine.events[-1]['event'], 'error')

    def test_cli_json(self):
        folder = Path(__file__).parent
        result = subprocess.run([sys.executable, str(folder / 'run.py'),
                                 str(folder / 'example.sipl'), '--json'],
                                capture_output=True, text=True, check=True)
        output = json.loads(result.stdout)
        self.assertEqual(output['state'], {'x': 2, 'y': 5})
        self.assertEqual(output['events'][-1]['event'], 'completed')

if __name__ == '__main__':
    unittest.main()
