from dataclasses import dataclass, replace, fields, is_dataclass
from typing import Union
from lark import Transformer, v_args

@dataclass(frozen=True)
class SourceSpan:
    line: int
    column: int
    end_line: int
    end_column: int
    start_pos: int
    end_pos: int

@dataclass(frozen=True)
class Number:
    value: int
    span: SourceSpan

@dataclass(frozen=True)
class Variable:
    name: str
    span: SourceSpan

@dataclass(frozen=True)
class Binary:
    operator: str
    left: 'Expression'
    right: 'Expression'
    span: SourceSpan

@dataclass(frozen=True)
class Negation:
    operand: 'Expression'
    span: SourceSpan

Expression = Union[Number, Variable, Binary, Negation]

@dataclass(frozen=True)
class Assign:
    name: str
    expression: Expression
    span: SourceSpan

@dataclass(frozen=True)
class Skip:
    span: SourceSpan

@dataclass(frozen=True)
class Sequence:
    statements: list['Statement']
    span: SourceSpan

@dataclass(frozen=True)
class Block:
    statement: 'Statement'
    span: SourceSpan

@dataclass(frozen=True)
class If:
    condition: Expression
    then_branch: 'Statement'
    else_branch: 'Statement'
    span: SourceSpan

@dataclass(frozen=True)
class While:
    condition: Expression
    body: 'Statement'
    span: SourceSpan

Statement = Union[Assign, Skip, Sequence, Block, If, While]

@dataclass(frozen=True)
class Program:
    statement: Statement
    span: SourceSpan

def span(meta):
    return SourceSpan(meta.line, meta.column, meta.end_line, meta.end_column,
                      meta.start_pos, meta.end_pos)

@v_args(meta=True)
class ASTBuilder(Transformer):
    def program(self, meta, c): return Program(c[0], span(meta))
    def sequence(self, meta, c): return Sequence(c, span(meta))
    def assign(self, meta, c): return Assign(str(c[0]), c[1], span(meta))
    def skip(self, meta, c): return Skip(span(meta))
    def block(self, meta, c): return Block(c[0], span(meta))
    def if_stmt(self, meta, c): return If(*c, span(meta))
    def while_stmt(self, meta, c): return While(*c, span(meta))
    def number(self, meta, c): return Number(int(c[0]), span(meta))
    def negative_number(self, meta, c): return Number(-int(c[0]), span(meta))
    def variable(self, meta, c): return Variable(str(c[0]), span(meta))
    def grouped_expr(self, meta, c): return replace(c[0], span=span(meta))
    def grouped_condition(self, meta, c): return replace(c[0], span=span(meta))
    def negate(self, meta, c): return Negation(c[-1], span(meta))
    def add(self, meta, c): return Binary('+', c[0], c[1], span(meta))
    def sub(self, meta, c): return Binary('-', c[0], c[1], span(meta))
    def mul(self, meta, c): return Binary('*', c[0], c[1], span(meta))
    def equals(self, meta, c): return Binary('=', c[0], c[1], span(meta))
    def greater(self, meta, c): return Binary('>', c[0], c[1], span(meta))
    def disjunction(self, meta, c): return Binary('∨', c[0], c[-1], span(meta))

def ast_to_dict(node):
    if is_dataclass(node):
        return {'type': type(node).__name__, **{
            f.name: ast_to_dict(getattr(node, f.name)) for f in fields(node)}}
    if isinstance(node, list):
        return [ast_to_dict(item) for item in node]
    return node
