"""Дерево конкретного розбору SIPL: текст, JSON або DOT."""
import argparse
import json
import sys
from pathlib import Path
from lark import Lark, Tree, Token, UnexpectedInput
from check import GRAMMAR

def parse_tree(source):
    parser = Lark(GRAMMAR, parser='earley', lexer='dynamic', ambiguity='resolve',
                  propagate_positions=True, keep_all_tokens=True)
    return parser.parse(source)

def tree_data(node, source):
    if isinstance(node, Token):
        start, end = node.start_pos, node.end_pos
        return {'kind':'token', 'label':node.type, 'text':str(node),
                'start':start, 'end':end, 'line':node.line, 'column':node.column,
                'children':[]}
    start, end = node.meta.start_pos, node.meta.end_pos
    return {'kind':'rule', 'label':str(node.data), 'text':source[start:end],
            'start':start, 'end':end, 'line':node.meta.line, 'column':node.meta.column,
            'children':[tree_data(child, source) for child in node.children]}

def to_text(node, depth=0):
    text = f"{'  ' * depth}{node['label']} [{node['line']}:{node['column']}] {node['text']!r}"
    return '\n'.join([text] + [to_text(c, depth+1) for c in node['children']])

def to_dot(root):
    lines = ['digraph SIPL {', '  node [shape=box];']
    def visit(node):
        index = len(ids)
        ids.append(index)
        label = node['label'] + '\\n' + node['text'] + f"\\n{node['line']}:{node['column']}"
        lines.append(f'  n{index} [label={json.dumps(label, ensure_ascii=True)}];')
        for child in node['children']:
            child_id = visit(child)
            lines.append(f'  n{index} -> n{child_id};')
        return index
    ids = []
    visit(root)
    lines.append('}')
    return '\n'.join(lines)

def main():
    cli = argparse.ArgumentParser(description='Візуалізація дерева розбору SIPL')
    cli.add_argument('file')
    cli.add_argument('--format', choices=['text','json','dot'], default='text')
    cli.add_argument('--output', help='Зберегти результат у файл UTF-8')
    args = cli.parse_args()
    try:
        source = Path(args.file).read_text(encoding='utf-8')
        root = tree_data(parse_tree(source), source)
        if args.format == 'json':
            result = json.dumps(root, ensure_ascii=True, indent=2)
        elif args.format == 'dot':
            result = to_dot(root)
        else:
            result = to_text(root)
        if args.output:
            Path(args.output).write_text(result + '\n', encoding='utf-8')
            print('Результат збережено:', args.output)
        else:
            print(result)
    except (OSError, UnicodeError) as exc:
        print(f'Помилка файлу: {exc}', file=sys.stderr)
        return 2
    except UnexpectedInput as exc:
        print(f'Синтаксична помилка: рядок {exc.line}, позиція {exc.column}', file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
