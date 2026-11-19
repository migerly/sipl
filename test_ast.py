import unittest
from check import parse_ast
from sipl_ast import Program, Assign, Number, Sequence, If, While

class ASTTests(unittest.TestCase):
    def test_precedence_and_positions(self):
        text = 'begin\n x := 2 + 3 * 4\nend'
        p = parse_ast(text)
        self.assertIsInstance(p, Program)
        self.assertIsInstance(p.statement, Assign)
        expression = p.statement.expression
        self.assertEqual(expression.operator, '+')
        self.assertEqual(expression.right.operator, '*')
        self.assertEqual((p.statement.span.line, p.statement.span.column), (2, 2))
        self.assertEqual(text[expression.span.start_pos:expression.span.end_pos], '2 + 3 * 4')

    def test_subtraction_associates_left(self):
        expr = parse_ast('begin x := 9-3-1 end').statement.expression
        self.assertEqual(expr.operator, '-')
        self.assertEqual(expr.left.operator, '-')
        self.assertEqual(expr.right.value, 1)

    def test_if_while_and_sequence(self):
        source = 'begin while x > 0 do begin x := x - 1; if x = 0 then skip else x := 1 end end'
        loop = parse_ast(source).statement
        self.assertIsInstance(loop, While)
        self.assertIsInstance(loop.body.statement, Sequence)
        self.assertIsInstance(loop.body.statement.statements[1], If)

    def test_negative(self):
        num = parse_ast('begin x := -2 end').statement.expression
        self.assertIsInstance(num, Number)
        self.assertEqual(num.value, -2)

if __name__ == '__main__':
    unittest.main()
