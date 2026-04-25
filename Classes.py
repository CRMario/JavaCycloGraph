from dataclasses import dataclass, field
from typing import List, Optional
from Scope import Scope, SemanticException


@dataclass
class Node:
    line: int = 0
    inferred_type: Optional[str] = field(default=None, init=False, repr=False)
    computed_value: object = field(default=None, init=False, repr=False)

    def Type(self, scope: Scope):
        raise NotImplementedError(f"Type() not implemented in {self.__class__.__name__}")

    def __str__(self):
        return self.__class__.__name__

@dataclass
class Program(Node):
    classes: List = field(default_factory=list)
    def Type(self, scope): pass

@dataclass
class Class(Node):
    name: str = ''
    methods: List = field(default_factory=list)
    def Type(self, scope): pass

@dataclass
class Method(Node):
    name: str = ''
    params: List = field(default_factory=list)
    body: List = field(default_factory=list)
    return_type: str = ''
    def Type(self, scope): pass

@dataclass
class Integer(Node):
    value: int = 0

    def Type(self, scope):
        self.inferred_type = 'int'
        self.computed_value = self.value
        return 'int'

    def __str__(self):
        return str(self.value)


@dataclass
class Float(Node):
    value: float = 0.0

    def Type(self, scope):
        self.inferred_type = 'float'
        self.computed_value = self.value
        return 'float'

    def __str__(self):
        return str(self.value)


@dataclass
class Bool(Node):
    value: bool = False

    def Type(self, scope):
        self.inferred_type = 'boolean'
        self.computed_value = self.value
        return 'boolean'

    def __str__(self):
        return str(self.value).lower()


@dataclass
class String(Node):
    value: str = ''

    def Type(self, scope):
        self.inferred_type = 'String'
        self.computed_value = self.value
        return 'String'

    def __str__(self):
        return f'"{self.value}"'


@dataclass
class NullLiteral(Node):
    def Type(self, scope):
        self.inferred_type = 'null'
        self.computed_value = None
        return 'null'

    def __str__(self):
        return 'null'


@dataclass
class This(Node):
    def Type(self, scope):
        self.inferred_type = scope.current_class or 'unknown'
        return self.inferred_type

    def __str__(self):
        return 'this'


@dataclass
class Identifier(Node):
    name: str = ''

    def Type(self, scope):
        var = scope.get_variable(self.name)
        if var is None:
            raise SemanticException(
                f'"{scope.filename}", line {self.line}: '
                f"Undeclared variable '{self.name}'"
            )
        self.inferred_type = var['type']
        self.computed_value = var['value']
        return self.inferred_type

    def __str__(self):
        return self.name


_NUMERIC = {'int', 'float'}

def _widen(t1, t2):
    """Return the wider of two numeric types. None if either is not numeric."""
    order = ['int', 'float']
    if t1 in order and t2 in order:
        return order[max(order.index(t1), order.index(t2))]
    return None

@dataclass
class BinaryOperation(Node):
    left: object = None
    right: object = None
    op: str = field(default='', init=False)

    def __str__(self):
        return f'{self.left} {self.op} {self.right}'

    def _tipo_numeric(self, scope):
        """Type-check both operands as numeric. Returns (lt, rt, wider)."""
        lt = self.left.Type(scope)
        rt = self.right.Type(scope)
        wider = _widen(lt, rt)
        if wider is None:
            raise SemanticException(
                f'"{scope.filename}", line {self.line}: '
                f"Operator '{self.op}' requires numeric operands, got {lt} and {rt}"
            )
        return lt, rt, wider

    def _tipo_boolean(self, scope):
        """Type-check both operands as boolean."""
        lt = self.left.Type(scope)
        rt = self.right.Type(scope)
        if lt != 'boolean' or rt != 'boolean':
            raise SemanticException(
                f'"{scope.filename}", line {self.line}: '
                f"Operator '{self.op}' requires boolean operands, got {lt} and {rt}"
            )
        return lt, rt


