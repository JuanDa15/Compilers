from sly import Lexer
from typing import Any, List
from dataclasses import dataclass, field
from multimethod import multimeta
from graphviz import Source
from graphviz import render as ren
from graphviz import Digraph
import os
os.environ["PATH"] += os.pathsep + 'C:/Graphviz/bin'
ExpressionList = []
assing_dict = {}

class Tokenizer(Lexer):
    tokens = { IDENT, NUMBER, }
    literals = '+-*/^=();'
    ignore = ' \t'

    # Expresiones Regulares
    IDENT  = r'[a-zA-Z_][a-zA-Z0-9_]*'
    NUMBER = r'\d+(\.\d*)?([eE][-+]?\d+)?'

    def NUMBER(self, t):
        t.value = float(t.value)
        return t

    def error(self, t):
        print(f'Error Lexico: {t.value[0]}')
        self.index += 1

# clases Abstractas
class Visitor(metaclass=multimeta):
    pass

@dataclass
class Node:
    def accept(self, visitor: Visitor, *args, **kwargs):
        return visitor.visit(self, *args, **kwargs)

@dataclass
class Statement(Node):
    pass

@dataclass
class Expression(Node):
    pass

@dataclass
class Literal(Expression):
    '''
    Una Constante como 2, 2.5, 'dos', Nil, True, False
    '''
    pass

@dataclass
class Location(Node):
    pass

# Nodos Reales del AST
@dataclass
class Number(Literal):
    value : float

@dataclass
class SimpleLocation(Location):
    name : str

@dataclass
class ReadLocation(Expression):
    location : Location

@dataclass
class WriteLocation(Statement):
    location : Location
    expr     : Expression

@dataclass
class Binop(Expression):
    '''
    Operador binario coom: +, -, *, /, ^
    '''
    op    : str
    left  : Expression
    right : Expression

class RecursiveDescentParser(object):
    '''
    Implementacion de un Analizador descendente recursivo.
    Cada metodo implementa una sola regla de la gramatica.

    Use el metodo ._accept() para probar y aceptar el token actualmente leido.
    Use el metodo ._expect() para coincidir y descartar exactamente el token
    siguiente en la entrada (o levantar un SystemError si no coincide).

    El atributo .tok contiene el ultimo token aceptado.
    El atributo .nexttok contiene el siguiente token leido.
    '''
    # Tabla de simbolos
    symtab = {}

    def assignment(self):
        '''
        assignment : [IDENT = expression ;, IDENT = expression ;, ...]
        '''
        if self._accept('IDENT'):
            name = self.tok.value
            self._expect('=')
            expr = self.expression()
            self._expect(';')
            ExpressionList.append(WriteLocation(SimpleLocation(name), expr))
            assing_dict[name] = AritExprEval(expr)
            self._continue()
            return ExpressionList
        else:
            raise SyntaxError('Error de sintaxis en Asignación')

    def expression(self):
        '''
        expression : term ( ('+'|'-') term )*
        '''
        expr = self.term()
        while self._accept('+') or self._accept('-'):
            op    = self.tok.value
            right = self.term()
            expr  = Binop(op, expr, right)

        return expr

    def term(self):
        '''
        term : factor ( ('*'|'/'|'^') factor )*
        '''
        term = self.factor()
        while self._accept('*') or self._accept('/') or self._accept('^'):
            op    = self.tok.value
            right = self.factor()
            term  = Binop(op, term, right)

        return term

    def factor(self):
        '''
        factor : IDENT | NUMBER | ( expression )
        '''
        if self._accept('IDENT'):
            return ReadLocation(SimpleLocation(self.tok.value))

        elif self._accept('NUMBER'):
            return Number(self.tok.value)

        elif self._accept('('):
            expr = self.expression()
            self._expect(')')
            return expr

        else:
            raise SyntaxError('Error de sintaxis en factor')


    # ------------------------------------------------- #
    # Funciones de Utilidad.  No cambie nada            #
    # Agregar significa cambiar?                        #
    # ------------------------------------------------- #
    def _continue(self):
        'Continues searching for more expressions'
        if self.nexttok:
            if self.nexttok.type == 'IDENT':
                'Entry point to parsing the next expression'
                return self.assignment()
        else:
            return False

    def _advance(self):
        'Advanced the tokenizer by one symbol'
        self.tok, self.nexttok = self.nexttok, next(self.tokens, None)

    def _accept(self, toktype):
        'Consume the next token if it matches an expected type'
        if self.nexttok and self.nexttok.type == toktype:
            self._advance()
            return True
        else:
            return False

    def _expect(self, toktype):
        'Consume and discard the next token or raise SyntaxError'
        if not self._accept(toktype):
            raise SyntaxError("Expected %s" % toktype)

    def start(self):
        'Entry point to parsing'
        self._advance()              # Load first lookahead token
        return self.assignment()

    def parse(self, tokens):
        'Entry point to parsing'
        self.tok = None         # Last symbol consumed
        self.nexttok = None     # Next symbol tokenized
        self.tokens = tokens
        return self.start()

