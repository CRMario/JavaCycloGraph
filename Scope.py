class Scope:
    def __init__(self):
        self.classes = {}  
        self.variables = {} 
        self.stack = []
        self.current_class = None
        self.current_method = None
        self.filename = ""

    def push(self):
        self.stack.append({})

    def pop(self):
        if self.stack:
            self.stack.pop()

    def add_variable(self, name, type, value=None):
        if self.get_variable(name) is not None: # prevent declaring variables already declared in previous or actual scopes (ex. int x = 5; while (true) {int x = 5;})
            raise SemanticException(f"Variable '{name}' is already defined in this scope.")
        if not self.stack:
            self.push()
        depth = len(self.stack)
        self.stack[-1][name] = {
            'type': type,
            'value': value,
            'mutable': False,
            'depth': depth
        }

    def get_variable(self, name):
        for scope in reversed(self.stack):
            if name in scope:
                return scope[name]
        return None
    
    def conforms(self, type1, type2):
        """Compatibility type1 w/ type2"""
        if type1 == type2:
            return True
        # int conforms to int, boolean to boolean, etc.
        return False

class SemanticException(Exception):
    pass