@dataclass
class AddOperation(BinaryOperation):
    op = '+'

    def Type(self, scope):
        lt = self.left.Type(scope)
        rt = self.right.Type(scope)
        # string concatenation
        if lt == 'String' or rt == 'String':
            self.inferred_type = 'String'
            lv, rv = self.left.computed_value, self.right.computed_value
            if lv is not None and rv is not None:
                self.computed_value = str(lv) + str(rv)
            return 'String'
        wider = _widen(lt, rt)
        if wider is None:
            raise SemanticException(
                f'"{scope.filename}", line {self.line}: '
                f"'+' requires numeric or String operands, got {lt} and {rt}"
            )
        self.inferred_type = wider
        lv, rv = self.left.computed_value, self.right.computed_value
        if lv is not None and rv is not None:
            self.computed_value = lv + rv
        return wider


@dataclass
class SubstractOperation(BinaryOperation):
    op = '-'

    def Type(self, scope):
        lt, rt, wider = self._tipo_numeric(scope)
        self.inferred_type = wider
        lv, rv = self.left.computed_value, self.right.computed_value
        if lv is not None and rv is not None:
            self.computed_value = lv - rv
        return wider


@dataclass
class MultOperation(BinaryOperation):
    op = '*'

    def Type(self, scope):
        lt, rt, wider = self._tipo_numeric(scope)
        self.inferred_type = wider
        lv, rv = self.left.computed_value, self.right.computed_value
        if lv is not None and rv is not None:
            self.computed_value = lv * rv
        return wider


@dataclass
class DivOperation(BinaryOperation):
    op = '/'

    def Type(self, scope):
        lt, rt, wider = self._tipo_numeric(scope)
        self.inferred_type = wider
        lv, rv = self.left.computed_value, self.right.computed_value
        if lv is not None and rv is not None:
            self.computed_value = lv / rv if rv != 0 else None
        return wider


@dataclass
class RemainderOperation(BinaryOperation):
    op = '%'

    def Type(self, scope):
        lt, rt, wider = self._tipo_numeric(scope)
        self.inferred_type = wider
        lv, rv = self.left.computed_value, self.right.computed_value
        if lv is not None and rv is not None:
            self.computed_value = lv % rv if rv != 0 else None
        return wider

@dataclass
class LEOperation(BinaryOperation):
    op = '<='

    def Type(self, scope):
        self._tipo_numeric(scope)
        self.inferred_type = 'boolean'
        lv, rv = self.left.computed_value, self.right.computed_value
        if lv is not None and rv is not None:
            self.computed_value = lv <= rv
        return 'boolean'


@dataclass
class GEOperation(BinaryOperation):
    op = '>='

    def Type(self, scope):
        self._tipo_numeric(scope)
        self.inferred_type = 'boolean'
        lv, rv = self.left.computed_value, self.right.computed_value
        if lv is not None and rv is not None:
            self.computed_value = lv >= rv
        return 'boolean'


@dataclass
class LTOperation(BinaryOperation):
    op = '<'

    def Type(self, scope):
        self._tipo_numeric(scope)
        self.inferred_type = 'boolean'
        lv, rv = self.left.computed_value, self.right.computed_value
        if lv is not None and rv is not None:
            self.computed_value = lv < rv
        return 'boolean'


@dataclass
class GTOperation(BinaryOperation):
    op = '>'

    def Type(self, scope):
        self._tipo_numeric(scope)
        self.inferred_type = 'boolean'
        lv, rv = self.left.computed_value, self.right.computed_value
        if lv is not None and rv is not None:
            self.computed_value = lv > rv
        return 'boolean'


@dataclass
class EQOperation(BinaryOperation):
    op = '=='

    def Type(self, scope):
        # == works on any type pair (int, float, String, null, objects)
        lt = self.left.Type(scope)
        rt = self.right.Type(scope)
        self.inferred_type = 'boolean'
        lv, rv = self.left.computed_value, self.right.computed_value
        if lv is not None and rv is not None:
            self.computed_value = lv == rv
        return 'boolean'


