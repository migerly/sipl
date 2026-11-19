import unittest
from pathlib import Path
from check import parse_ast
from interpreter import Interpreter

class ExampleTests(unittest.TestCase):
    def test_gcd(self):
        source = Path(__file__).with_name('gcd.sipl').read_text(encoding='utf-8')
        state = Interpreter({'M': 12, 'N': 8}).run(parse_ast(source))
        self.assertEqual(state, {'M': 4, 'N': 4})

if __name__ == '__main__':
    unittest.main()
