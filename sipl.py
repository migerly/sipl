"""Єдиний командний інтерфейс SIPL: parse, check, run, trace."""
import argparse
import json
import re
import sys
from pathlib import Path
from lark import UnexpectedInput
from check import parse_ast
from interpreter import Interpreter, RuntimeErrorSIPL
from sipl_ast import ast_to_dict


def initial_variables(values):
    state = {}
    for item in values:
        match = re.fullmatch(r'([A-Za-z_][A-Za-z_0-9]*)=(-?[0-9]+)', item)
        if not match:
            raise ValueError('Потрібен запис NAME=VALUE, наприклад x=2')
        state[match.group(1)] = int(match.group(2))
    return state


def main():
    parser = argparse.ArgumentParser(description='Інструменти мови SIPL')
    subcommands = parser.add_subparsers(dest='command', required=True)
    for command in ('parse', 'check', 'run', 'trace'):
        sub = subcommands.add_parser(command)
        sub.add_argument('file', help='Файл програми SIPL')
        sub.add_argument('--json', action='store_true', help='Результат у JSON')
        if command in ('run', 'trace'):
            sub.add_argument('--var', action='append', default=[], metavar='NAME=VALUE')
            sub.add_argument('--max-steps', type=int, default=10000)
    args = parser.parse_args()
    machine = None
    try:
        source = Path(args.file).read_text(encoding='utf-8')
        program = parse_ast(source)
        result = {'schema_version': 1, 'status': 'ok', 'command': args.command}
        if args.command == 'parse':
            result['ast'] = ast_to_dict(program)
        elif args.command in ('run', 'trace'):
            machine = Interpreter(initial_variables(args.var), args.max_steps)
            result['state'] = machine.run(program)
            if args.command == 'trace':
                result['events'] = machine.events
    except (OSError, UnicodeError) as exc:
        result = {'schema_version': 1, 'status': 'error', 'command': args.command,
                  'error': {'kind': 'file', 'message': str(exc)}}
        code = 2
    except UnexpectedInput as exc:
        result = {'schema_version': 1, 'status': 'error', 'command': args.command,
                  'error': {'kind': 'syntax', 'line': exc.line, 'column': exc.column,
                            'message': 'Синтаксична помилка'}}
        code = 1
    except (RuntimeErrorSIPL, ValueError) as exc:
        result = {'schema_version': 1, 'status': 'error', 'command': args.command,
                  'error': {'kind': 'runtime', 'message': str(exc)}}
        if machine is not None and args.command == 'trace':
            result['events'] = machine.events
        code = 1
    else:
        code = 0
    if args.json or args.command == 'parse':
        print(json.dumps(result, ensure_ascii=True, indent=2))
    elif code:
        print(f"Помилка: {result['error']['message']}", file=sys.stderr)
    elif args.command == 'check':
        print('Синтаксис правильний')
    else:
        if args.command == 'trace':
            for event in result['events']:
                print(json.dumps(event, ensure_ascii=True))
        print('Кінцевий стан змінних:')
        for name, value in sorted(result['state'].items()):
            print(f'{name} = {value}')
        if not result['state']:
            print('(порожній)')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
