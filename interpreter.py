"""Виконання дерева SIPL зі станом змінних та обмеженням кроків."""
from sipl_ast import (Program, Assign, Skip, Sequence, Block, If, While,
                      Number, Variable, Binary, Negation)
from dataclasses import asdict


class RuntimeErrorSIPL(Exception):
    pass


class Interpreter:
    def __init__(self, initial_state=None, max_steps=10000):
        if max_steps < 1:
            raise ValueError('Ліміт кроків має бути додатним')
        self.state = dict(initial_state or {})
        self.max_steps = max_steps
        self.steps = 0
        self.events = []

    def emit(self, event_type, node=None, **details):
        event = {'event': event_type, 'step': self.steps,
                 'state': dict(self.state)}
        if node is not None:
            event['node'] = type(node).__name__
            event['span'] = asdict(node.span)
        event.update(details)
        self.events.append(event)

    def tick(self, node):
        if self.steps >= self.max_steps:
            raise RuntimeErrorSIPL(
                f'Перевищено ліміт {self.max_steps} кроків '
                f'(рядок {node.span.line}, позиція {node.span.column})')
        self.steps += 1

    def evaluate(self, node):
        if isinstance(node, Number):
            return node.value
        if isinstance(node, Variable):
            if node.name not in self.state:
                raise RuntimeErrorSIPL(
                    f'Змінна {node.name} не має значення '
                    f'(рядок {node.span.line}, позиція {node.span.column})')
            return self.state[node.name]
        if isinstance(node, Negation):
            return not self.evaluate(node.operand)
        if isinstance(node, Binary):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            if node.operator == '+': return left + right
            if node.operator == '-': return left - right
            if node.operator == '*': return left * right
            if node.operator == '=': return left == right
            if node.operator == '>': return left > right
            if node.operator == '∨': return left or right
        raise RuntimeErrorSIPL('Невідомий арифметичний або логічний вираз')

    def execute(self, node):
        if not isinstance(node, Program):
            self.emit('before_statement', node)
        self._execute(node)
        if not isinstance(node, Program):
            self.emit('after_statement', node)

    def _execute(self, node):
        if isinstance(node, Program):
            self.execute(node.statement)
        elif isinstance(node, Sequence):
            for statement in node.statements:
                self.execute(statement)
        elif isinstance(node, Block):
            self.execute(node.statement)
        elif isinstance(node, Assign):
            self.tick(node)
            value = self.evaluate(node.expression)
            old_value = self.state.get(node.name)
            existed = node.name in self.state
            self.state[node.name] = value
            self.emit('variable_changed', node, name=node.name, old_value=old_value,
                      previously_defined=existed, new_value=value)
        elif isinstance(node, Skip):
            self.tick(node)
        elif isinstance(node, If):
            self.tick(node)
            condition = self.evaluate(node.condition)
            self.emit('condition_checked', node.condition, result=condition)
            branch = node.then_branch if condition else node.else_branch
            self.execute(branch)
        elif isinstance(node, While):
            while True:
                self.tick(node)
                condition = self.evaluate(node.condition)
                self.emit('condition_checked', node.condition, result=condition)
                if not condition:
                    break
                self.execute(node.body)
        else:
            raise RuntimeErrorSIPL('Невідомий оператор')

    def run(self, program):
        try:
            self.execute(program)
        except RuntimeErrorSIPL as exc:
            self.emit('error', message=str(exc))
            raise
        self.emit('completed', program)
        return dict(self.state)
