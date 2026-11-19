"""Запуск: py run.py example.sipl --var x=2 --max-steps 10000"""
import argparse
import json
import re
from pathlib import Path
from lark import UnexpectedInput
from check import parse_ast
from interpreter import Interpreter, RuntimeErrorSIPL


def main():
    cli = argparse.ArgumentParser(description='Виконання програми SIPL')
    cli.add_argument('file', help='Файл із програмою SIPL')
    cli.add_argument('--var', action='append', default=[], metavar='NAME=VALUE',
                     help='Початкове значення змінної; можна вказати кілька разів')
    cli.add_argument('--max-steps', type=int, default=10000, help='Ліміт кроків')
    cli.add_argument('--trace', action='store_true', help='Показати події виконання')
    cli.add_argument('--json', action='store_true', help='Вивести результат і події у JSON')
    args = cli.parse_args()
    initial = {}
    for item in args.var:
        match = re.fullmatch(r'([A-Za-z_][A-Za-z_0-9]*)=(-?[0-9]+)', item)
        if not match:
            cli.error('Очікується --var NAME=VALUE, наприклад --var x=2')
        initial[match.group(1)] = int(match.group(2))
    try:
        source = Path(args.file).read_text(encoding='utf-8')
        machine = Interpreter(initial, args.max_steps)
        result = machine.run(parse_ast(source))
    except (OSError, UnicodeError) as exc:
        print(f'Помилка читання файлу: {exc}')
        return 2
    except UnexpectedInput as exc:
        print(f'Синтаксична помилка: рядок {exc.line}, позиція {exc.column}')
        return 1
    except (RuntimeErrorSIPL, ValueError) as exc:
        if args.json:
            print(json.dumps({'status': 'error', 'message': str(exc),
                              'events': getattr(locals().get('machine'), 'events', [])},
                             ensure_ascii=True, indent=2))
        else:
            if args.trace and 'machine' in locals():
                for event in machine.events:
                    print(json.dumps(event, ensure_ascii=True))
            print(f'Помилка виконання: {exc}')
        return 1
    if args.json:
        print(json.dumps({'status': 'ok', 'state': result, 'events': machine.events},
                         ensure_ascii=True, indent=2))
        return 0
    if args.trace:
        for event in machine.events:
            print(json.dumps(event, ensure_ascii=True))
    print('Кінцевий стан змінних:')
    if not result:
        print('(порожній)')
    for name, value in sorted(result.items()):
        print(f'{name} = {value}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
