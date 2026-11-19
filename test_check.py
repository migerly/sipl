import unittest
from lark import UnexpectedInput
from check import check

VALID = [
    'begin skip end',
    'begin x := 2 end',
    'begin x := -2 end',
    'begin x := 2; y := x + 3 end',
    'begin x := (2 + 3) * 4 end',
    'begin if x > 0 then y := 1 else y := 0 end',
    'begin while x > 0 do x := x - 1 end',
    'begin begin x := 1; y := 2 end end',
    'begin if ¬(x = 0) then skip else x := 1 end',
    'begin if x = 0 ∨ y > 1 then skip else skip end',
    'begin while x > 0 do begin x := x - 1; y := y + 1 end end',
]
INVALID = [
    '', 'skip', 'begin end', 'begin x := 2', 'x := 2 end',
    'begin := x 2 end', 'begin x := end', 'begin x := 1; end',
    'begin if x > 0 then skip end', 'begin while x > 0 skip end',
    'begin x := 2 / 3 end', 'begin x := 1 y := 2 end',
    'begin skipend', 'begin while1 = 1 do skip end',
]

class GrammarTests(unittest.TestCase):
    def test_valid(self):
        for source in VALID:
            with self.subTest(source=source):
                check(source)

    def test_invalid(self):
        for source in INVALID:
            with self.subTest(source=source):
                with self.assertRaises(UnexpectedInput):
                    check(source)

if __name__ == '__main__':
    unittest.main()