@dataclass
class NEOperation(BinaryOperation):
    op = '!='

    def Type(self, scope):
        lt = self.left.Type(scope)
        rt = self.right.Type(scope)
        self.inferred_type = 'boolean'
        lv, rv = self.left.computed_value, self.right.computed_value
        if lv is not None and rv is not None:
            self.computed_value = lv != rv
        return 'boolean'

@dataclass
class ANDOperation(BinaryOperation):
    op = '&&'

    def Type(self, scope):
        self._tipo_boolean(scope)
        self.inferred_type = 'boolean'
        lv, rv = self.left.computed_value, self.right.computed_value
        if lv is not None and rv is not None:
            self.computed_value = lv and rv
        return 'boolean'


@dataclass
class OROperation(BinaryOperation):
    op = '||'

    def Type(self, scope):
        self._tipo_boolean(scope)
        self.inferred_type = 'boolean'
        lv, rv = self.left.computed_value, self.right.computed_value
        if lv is not None and rv is not None:
            self.computed_value = lv or rv
        return 'boolean'


@dataclass
class BitwiseANDOperation(BinaryOperation):
    op = '&'

    def Type(self, scope):
        lt = self.left.Type(scope)
        rt = self.right.Type(scope)
        if lt != 'int' or rt != 'int':
            raise SemanticException(
                f'"{scope.filename}", line {self.line}: '
                f"'&' requires int operands, got {lt} and {rt}"
            )
        self.inferred_type = 'int'
        return 'int'


@dataclass
class BitwiseOROperation(BinaryOperation):
    op = '|'

    def Type(self, scope):
        lt = self.left.Type(scope)
        rt = self.right.Type(scope)
        if lt != 'int' or rt != 'int':
            raise SemanticException(
                f'"{scope.filename}", line {self.line}: '
                f"'|' requires int operands, got {lt} and {rt}"
            )
        self.inferred_type = 'int'
        return 'int'

@dataclass
class UnaryOperation(Node):
    operand: object = None
    op: str = field(default='', init=False)

    def __str__(self):
        return f'{self.op}{self.operand}'


@dataclass
class NotOp(UnaryOperation):
    op = '!'

    def Type(self, scope):
        t = self.operand.Type(scope)
        if t != 'boolean':
            raise SemanticException(
                f'"{scope.filename}", line {self.line}: '
                f"'!' requires boolean operand, got {t}"
            )
        self.inferred_type = 'boolean'
        v = self.operand.computed_value
        if v is not None:
            self.computed_value = not v
        return 'boolean'


@dataclass
class Increment(UnaryOperation):
    op = '++'

    def Type(self, scope):
        t = self.operand.Type(scope)
        if t != 'int':
            raise SemanticException(
                f'"{scope.filename}", line {self.line}: '
                f"'++' requires int operand, got {t}"
            )
        self.inferred_type = 'int'
        return 'int'

    def __str__(self):
        return f'{self.operand}++'


@dataclass
class Decrement(UnaryOperation):
    op = '--'

    def Type(self, scope):
        t = self.operand.Type(scope)
        if t != 'int':
            raise SemanticException(
                f'"{scope.filename}", line {self.line}: '
                f"'--' requires int operand, got {t}"
            )
        self.inferred_type = 'int'
        return 'int'

    def __str__(self):
        return f'{self.operand}--'

@dataclass
class Assignment(Node):
    name: str = ''
    value: object = None

    def Type(self, scope):
        vt = self.value.Type(scope)
        var = scope.get_variable(self.name)
        if var is None:
            raise SemanticException(
                f'"{scope.filename}", line {self.line}: '
                f"Undeclared variable '{self.name}'"
            )
        declared = var['type']
        if not scope.conforms(vt, declared):
            raise SemanticException(
                f'"{scope.filename}", line {self.line}: '
                f"Cannot assign {vt} to '{self.name}' of type {declared}"
            )
        # update value in scope so later references see the new value
        for frame in reversed(scope.stack):
            if self.name in frame:
                frame[self.name]['value'] = self.value.computed_value
                break
        self.inferred_type = declared
        self.computed_value = self.value.computed_value
        return declared

    def __str__(self):
        return f'{self.name} = {self.value}'

