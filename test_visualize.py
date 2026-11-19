import unittest
from visualize import parse_tree, tree_data, to_text, to_dot

class VisualizeTests(unittest.TestCase):
    def test_source_positions_and_tokens(self):
        source = 'begin x := 2 + 3 end'
        root = tree_data(parse_tree(source), source)
        self.assertEqual(root['text'], source)
        nodes = []
        def visit(n):
            nodes.append(n)
            for child in n['children']: visit(child)
        visit(root)
        for node in nodes:
            self.assertEqual(source[node['start']:node['end']], node['text'])
        self.assertTrue(any(n['text'] == 'begin' for n in nodes))
        self.assertTrue(any(n['text'] == '+' for n in nodes))
        self.assertIn('program', to_text(root))
        self.assertIn('digraph SIPL', to_dot(root))

if __name__ == '__main__':
    unittest.main()
