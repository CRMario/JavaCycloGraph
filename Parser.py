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
    
    @_("modifiers return_type ID '(' parameters_list ')' '{' method_body '}'")
    def method_declaration(self, p):
        return Method(name=p.ID, params=p.parameters_list, body=p.method_body)
    
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
    
    
