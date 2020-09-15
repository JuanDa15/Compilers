from sly import Lexer

class tokenizer(Lexer):
    tokens = {IDENT,NUMBER}
    literals = '+-*/();='
    
    ignore = r' \t\r'
    
    #Regular expresions
    
    NUMBER = r'\d+(\.\d*)?([eE][-+]?\d+)?'
    IDENT = r'[a-zA-Z_][a-zA-Z0-9]*'
    
    def NUMBER(self,t):
        t.value = float(t.value)
        return t
    
    def error(self,t):
        print(f'wrong input {t.value[0]}')
        self.index += 1
    
class RecursiveDescentParser(object):
    
    symtab = {}
    def assignment(self):
        '''
        assignment: IDENT = expression;
        '''
        if self._accept('IDENT'):
            name = self.tok.value
            self._expect('=')
            expr = self.expression()
            self._expect(';')
            self.symtab[name] = expr
            return expr
        else:
            raise SyntaxError('Error en assignacion')
        
    def expression(self):
        '''
        expression: term { ('+'|'-') term }
        '''
        expr = self.term()
        while self._accept('+') or self._accept('-'):
            if self.tok.value == '+':
                expr += self.term()
            else:
                expr -= self.term()
            return expr
            
    def term(self):
        '''
        term: factor { ('*'|'/') factor }
        '''
        term = self.factor()
        while self._accept('*') or self._accept('/'):
            if self.tok.value == '*':
                term *= self.factor()
            else:
                term /= self.factor()
            return term
    
    def factor(self):
        '''
        factor: IDENT
                |NUMBER
                |(expression)
        '''
        if self._accept('IDENT'):
            return self.symtab[self.tok.value]
        elif self._accept('NUMBER'):
            return self.tok.value
        elif self._accept('('):
            expr = self.expression()
            self._expect(')')
            return expr
        else:
            raise SyntaxError('Error en factor')
    
    #USE EL METODO ._accept() para probar y aceptar el token actualmente leido
    #USE EL METODO ._expect() para coincidir y descartar exactamente  el token

    #El atributo .tok contiene el ultimo token aceptado
    #El atributo .nexttok contiene el siguiente token leido

    #---------------------------------------------------
    #Funciones de utilidad
    #
    def _advance(self):
        'Advanced the tokenizer by one symbol'
        self.tok, self.nexttok = self.nexttok, next(self.tokens,None)
    
    def _accept(self,toktype):
        'consume the next token if it matches an expected type'
        if self.nexttok and  self.nexttok.type == toktype:
            self._advance()
            return True
        else:
            return False
        
    def _expect(self,toktype):
        'consume and discard the next token or raise syntaxerror'
        if not self._accept(toktype):
            raise SyntaxError("Expected %s" %toktype)
        
    def start(self):
        'entry point to parsing'
        self._advance()
        return self.assignment()
    
    
    def parse(self,tokens):
        'entry  point to parsing'
        self.tok = None #Last symbol consume
        self.nexttok = None #next symbol tokenized
        self.tokens = tokens
        return self.start()
    
    
text = 'a = 2 + 3 * (4 + 5);'
lexer = tokenizer()
parser = RecursiveDescentParser()

root = parser.parse(lexer.tokenize(text))
print(root)