@dataclass
class VarDecl(Node):
    var_type: str = ''
    name: str = ''
    value: object = None

    def Type(self, scope):
        if self.value is not None:
            vt = self.value.Type(scope)
            if not scope.conforms(vt, self.var_type):
                raise SemanticException(
                    f'"{scope.filename}", line {self.line}: '
                    f"Type {vt} does not conform to declared type {self.var_type} "
                    f"for '{self.name}'"
                )
            computed = self.value.computed_value
        else:
            computed = None
        scope.add_variable(self.name, self.var_type, computed)
        self.inferred_type = self.var_type
        self.computed_value = computed
        return self.var_type

    def __str__(self):
        if self.value is not None:
            return f'{self.var_type} {self.name} = {self.value}'
        return f'{self.var_type} {self.name}'

@dataclass
class MethodCall(Node):
    obj: object = None
    method: str = ''
    args: List = field(default_factory=list)

    def Type(self, scope):
        if self.obj is not None and hasattr(self.obj, 'Type'):
            self.obj.Type(scope)
        for arg in self.args:
            if hasattr(arg, 'Type'):
                arg.Type(scope)
        self.inferred_type = 'unknown'
        return 'unknown'

    def __str__(self):
        args = ', '.join(str(a) for a in self.args)
        if self.obj is not None:
            return f'{self.obj}.{self.method}({args})'
        return f'{self.method}({args})'


@dataclass
class FieldAccess(Node):
    obj: object = None
    field: str = ''

    def Type(self, scope):
        if hasattr(self.obj, 'Type'):
            self.obj.Type(scope)
        self.inferred_type = 'unknown'
        return 'unknown'

    def __str__(self):
        return f'{self.obj}.{self.field}'


@dataclass
class ArrayAccess(Node):
    array: object = None
    index: object = None

    def Type(self, scope):
        at = self.array.Type(scope)
        it = self.index.Type(scope)
        if it != 'int':
            raise SemanticException(
                f'"{scope.filename}", line {self.line}: '
                f'Array index must be int, got {it}'
            )
        self.inferred_type = at[:-2] if at.endswith('[]') else 'unknown'
        return self.inferred_type

    def __str__(self):
        return f'{self.array}[{self.index}]'


@dataclass
class Cast(Node):
    cast_type: str = ''
    expr: object = None

    def Type(self, scope):
        self.expr.Type(scope)
        self.inferred_type = self.cast_type
        self.computed_value = self.expr.computed_value
        return self.cast_type

    def __str__(self):
        return f'({self.cast_type}){self.expr}'


@dataclass
class NewObject(Node):
    class_name: str = ''
    args: List = field(default_factory=list)

    def Type(self, scope):
        for arg in self.args:
            if hasattr(arg, 'Type'):
                arg.Type(scope)
        self.inferred_type = self.class_name
        return self.class_name

    def __str__(self):
        args = ', '.join(str(a) for a in self.args)
        return f'new {self.class_name}({args})'


@dataclass
class NewArray(Node):
    element_type: str = ''
    size: object = None

    def Type(self, scope):
        st = self.size.Type(scope)
        if st != 'int':
            raise SemanticException(
                f'"{scope.filename}", line {self.line}: '
                f'Array size must be int, got {st}'
            )
        self.inferred_type = f'{self.element_type}[]'
        return self.inferred_type

    def __str__(self):
        return f'new {self.element_type}[{self.size}]'

