class Scope:
    def __init__(self):
        self.stack = []

    def push(self):
        self.stack.append({})

    def pop(self):
        if self.stack:
            self.stack.pop()

    def add(self, name, type):
        if self.stack:
            self.stack[-1][name] = type # append at the end

    def lookup(self, name):
        # search from innermost to outermost scope
        for scope in reversed(self.stack):
            if name in scope:
                return scope[name]
        return None  # not found
    
    def is_declared_in_current(self, name):
        if self.stack:
            return name in self.stack[-1]
        return False
    
    def nesting_depth(self):
        return len(self.stack)