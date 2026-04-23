from dataclasses import dataclass, field
from typing import List

# simple classes to store information. Type checking is not really needed for the CFG.

@dataclass
class Node:
    line: int = 0

    def str(self, n):
        return f'{n*" "}#{self.line}\n'

@dataclass
class Program(Node):
    classes: List = field(default_factory=list)

@dataclass
class Class(Node):
    name: str = ''
    methods: List = field(default_factory=list)

@dataclass
class Method(Node):
    name: str = ''
    params: List = field(default_factory=list)
    body: List = field(default_factory=list)

@dataclass
class If(Node):
    condition: object = None
    true: List = field(default_factory=list)
    false: List = field(default_factory=list)

@dataclass
class While(Node):
    condition: object = None
    body: List = field(default_factory=list)

@dataclass
class For(Node):
    initialization: object = None
    condition: object = None
    update: object = None
    body: List = field(default_factory=list)

@dataclass
class Switch(Node):
    condition: object = None
    cases: List = field(default_factory=list)

@dataclass
class Case(Node):
    value: object = None
    body: List = field(default_factory=list)

@dataclass
class Try(Node):
    body: List = field(default_factory=list)
    catch: List = field(default_factory=list)
    finally_do: List = field(default_factory=list)

@dataclass
class Catch(Node):
    exception: str = ''
    variable: str = ''
    body: List = field(default_factory=list)

@dataclass
class Return(Node):
    value: object = None