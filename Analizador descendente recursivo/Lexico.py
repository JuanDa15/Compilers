#Analizador descendente recursivo
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
        
text = 'a = 2 + 3 * ( 2 + 4 );'
lexer = tokenizer()
for tok in lexer.tokenize(text):
    print(tok)