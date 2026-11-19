from pathlib import Path
import argparse
import json
from lark import Lark, UnexpectedInput
from sipl_ast import ASTBuilder, ast_to_dict

GRAMMAR = Path(__file__).with_name('sipl.lark').read_text(encoding='utf-8')
parser = Lark(GRAMMAR, parser='earley', lexer='dynamic', ambiguity='resolve', propagate_positions=True)

def check(source):
    return parser.parse(source)

def parse_ast(source):
    return ASTBuilder().transform(check(source))

def main():
    cli = argparse.ArgumentParser(description='Перевірка синтаксису SIPL')
    cli.add_argument('file', help='Шлях до файлу з програмою SIPL')
    cli.add_argument('--ast', action='store_true', help='Вивести AST у форматі JSON')
    args = cli.parse_args()
    try:
        source = Path(args.file).read_text(encoding='utf-8')
        tree = parse_ast(source) if args.ast else check(source)
    except (OSError, UnicodeError) as exc:
        print(f'Помилка читання файлу: {exc}')
        return 2
    except UnexpectedInput as exc:
        print(f'Синтаксична помилка: рядок {exc.line}, позиція {exc.column}')
        return 1
    if args.ast:
        print(json.dumps(ast_to_dict(tree), ensure_ascii=False, indent=2))
    else:
        print('Синтаксис правильний')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
