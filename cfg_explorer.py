"""Пошук виведень контекстно-вільної граматики в заданих межах."""
import argparse
import json
from collections import deque
from pathlib import Path

def validate(g):
    if not isinstance(g, dict) or not isinstance(g.get('rules'), dict):
        raise ValueError('Граматика має містити об’єкт rules')
    rules = g['rules']
    if not rules or g.get('start') not in rules:
        raise ValueError('Початковий символ має бути серед лівих частин правил')
    if any(not isinstance(k, str) or not k for k in rules):
        raise ValueError('Назви нетерміналів мають бути непорожніми рядками')
    for name, choices in rules.items():
        if not isinstance(choices, list) or not choices:
            raise ValueError(f'Для {name} потрібен список альтернатив')
        for choice in choices:
            if not isinstance(choice, list) or any(not isinstance(x, str) or not x for x in choice):
                raise ValueError('Альтернатива має бути списком непорожніх символів')
    return rules

def leaf(symbol):
    return {'symbol': symbol, 'children': None}

def leaves(tree, path=()):
    if tree['children'] is None:
        yield path, tree['symbol']
    else:
        for i, child in enumerate(tree['children']):
            yield from leaves(child, path + (i,))

def replace(tree, path, children):
    if not path:
        return {'symbol': tree['symbol'], 'children': children}
    copies = list(tree['children'])
    copies[path[0]] = replace(copies[path[0]], path[1:], children)
    return {'symbol': tree['symbol'], 'children': copies}

def explore(grammar, word, direction='left', max_steps=8, max_states=10000, max_trees=20):
    rules = validate(grammar)
    if direction not in ('left', 'right') or max_steps < 0 or max_states < 1 or max_trees < 1:
        raise ValueError('Неправильний напрям або межі пошуку')
    if not isinstance(word, list) or any(not isinstance(x, str) for x in word):
        raise ValueError('Слово задається JSON-списком термінальних символів')
    if any(x in rules for x in word):
        raise ValueError('Слово має містити лише термінали')
    root = leaf(grammar['start'])
    queue = deque([(root, [[grammar['start']]], 0)])
    results = []
    visited = 0
    truncated = False
    while queue:
        if visited >= max_states or len(results) >= max_trees:
            truncated = True
            break
        tree, history, steps = queue.popleft()
        visited += 1
        frontier = list(leaves(tree))
        nonterminals = [(path, sym) for path, sym in frontier if sym in rules]
        if not nonterminals:
            if [sym for _, sym in frontier] == word:
                results.append({'derivation': history, 'tree': tree})
            continue
        if steps == max_steps:
            truncated = True
            continue
        path, symbol = nonterminals[0 if direction == 'left' else -1]
        for alternative in rules[symbol]:
            new_tree = replace(tree, path, [leaf(x) for x in alternative])
            form = [sym for _, sym in leaves(new_tree)]
            queue.append((new_tree, history + [form], steps + 1))
    return {'direction':direction, 'max_steps':max_steps, 'visited':visited,
            'truncated':truncated, 'results':results}

def main():
    cli = argparse.ArgumentParser(description='Пошук виведень КВ-граматики')
    cli.add_argument('grammar', help='JSON-файл граматики')
    cli.add_argument('word', help='Слово з однобуквених терміналів або JSON-список')
    cli.add_argument('--direction', choices=['left', 'right'], default='left')
    cli.add_argument('--max-steps', type=int, default=8)
    cli.add_argument('--max-states', type=int, default=10000)
    cli.add_argument('--max-trees', type=int, default=20)
    cli.add_argument('--output', help='Файл для експорту результату JSON')
    args = cli.parse_args()
    try:
        grammar = json.loads(Path(args.grammar).read_text(encoding='utf-8'))
        word = json.loads(args.word) if args.word.startswith('[') else list(args.word)
        result = explore(grammar, word, args.direction, args.max_steps, args.max_states, args.max_trees)
        output = json.dumps(result, ensure_ascii=True, indent=2)
        if args.output:
            Path(args.output).write_text(output + '\n', encoding='utf-8')
            print('Результат збережено:', args.output)
        else:
            print(output)
        return 0
    except (ValueError, OSError) as exc:
        print('Помилка:', exc)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
