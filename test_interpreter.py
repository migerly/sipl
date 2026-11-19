import unittest
from check import parse_ast
from interpreter import Interpreter, RuntimeErrorSIPL

def run(source, state=None, limit=100):
    return Interpreter(state, limit).run(parse_ast(source))

class InterpreterTests(unittest.TestCase):
    def test_assign_and_arithmetic(self):
        self.assertEqual(run('begin x := 2; y := x + 3 * 4 end'), {'x': 2, 'y': 14})

    def test_loop_and_input(self):
        source = 'begin z := 0; k := y; while k > 0 do begin z := z + x; k := k - 1 end end'
        self.assertEqual(run(source, {'x': 2, 'y': 3}), {'x': 2, 'y': 3, 'z': 6, 'k': 0})

    def test_if_both_branches(self):
        source = 'begin if x > 0 then y := 1 else y := -1 end'
        self.assertEqual(run(source, {'x': 2})['y'], 1)
        self.assertEqual(run(source, {'x': 0})['y'], -1)

    def test_logic_and_skip(self):
        source = 'begin if ¬(x = 0) ∨ x > 5 then y := 7 else skip end'
        self.assertEqual(run(source, {'x': 1})['y'], 7)
        self.assertEqual(run(source, {'x': 0}), {'x': 0})

    def test_missing_variable(self):
        with self.assertRaisesRegex(RuntimeErrorSIPL, 'не має значення'):
            run('begin x := missing end')

    def test_infinite_loop(self):
        with self.assertRaisesRegex(RuntimeErrorSIPL, 'Перевищено ліміт'):
            run('begin x := 1; while x > 0 do skip end', limit=8)

    def test_input_not_mutated(self):
        initial = {'x': 2}
        self.assertEqual(run('begin x := x + 1 end', initial)['x'], 3)
        self.assertEqual(initial, {'x': 2})

if __name__ == '__main__':
    unittest.main()