@dataclass
class Ternary(Node):
    condition: object = None
    true: object = None
    false: object = None

    def Type(self, scope):
        ct = self.condition.Type(scope)
        if ct != 'boolean':
            raise SemanticException(
                f'"{scope.filename}", line {self.line}: '
                f'Ternary condition must be boolean, got {ct}'
            )
        tt = self.true.Type(scope)
        ft = self.false.Type(scope)
        wider = _widen(tt, ft)
        if tt != ft and wider is None:
            raise SemanticException(
                f'"{scope.filename}", line {self.line}: '
                f'Ternary branches have incompatible types: {tt} and {ft}'
            )
        self.inferred_type = wider if wider else tt
        cv = self.condition.computed_value
        if cv is True:
            self.computed_value = self.true.computed_value
        elif cv is False:
            self.computed_value = self.false.computed_value
        return self.inferred_type

    def __str__(self):
        return f'{self.condition} ? {self.true} : {self.false}'

@dataclass
class If(Node):
    condition: object = None
    true: List = field(default_factory=list)
    false: object = field(default_factory=list)

    def Type(self, scope):
        ct = self.condition.Type(scope)
        if ct != 'boolean':
            raise SemanticException(
                f'"{scope.filename}", line {self.line}: '
                f'If condition must be boolean, got {ct}'
            )

    def __str__(self):
        return f'if ({self.condition})'


@dataclass
class While(Node):
    condition: object = None
    body: List = field(default_factory=list)

    def Type(self, scope):
        ct = self.condition.Type(scope)
        if ct != 'boolean':
            raise SemanticException(
                f'"{scope.filename}", line {self.line}: '
                f'While condition must be boolean, got {ct}'
            )

    def __str__(self):
        return f'while ({self.condition})'


@dataclass
class DoWhile(Node):
    condition: object = None
    body: List = field(default_factory=list)

    def Type(self, scope):
        ct = self.condition.Type(scope)
        if ct != 'boolean':
            raise SemanticException(
                f'"{scope.filename}", line {self.line}: '
                f'Do-while condition must be boolean, got {ct}'
            )

    def __str__(self):
        return f'do-while ({self.condition})'


@dataclass
class For(Node):
    initialization: object = None
    condition: object = None
    update: object = None
    body: List = field(default_factory=list)

    def Type(self, scope):
        if self.initialization is not None and hasattr(self.initialization, 'Type'):
            self.initialization.Type(scope)
        if self.condition is not None:
            ct = self.condition.Type(scope)
            if ct != 'boolean':
                raise SemanticException(
                    f'"{scope.filename}", line {self.line}: '
                    f'For condition must be boolean, got {ct}'
                )
        if self.update is not None and hasattr(self.update, 'Type'):
            self.update.Type(scope)

    def __str__(self):
        return f'for ({self.initialization}; {self.condition}; {self.update})'


@dataclass
class Switch(Node):
    expr: object = None
    cases: List = field(default_factory=list)

    def Type(self, scope):
        if hasattr(self.expr, 'Type'):
            self.expr.Type(scope)

    def __str__(self):
        return f'switch ({self.expr})'


@dataclass
class Case(Node):
    value: object = None
    body: List = field(default_factory=list)

    def Type(self, scope):
        if self.value != 'default' and hasattr(self.value, 'Type'):
            self.value.Type(scope)

    def __str__(self):
        return f'case {self.value}'


@dataclass
class Try(Node):
    body: List = field(default_factory=list)
    catch: List = field(default_factory=list)
    finally_do: List = field(default_factory=list)

    def Type(self, scope): pass

    def __str__(self):
        return 'try'


@dataclass
class Catch(Node):
    exception: str = ''
    variable: str = ''
    body: List = field(default_factory=list)

    def Type(self, scope):
        scope.add_variable(self.variable, self.exception)

    def __str__(self):
        return f'catch ({self.exception} {self.variable})'


@dataclass
class Return(Node):
    value: object = None

    def Type(self, scope):
        if self.value is not None:
            self.value.Type(scope)
            self.inferred_type = self.value.inferred_type
            self.computed_value = self.value.computed_value
        else:
            self.inferred_type = 'void'

    def __str__(self):
        if self.value is not None:
            return f'return {self.value}'
        return 'return'