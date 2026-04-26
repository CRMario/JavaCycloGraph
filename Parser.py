from Lexer import JavaLexer
from sly import Parser
import sys
import os
from Classes import *

class JavaParser(Parser):
    tokens = JavaLexer.tokens
    debugfile = "debug.out"

    precedence = (
        ('right', '='), # (int a = 3)
        ('left', 'OR'), # (a || b) || c
        ('left', 'AND'), # (a && b) && c
        ('right', 'NOT'), # (! a)
        ('nonassoc', 'EQ', 'NE'), # can not do a == b == c or a != b != c ...
        ('nonassoc', 'LE', 'GE', 'GT', 'LT'), # can not do a < b < c ...
        ('left', '+', '-'), # (a + b) + c
        ('left', '*', '/'), # (a * b) * c
        ('right', 'UMINUS'), # (- a)
        ('left', '.') # (members.get(2)).salary
    )

    def __init__(self, filename=''):
        self.filename = filename
        self.errors = []  # errors list

    def error(self, p):
  
        if not hasattr(self, 'errores'):
            self.errors = []
            
        if p:
            message = f'"{self.filename}", line {p.lineno}: syntax error at or near \'{p.type}\''
        else:
            # EOF error
            message = f'"{self.filename}", line 0: syntax error at or near EOF'

        self.errors.append(message)

    def parse(self, tokens):
        result = super().parse(tokens)
 
        if result is None:
            return Program()
            
        return result
    
    # a program is made out of multiple classes
    @_("classes_list")
    def program(self, p):
        return Program(classes=p.classes_list)

    @_("classes_list class_declaration")     
    def classes_list(self, p):
        return p.classes_list + [p.class_declaration]
    
    @_("class_declaration")
    def classes_list(self, p):
        return [p.class_declaration]
    
    # a class is made out of multiple methods
    
    @_("modifiers CLASS ID '{' class_body '}'")
    def class_declaration(self,p):
        return Class(name=p.ID, methods=p.class_body, line=p.lineno)
    
    @_("methods_list")
    def class_body(self,p):
        """Since I am doing a simple case the class_body is just a list of
        methods, so this grammar rule could have been omitted in class_declaration
        to methods_list instead of class_body but I add this here in case it is
        extended afterwards.."""
        return p.methods_list
    
    @_("methods_list method_declaration")
    def methods_list(self, p):
        return p.methods_list + [p.method_declaration]
    
    @_("method_declaration")
    def methods_list(self, p):
        return [p.method_declaration]

    @_("")
    def methods_list(self, p):
        return []  # the class can also have no methods
    
    @_("modifiers type ID '(' parameters_list ')' '{' method_body '}'")
    def method_declaration(self, p):
        return Method(name=p.ID, return_type=p.type, params=p.parameters_list, body=p.method_body)
    
    @_("VOID")
    def type(self, p):
        return p.VOID
    
    @_("ID")
    def type(self, p):
        return p.ID
    
    @_("ID '[' ']'")
    def type(self, p):
        return f'{p.ID}[]' #arrays
    
    @_("parameters_list ',' type ID")
    def parameters_list(self,p):
        return p.parameters_list + [(p.type, p.ID)]

    @_("type ID")
    def parameters_list(self,p):
        return [(p.type, p.ID)]
    
    @_("")
    def parameters_list(self,p):
        return [] # a method can have no parameters

    @_("statements_list")
    def method_body(self, p):
        return p.statements_list
    
    @_("statements_list statement")
    def statements_list(self, p):
        return p.statements_list + [p.statement]
    
    @_("statement")
    def statements_list(self, p):
        return [p.statement]
    
    @_("")
    def statements_list(self, p):
        return [] # in java a method can have no statements
    
    @_("if_statement")
    def statement(self, p):
        return p.if_statement
    
    @_("while_statement")
    def statement(self, p):
        return p.while_statement
    
    @_("do_while_statement")
    def statement(self, p):
        return p.do_while_statement
    
    @_("for_statement")
    def statement(self,p):
        return p.for_statement
    
    @_("switch_statement")
    def statement(self,p):
        return p.switch_statement
    
    @_("try_statement")
    def statement(self, p):
        return p.try_statement
    
    @_("return_statement")
    def statement(self, p):
        return p.return_statement
    
    @_("variable_declaration")
    def statement(self, p):
        return p.variable_declaration
    
    @_("expression_statement")
    def statement(self, p):
        return p.expression_statement
    
    @_("modifiers PUBLIC")
    def modifiers(self, p):
        return p.modifiers + ['public']
 
    @_("modifiers PRIVATE")
    def modifiers(self, p):
        return p.modifiers + ['private']
 
    @_("modifiers STATIC")
    def modifiers(self, p):
        return p.modifiers + ['static']
 
    @_("PUBLIC")
    def modifiers(self, p):
        return ['public']
 
    @_("PRIVATE")
    def modifiers(self, p):
        return ['private']
 
    @_("STATIC")
    def modifiers(self, p):
        return ['static']
 
    @_("")
    def modifiers(self, p):
        return [] # no modifiers

    @_("IF '(' expression ')' '{' statements_list '}' ")
    def if_statement(self,p):
        return If(condition=p.expression, true=p.statements_list, line=p.lineno)

    @_("IF '(' expression ')' '{' statements_list '}' ELSE '{' statements_list '}'")
    def if_statement(self,p):
        return If(condition=p.expression, true=p[5], false=p[9], line=p.lineno)
    
    # if (a > b) }
    #    a = 5; 
    # } else
    # if (b > c) {
    #     ...
    # }
    # else-if statements are another recursive if_statement
    @_("IF '(' expression ')' '{' statements_list '}' ELSE if_statement")
    def if_statement(self, p):
        return If(condition=p.expression, true=p.statements_list, false=p.if_statement, line=p.lineno)
    
    @_("WHILE '(' expression ')' '{' statements_list '}'")
    def while_statement(self,p):
        return While(condition=p.expression, body=p.statements_list, line=p.lineno)
    
    @_("DO '{' statements_list '}' WHILE '(' expression ')' ';'")
    def do_while_statement(self, p):
        return DoWhile(condition=p.expression, body=p.statements_list, line=p.lineno)
    
    @_("FOR '(' for_init expression ';' expression ')' '{' statements_list '}' ")
    def for_statement(self,p):
        return For(initialization=p.for_init, condition=p[3],
                   update=p[5], body=p.statements_list, line=p.lineno)
    
    @_("variable_declaration")
    def for_init(self, p):
        return p.variable_declaration
    
    @_("expression")
    def for_init(self, p):
        return p.expression
    
    # comparison expressions

    @_("expression LE expression")
    def expression(self, p):
        return LEOperation(left=p[0],right=p[2],line=p.lineno)
    
    @_("expression GE expression")
    def expression(self, p):
        return GEOperation(left=p[0],right=p[2],line=p.lineno)
    
    @_("expression LT expression")
    def expression(self, p):
        return LTOperation(left=p[0],right=p[2],line=p.lineno)
    
    @_("expression GT expression")
    def expression(self, p):
        return GTOperation(left=p[0],right=p[2],line=p.lineno)
    
    @_("expression EQ expression")
    def expression(self, p):
        return EQOperation(left=p[0],right=p[2],line=p.lineno)
    
    @_("expression NE expression")
    def expression(self, p):
        return NEOperation(left=p[0],right=p[2],line=p.lineno)

    # logical expressions
    @_("expression AND expression")
    def expression(self, p):
        return ANDOperation(left=p[0],right=p[2],line=p.lineno)
    
    @_("expression '&' expression")   
    def expression(self, p):
        return BitwiseANDOperation(left=p[0],right=p[2],line=p.lineno)
    
    @_("expression OR expression")
    def expression(self, p):
        return OROperation(left=p[0],right=p[2],line=p.lineno)
    
    @_("expression '|' expression")   
    def expression(self, p):
        return BitwiseOROperation(left=p[0],right=p[2],line=p.lineno)
    
    @_("NOT expression")
    def expression(self, p):
        return NotOp(op='!', operand=p[1], line=p.lineno)

    # arithmetic expressions
    @_("expression '+' expression")
    def expression(self,p):
        return AddOperation(left=p[0],right=p[2],line=p.lineno)
    
    @_("expression '-' expression")
    def expression(self,p):
        return SubstractOperation(left=p[0],right=p[2],line=p.lineno)
    
    @_("expression '/' expression")
    def expression(self,p):
        return DivOperation(left=p[0],right=p[2],line=p.lineno)
    
    @_("expression '*' expression")
    def expression(self,p):
        return MultOperation(left=p[0],right=p[2],line=p.lineno)
    
    @_("expression '%' expression")
    def expression(self,p):
        return RemainderOperation(left=p[0],right=p[2],line=p.lineno)
    
    #method calls
    @_("ID '(' expression_list ')'")
    def expression(self, p):
        return MethodCall(obj=None, method=p.ID, args=p.expression_list, line=p.lineno)

    @_("expression_list ',' expression")
    def expression_list(self, p):
        return p.expression_list + [p.expression]

    @_("expression")
    def expression_list(self, p):
        return [p.expression]
    
    @_("")
    def expression_list(self, p):
        return [] # no arguments
    
    # parenthesized expression
    @_("'(' expression ')'")
    def expression(self, p):
        return p.expression
    
    # chained method calls: field access (ex. System.out) and method call (ex. banana.split())
    @_("expression '.' ID") 
    def expression(self, p):
        return FieldAccess(obj=p[0], field=p.ID, line=p.lineno)
    
    @_("expression '.' ID '(' expression_list ')'") 
    def expression(self, p):
        return MethodCall(obj=p[0], method=p.ID, args=p.expression_list, line=p.lineno)

    # array access
    @_("expression '[' expression ']'")
    def expression(self, p):
        return ArrayAccess(array=p[0], index=p[2], line=p.lineno)
    
    # ternary operator
    @_("expression QUESTION expression ':' expression")
    def expression(self, p):
        return Ternary(condition=p[0],true=p[2],false=p[4],line=p.lineno)
    
    # casting
    @_("'(' type ')' expression")
    def expression(self, p):
        return Cast(cast_type=p.type, expr=p.expression, line=p.lineno)

    # this
    @_("THIS")
    def expression(self,p):
        return This(line=p.lineno)
    
    # null
    @_("NULL")
    def expression(self,p):
        return NullLiteral(line=p.lineno)
    
    # new for object creation
    @_("NEW ID '(' expression_list ')'")
    def expression(self,p):
        return NewObject(class_name=p.ID, args=p.expression_list, line=p.lineno)
    
    @_("NEW ID '[' expression ']'")
    def expression(self,p):
        return NewArray(element_type=p.ID, size=p.expression, line=p.lineno)
    
    # int, float, boolean, string
    @_("INT_CONST")
    def expression(self, p):
        return Integer(value=int(p.INT_CONST),line=p.lineno)
    
    @_("FLOAT_CONST")
    def expression(self, p):
        return Float(value=float(p.FLOAT_CONST),line=p.lineno)
    
    @_("BOOL_CONST")
    def expression(self, p):
        return Bool(value=(p.BOOL_CONST == 'true'),line=p.lineno)
    
    @_("STR_CONST")
    def expression(self, p):
        return String(value=p.STR_CONST,line=p.lineno)

    # there's more primitive types. they will all fall under the 'type' rule, just like
    # these four previous ones could have had since i will not be doing type checking (for now?)

    # assignment as expression
    @_("ID '=' expression")
    def expression(self, p):
        return Assignment(name=p.ID, value=p.expression, line=p.lineno)
    
    # increment expressions
    @_("ID INCREMENT")
    def expression(self, p):
        return Increment(operand=Identifier(name=p.ID, line=p.lineno), line=p.lineno)

    @_("ID DECREMENT")
    def expression(self, p):
        return Decrement(operand=Identifier(name=p.ID, line=p.lineno),line=p.lineno)
    
    @_("'-' expression %prec UMINUS") # ex. value -1
    def expression(self, p):
        return UnaryMinus(operand=p.expression, line=p.lineno)
    
    @_("ID")
    def expression(self, p):
        return Identifier(name=p.ID, line=p.lineno)
    
    # done with expressions

    # variable declaration
    @_("type ID '=' expression ';'")
    def variable_declaration(self, p):
        return VarDecl(var_type=p.type, name=p.ID, value=p.expression, line=p.lineno)
    
    @_("type ID ';'")
    def variable_declaration(self, p):
        return VarDecl(var_type=p.type, name=p.ID, line=p.lineno)
    
    #expression statement
    @_("expression ';'")
    def expression_statement(self, p):
        return p.expression
    
    # return statement
    @_("RETURN expression ';'")
    def return_statement(self, p):
        return Return(value=p.expression,line=p.lineno)
    
    @_("RETURN ';'")
    def return_statement(self, p):
        return Return(line=p.lineno)
    
    # switch statement
    @_("SWITCH '(' expression ')' '{' case_list '}'")
    def switch_statement(self,p):
        return Switch(condition=p.expression,cases=p.case_list,line=p.lineno)
    
    @_("case_list case")
    def case_list(self, p):
        return p.case_list + [p.case]
    
    @_("case")
    def case_list(self, p):
        return [p.case]
    
    @_("CASE expression ':' statements_list BREAK ';'")
    def case(self, p):
        return Case(value=p.expression,body=p.statements_list,line=p.lineno)
    
    @_("CASE expression ':' statements_list") #java allows no break in cases
    def case(self, p):
        return Case(value=p.expression, body=p.statements_list, line=p.lineno)
    
    @_("DEFAULT ':' statements_list BREAK ';'")
    def case(self, p):
        return Case(value="default",body=p.statements_list,line=p.lineno)
    
    @_("DEFAULT ':' statements_list")
    def case(self, p):
        return Case(value="default",body=p.statements_list,line=p.lineno)
    
    # try statement
    @_("TRY '{' statements_list '}' catch_list")
    def try_statement(self,p):
        return Try(body=p.statements_list,catch=p.catch_list,line=p.lineno)
    
    @_("TRY '{' statements_list '}' catch_list FINALLY '{' statements_list '}'") #with finally block
    def try_statement(self,p):
        return Try(body=p[2],catch=p.catch_list,finally_do=p[7],line=p.lineno)
    
    @_("TRY '{' statements_list '}' FINALLY '{' statements_list '}'") #with finally block and no cases
    def try_statement(self,p):
        return Try(body=p[2],finally_do=p[6],line=p.lineno)
    
    @_("catch_list CATCH '(' type ID ')' '{' statements_list '}'")
    def catch_list(self,p):
        return p.catch_list + [Catch(exception=p.type,variable=p.ID,body=p.statements_list,line=p.lineno)]

    @_("CATCH '(' type ID ')' '{' statements_list '}'")
    def catch_list(self,p):
        return [Catch(exception=p.type,variable=p.ID,body=p.statements_list,line=p.lineno)]