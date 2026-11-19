"""Перевірка незалежних прикладів через публічний JSON-інтерфейс CLI."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def without_spans(value):
    if isinstance(value, dict):
        return {k: without_spans(v) for k, v in value.items() if k != 'span'}
    if isinstance(value, list):
        return [without_spans(v) for v in value]
    return value

def main():
    suite = json.loads((ROOT / 'conformance.json').read_text(encoding='utf-8'))
    if suite.get('format_version') != 1:
        raise ValueError('Невідома версія формату тестів')
    failed = 0
    with tempfile.TemporaryDirectory() as folder:
        file = Path(folder) / 'program.sipl'
        for case in suite['cases']:
            file.write_text(case['source'], encoding='utf-8')
            command = [sys.executable, str(ROOT / 'sipl.py'), 'run', str(file), '--json',
                       '--max-steps', str(case.get('max_steps', 10000))]
            for name, value in case.get('initial', {}).items():
                command.extend(['--var', f'{name}={value}'])
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
            expected = case['expect']
            try:
                actual = json.loads(result.stdout)
                success = actual['status'] == expected['status']
                if expected['status'] == 'ok':
                    success = success and result.returncode == 0 and actual['state'] == expected['state']
                    if 'ast' in expected:
                        parsed = subprocess.run([sys.executable, str(ROOT / 'sipl.py'), 'parse',
                                                 str(file), '--json'], capture_output=True,
                                                text=True, encoding='utf-8')
                        actual_ast = json.loads(parsed.stdout)['ast']
                        success = success and parsed.returncode == 0 and without_spans(actual_ast) == expected['ast']
                else:
                    success = success and result.returncode != 0 and actual['error']['kind'] == expected['kind']
                    if 'message_contains' in expected:
                        success = success and expected['message_contains'] in actual['error']['message']
            except (ValueError, KeyError, TypeError):
                success = False
            print(('OK' if success else 'FAIL') + '  ' + case['id'])
            if not success:
                failed += 1
                print('  stdout:', result.stdout, 'stderr:', result.stderr)
    print(f'Пройдено: {len(suite["cases"]) - failed} / {len(suite["cases"])}')
    return 1 if failed else 0

if __name__ == '__main__':
    raise SystemExit(main())