class AritExprEval(Visitor):
    '''
    Arithmetical Expression Evaluator
    Recieves the expression from a Abstract Syntax Tree
    from the  RecursiveDescentParser function.
    '''
    def __init__(self,exp):
        self.exp = exp

    def transform(self, oper):
        if oper == '^':
            return '**'
        else:
            return str(oper)

    def calcExpression(self, Expression):
        if isinstance(Expression,Binop):
            return str(eval(str(eval(self.calcExpression(Expression.left)))+self.transform(Expression.op)+str(eval(self.calcExpression(Expression.right)))))
        elif isinstance(Expression,Number):
            return str(Expression.value)
        elif isinstance(Expression,ReadLocation):
            try:
                value = str(assing_dict[Expression.location.name])
                return value
            except:
                raise SyntaxError("variable %s doesn't exist." % str(Expression.location.name))
    
    def __repr__(self):
        return self.calcExpression(self.exp)

text   = 'x = 1/2; arcsin_x = x + ((1/2)*((x)^3)/3) + ((1/2)*(3/4)*((x)^5)/5) + ((1/2)*(3/4)*(5/6)*((x)^7))/7; pi = arcsin_x * 6;'

lexer  = Tokenizer()
parser = RecursiveDescentParser()
ast_list = parser.parse(lexer.tokenize(text))
#for ast in ast_list:
#    print(ast)
for assing in assing_dict:
    print(assing + " = " + str(assing_dict[assing]))


#RENDER EN PDF
class ASTRender(Visitor):
    '''
    Crea archivo tipo 'dot' para Graphiz
    '''
    _node_defaults = {
        'shape': 'box',
        'color': 'lightblue2',
        'style': 'filled'
    }

    _edge_defaults = { }


    def __init__(self):
        '''
        creamos un obj del tipo dot que se va a llamar AST
        '''
        self.dot = Digraph('AST', comment='AST para Calculadora')
        self.dot.attr('node', **self._node_defaults)
        self.dot.attr('edge', **self._edge_defaults)
        self.id =0

    @classmethod
    def render(cls, model):
        renderer = cls()
        model.accept(renderer)

    def __repr__(self):
        return self.dot

    def _id(self):
        self.id += 1
        return 'n%02d' % self.id

    def visit(self, node: Binop):
        name = self._id()
        label = 'binop\nop: {}'.format(node.op)
        self.dot.node(name, label)
        self.dot.edge(name, self.visit(node.left))
        self.dot.edge(name, self.visit(node.right))
        return name

    def visit(self, node: WriteLocation):
        name = self._id()
        label = 'assign'
        self.dot.node(name, label)
        self.dot.edge(name, self.visit(node.location))
        self.dot.edge(name, self.visit(node.expr))
        return name

    def visit(self, node: ReadLocation):
        name = self._id()
        label = 'variable\nrequest: {}'.format(node.location.name)
        self.dot.node(name, label, color='lightgreen')
        return name
    
    def visit(self, node: Number):
        name = self._id()
        label = 'constant\nvalue: {}'.format(node.value)
        self.dot.node(name, label, color='yellow')   # color amarillo
        return name

    def visit(self, node: SimpleLocation):
        name = self._id()
        label = 'variable\nname: {}'.format(node.name)
        self.dot.node(name, label, color='limegreen')
        return name

if __name__ == '__main__':
    dot = ASTRender()
    #print(dot)
    print(ast_list[0])
    for i in ast_list:
        i.accept(dot)
    #dot.dot.view()
