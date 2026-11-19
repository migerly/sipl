import unittest
from cfg_explorer import explore

class GrammarTests(unittest.TestCase):
    def test_balanced(self):
        g = {'start':'S', 'rules':{'S':[['a','S','b'], []]}}
        result = explore(g, ['a','a','b','b'])
        self.assertEqual(result['results'][0]['derivation'],
                         [['S'], ['a','S','b'], ['a','a','S','b','b'], ['a','a','b','b']])
        self.assertEqual(explore(g, [])['results'][0]['derivation'], [['S'], []])

    def test_ambiguous(self):
        g = {'start':'S', 'rules':{'S':[['S','S'], ['a']]}}
        for direction in ('left', 'right'):
            result = explore(g, ['a','a','a'], direction, max_steps=5)
            self.assertEqual(len(result['results']), 2)
            self.assertNotEqual(result['results'][0]['tree'], result['results'][1]['tree'])

    def test_limit_not_nonmembership(self):
        g = {'start':'S', 'rules':{'S':[['a','S','b'], []]}}
        result = explore(g, ['a','a','b','b'], max_steps=1)
        self.assertEqual(result['results'], [])
        self.assertTrue(result['truncated'])

if __name__ == '__main__':
    unittest.main()
