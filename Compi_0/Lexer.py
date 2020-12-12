from Errors import error
from sly import Lexer

class LuaLexer(Lexer):

    tokens = {
        # palabras reservadas
        AND, BREAK, DO, ELSE, ELSEIF,
        END, FOR, FUNCTION, IF,
        IN, LOCAL, NOT, OR, REPEAT,
        RETURN, THEN, UNTIL, WHILE,

        # operadores de relacion
        EQ, NE, LE, GE, LT, GT,
        CONCAT,

        # Identificador
        NAME,

        # Constantes
        NUMBER, STRING, FALSE, TRUE, NIL,
    }

    literals = '+-*/^%=(){}[];:,.'

    # patrones ignorados
    ignore = ' \t\r'

    # comentarios
    ignore_comment = r'--\[(=*)\[(.|\n)*?\]\]'

    ignore_comment_line = r'--[^\n]*'

    # Identificador
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

    # palabras reservadas
    NAME['if'] = IF
    NAME['then'] = THEN
    NAME['elseif'] = ELSEIF
    NAME['else'] = ELSE

    NAME['while'] = WHILE
    NAME['do'] = DO
    NAME['repeat'] = REPEAT
    NAME['for'] = FOR
    NAME['until'] = UNTIL
    NAME['in'] = IN

    NAME['function'] = FUNCTION
    NAME['break'] = BREAK
    NAME['return'] = RETURN
    NAME['end'] = END
    NAME['local'] = LOCAL

    NAME['and'] = AND
    NAME['or'] = OR
    NAME['not'] = NOT

    # literals
    NAME['true'] = TRUE
    NAME['false'] = FALSE
    NAME['nil'] = NIL

    # operadores
    LE = r'<='
    LT = r'<'
    GE = r'>='
    GT = r'>'
    EQ = r'=='
    NE = r'~='
    CONCAT = r'\.\.'

    @_(r'0x[0-9a-fA-F]+', r'\d+(\.\d+)?([eE][-+]?\d+)?')
    def NUMBER(self, t):
        if t.value.startswith('0x'):
            t.value = int(t.value[2:],16)
        else:
            try:
                t.value = int(t.value)
            except ValueError:
                t.value = float(t.value)
        return t

    @_(r"'[^']*'", r'"[^"]*"')
    def STRING(self, t):
        # Revision secuencia de escape malas
        index = 0
        while index < len(t.value):
            if t.value[index] == '\\':
                if t.value[index+1] in 'abfnrtv"\\':
                    index += 2
                    continue
                else:
                    error(t.lineno, "Incomplete character escape sequence in string literal.")
            index += 1
        return t

    # acciones extras para newline
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    # comentarios
    def ignore_comment(self, t):
        self.lineno += t.value.count('\n')

    @_(r'--\[\[[^\]]*')
    def ignore_untermcomment(self, t):
        error(t.lineno, "Comentario largo sin cerrar.")

    def error(self, t):
        error("Caracter ilegal '%s'" % t.value[0], t.lineno)
        self.index += 1
