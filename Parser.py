from Lexer import JavaLexer
from sly import Parser
import sys
import os
from Classes import *

class JavaParser(Parser):
    tokens = JavaLexer.tokens
    debugfile = "debug.out"

    precedence = (
        ('right', 'ASSIGN'), # (int a = 3)
        ('left', 'OR'), # (a || b) || c
        ('left', 'AND'), # (a && b) && c
        ('right', 'NOT'), # (! a)
        ('nonassoc', 'EQ', 'NE'), # can not do a == b == c or a != b != c ...
        ('nonassoc', 'LE', 'GE', 'GT', 'LT'), # can not do a < b < c ...
        ('left', '+', '-'), # (a + b) + c
        ('left', '*', '/'), # (a * b) * c
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
    def method_list(self, p):
        return []  # the class can also have no methods
    
    @_("modifiers type ID '(' parameters_list ')' '{' method_body '}'")
    def method_declaration(self, p):
        return Method(name=p.ID, params=p.parameters_list, body=p.method_body)
    
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
        return p.modifiers + [p.PUBLIC]
    
    @_("modifiers PRIVATE")
    def modifiers(self, p):
        return p.modifiers + [p.PRIVATE]
    
    @_("modifiers STATIC")
    def modifiers(self, p):
        return p.modifiers + [p.STATIC]
    
    @_("PUBLIC")
    def modifiers(self, p):
        return [p.PUBLIC]
    
    @_("PRIVATE")
    def modifiers(self, p):
        return [p.PRIVATE]
    
    @_("STATIC")
    def modifiers(self, p):
        return [p.STATIC]

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
        return For(initialization=p.for_init, condition=p.expression,
                   update=p.expression, body=p.statements_list, line=p.lineno)
    
    @_("variable_declaration")
    def for_init(self, p):
        return p.variable_declaration
    
    @_("assignment")
    def for_init(self, p):
        return p.assignment
    
    # comparison expressions

    @_("expression LE expression")
    def expression(self, p):
        return f'{p[0]} <= {p[2]}'
    
    @_("expression GE expression")
    def expression(self, p):
        return f'{p[0]} >= {p[2]}'
    
    @_("expression LT expression")
    def expression(self, p):
        return f'{p[0]} < {p[2]}'
    
    @_("expression GT expression")
    def expression(self, p):
        return f'{p[0]} > {p[2]}'
    
    @_("expression EQ expression")
    def expression(self, p):
        return f'{p[0]} == {p[2]}'
    
    @_("expression NE expression")
    def expression(self, p):
        return f'{p[0]} != {p[2]}'

    # logical expressions
    @_("expression AND expression")
    def expression(self, p):
        return f'{p[0]} && {p[2]}'
    
    @_("expression '&' expression")   
    def expression(self, p):
        return f'{p[0]} & {p[2]}'
    
    @_("expression OR expression")
    def expression(self, p):
        return f'{p[0]} || {p[2]}'
    
    @_("expression '|' expression")   
    def expression(self, p):
        return f'{p[0]} | {p[2]}'
    
    @_("NOT expression")
    def expression(self, p):
        return f'!{p[1]}'

    # TODO: more expressions

    # increment expressions
    @_("ID INCREMENT")
    def expression(self, p):
        return f'{p.ID}++'

    @_("ID DECREMENT")
    def expression(self, p):
        return f'{p.ID}--'
    
    @_("ID")
    def expression(self, p):
        return f'{p.ID}'