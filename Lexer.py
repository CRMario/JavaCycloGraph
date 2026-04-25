from sly import Lexer

class JavaLexer(Lexer):

    # this part is for EOF that sly does not manage
    def tokenize(self, text, *args, **kwargs):
        for tok in super().tokenize(text, *args, **kwargs):
            yield tok
        
        if self.__class__.__name__ == 'MatchingString':
            class EOFToken: pass
            t = EOFToken()
            t.type = "ERROR"
            t.value = '"EOF in string constant"'
            t.lineno = self.lineno
            yield t
            self.begin(JavaLexer)

        elif self.__class__.__name__ == 'BlockComment':
            class EOFToken: pass
            t = EOFToken()
            t.type = "ERROR"
            t.value = '"EOF in comment"'
            t.lineno = self.lineno
            yield t
            self.begin(JavaLexer)

    tokens = {
        # literals and identifiers
        ID, INT_CONST, BOOL_CONST, FLOAT_CONST, STR_CONST,

        # tokens that add up to cyclomatic complexity
        IF, ELSE, WHILE, FOR, SWITCH, CASE, DO, RETURN, 
        DEFAULT, QUESTION, BREAK, TRY, CATCH, FINALLY,
        # ? for ternary operators

        # tokens that define the code structure
        CLASS, PUBLIC, PRIVATE, STATIC, VOID, THIS, NULL,

        # logic operators
        AND, OR, NOT,

        # comparison operators
        LE, GE, LT, GT, EQ, NE,

        INCREMENT, DECREMENT, NEW,
    }

    literals = { '{', '}',
                 '(', ')',
                 '[', ']',
                 ';', ':', ',', '.', '=',
                 '+', '-', '*', '/', '&', '|', '%'
                }

    keywords = {
        'if': 'IF', 'else': 'ELSE', 'while': 'WHILE', 'for': 'FOR',
        'switch': 'SWITCH', 'case': 'CASE', 'do': 'DO', 'return': 'RETURN',
        'class': 'CLASS', 'public': 'PUBLIC', 'private': 'PRIVATE',
        'static': 'STATIC', 'void': 'VOID', 'default': 'DEFAULT',
        'break': 'BREAK', 'try': 'TRY', 'catch': 'CATCH', 'finally': 'FINALLY',
        'this': 'THIS', 'null': 'NULL','new': 'NEW'
    }

    ignore = '\t\r' # using windows, may have to be changed for unix
    
    # integers
    @_(r'[0-9]+')
    def INT_CONST(self,t):
        return t
    
    # booleans
    @_(r'true|false')
    def BOOL_CONST(self,t):
        return t
    
    # strings
    @_(r'"|\'')
    def STR_CONST(self,t):
        self.str_buf = f"{t.value}"
        self.closing_delimiter = t.value # remember if the string was opened with " or '
        self.begin(MatchingString)

    # floats
    @_(r'[0-9]*\.[0-9]+|[0-9]+\.[0-9]*')
    def FLOAT_CONST(self,t):
        return t
    
    # ids
    @_(r'[a-zA-Z_][a-zA-Z0-9_]*')
    def ID(self, t):
        t.type = self.keywords.get(t.value,'ID')
        return t
    
    # the following tokens are for logic operators

    @_(r'&&')
    def AND(self,t):
        t.type = "AND"
        return t
    
    @_(r'\|\|')
    def OR(self,t):
        t.type = "OR"
        return t
    
    @_(r'!')
    def NOT(self,t):
        t.type = "NOT"
        return t

    # the following tokens are for comparison

    @_(r'<=')
    def LE(self,t):
        t.type = "LE"
        return t
    
    @_(r'>=')
    def GE(self,t):
        t.type = "GE"
        return t

    @_(r'<')
    def LT(self,t):
        t.type = "LT"
        return t
    
    @_(r'>')
    def GT(self,t):
        t.type = "GT"
        return t
    
    @_(r'==')
    def EQ(self,t):
        t.type = "EQ"
        return t
    
    @_(r'!=')
    def NE(self,t):
        t.type = "NE"
        return t
    
    # increment and decrement

    @_(r'\+\+')
    def INCREMENT(self, t):
        return t

    @_(r'--')
    def DECREMENT(self, t):
        return t

    # question for the ternary operator
    @_(r'\?')
    def QUESTION(self, t):
        return t
    
    # single line comments
    @_(r'//.*')
    def COMMENT(self, t):
        pass

    @_(r'/\*')
    def BLOCK_COMMENT(self, t):
        self.begin(BlockComment)

    @_(r'\n')
    def NEWLINE(self, t):
        self.lineno += 1

    def error(self, t):
        self.index += 1

# -----------------------------------------------------------

class MatchingString(Lexer):
    """State that keeps track of valid and invalid strings"""
    tokens = {}
    # all characters and escaped elements are added to the string
    @_(r'[^\x00-\x1f\x7f\\\"\n]+')
    def CHARACTER(self, t):
        self.str_buf += t.value

    @_(r'\\\\')
    def ESCAPE_BACKLASH(self, t):
        self.str_buf += t.value

    @_(r'\\[nbtf"]')
    def ESCAPE_ESPECIAL(self, t):
        self.str_buf += t.value 

    # detect when there is a new line and the string hasn't been closed
    @_(r'\r?\n')
    def NOT_ESCAPED(self, t):
        self.lineno += 1
        self.begin(JavaLexer)
        t.type = "ERROR"
        t.value = '"Unterminated string constant"' 
        return t

    # closing the string with the same delim
    @_(r'"|\'')
    def CLOSE_STRING(self, t):
        if self.closing_delimiter == t.value:
            t.value = self.str_buf + t.value
            t.type = "STR_CONST"
            self.begin(JavaLexer)
            return t
        else:
            # if its not the same delimiter used for
            # opening and closing add it to the string
            self.str_buf += t.value

# -----------------------------------------------------------

class BlockComment(Lexer):
    """State that keeps track of block comments"""
    tokens = {}

    @_(r'\*/')
    def CLOSE_BLOCK_COMMENT(self,t):
        self.begin(JavaLexer)

    @_(r'\n')
    def NEWLINE(self,t):
        self.lineno += 1
        
    @_(r'.')
    def CONTENT(self,t):
        pass