# ----------------------------------------
# Analisis Sintatico para Lua 5.1
#
# (c) Angel A Agudelo Z
# ----------------------------------------
from dataclasses import dataclass, field
from typing import Any, List
from Errors import error
from Lexer import LuaLexer
from multimethod import multimeta
from graphviz import Source
from graphviz import render as ren
from graphviz import Digraph
import sly
import os
os.environ["PATH"] += os.pathsep + 'C:/Graphviz/bin'

@dataclass
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
    pass

@dataclass
class Number(Literal):
    value: float

@dataclass
class Nil(Literal):
    pass

@dataclass
class Boolean(Literal):
    value: bool = field(default_factory=False)

@dataclass
class String(Literal):
    value: str

@dataclass
class Var(Literal):
    value: str

@dataclass
class Name(Literal):
    value: str
    def _add(self,s):
        self.value = self.value + '.' + s

@dataclass
class Not(Expression):
    value: Expression

@dataclass
class TableData(Expression):
    value: str
    exp: Expression

@dataclass
class Table(Expression):
    data: List[TableData] = field(default_factory=list)

@dataclass
class CallTable(Expression):
    field: Expression
    table: List[Name] = field(default_factory=list)

@dataclass
class Binop(Expression):
    left: [Expression] = field(default_factory=list)
    operator: str = field(default_factory='')
    right: List[Expression] = field(default_factory=list)

@dataclass
class FunctionBody(Statement):
    params: List[Literal] = field(default_factory=list)
    stmtlist: List[Statement] = field(default_factory=list)

@dataclass
class Function(Statement):
    value: Name
    funcbody: FunctionBody

@dataclass
class DefFunction(Statement):
    function: Function
    local: bool = field(default_factory=bool)

@dataclass
class CallFunction(Statement):
    value: Name
    explist: List[Expression] = field(default_factory=list)

@dataclass
class Do(Statement):
    stmtlist: List[Statement] = field(default_factory=list)

@dataclass
class Program(Statement):
    stmtlist: List[Statement] = field(default_factory=list)

@dataclass
class Assignment(Statement):
    varlist: List[Var] = field(default_factory=list)
    explist: List[Expression] = field(default_factory=list)
    local: bool = field(default_factory=bool)

@dataclass
class While(Statement):
    cond: Expression
    stmtlist: List[Statement] = field(default_factory=list)

@dataclass
class Return(Statement):
    exprlist: List[Expression] = field(default_factory=list)

@dataclass
class Break(Statement):
    pass

@dataclass
class If(Statement):
    cond: Expression
    stmtlist: List[Statement] = field(default_factory=list)
    elsepart: List[Statement] = field(default_factory=list)

@dataclass
class For(Statement):
    assign: Assignment
    limit: Expression
    step: Expression
    stmtlist: List[Statement] = field(default_factory=list)

@dataclass
class Forin(Statement):
    namelist: List[Literal] = field(default_factory=list)
    exprlist: List[Expression] = field(default_factory=list)
    stmtlist: List[Statement] = field(default_factory=list)

class LuaParser(sly.Parser):
    debugfile = 'AFD.txt'
    tokens = LuaLexer.tokens

    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'LT', 'GT', 'LE', 'GE', 'NE', 'EQ'),
        ('left', '+', '-'),
        ('left', '*', '/', '%'),
        ('left', 'NOT', 'UMINUS'),
        ('right', 'CONCAT'),
        ('right', '^'),
    )

    @_("stmtlist")
    def start(self, p):
        return Program(p.stmtlist)

    @_("empty")
    def stmtlist(self, p):
        return []

    @_("stmtlist stmt ';'")
    def stmtlist(self, p):
        return p.stmtlist + [p.stmt]

    @_("varlist '=' explist")
    def stmt(self, p):
        return Assignment(p.varlist, p.explist)

    @_("functioncall")
    def stmt(self, p):
        return p.functioncall

    @_("DO stmtlist END")
    def stmt(self, p):
        return Do(p.stmtlist)

    @_("WHILE exp DO stmtlist END")
    def stmt(self, p):
        return While(p.exp, p.stmtlist)

    @_("IF exp THEN stmtlist elsepart END")
    def stmt(self, p):
        return If(p.exp, p.stmtlist, p.elsepart)

    @_("RETURN")
    def stmt(self, p):
        return Return()

    @_("RETURN explist")
    def stmt(self, p):
        return Return(p.explist)

    @_("BREAK")
    def stmt(self, p):
        return Break()

    @_("FOR NAME '=' exp ',' exp DO stmtlist END")
    def stmt(self, p):
        return For(Assignment([Var(p.NAME)], [p.exp0]), p.exp1, Number(1), p.stmtlist)

    @_("FOR NAME '=' exp ',' exp ',' exp DO stmtlist END")
    def stmt(self, p):
        return For(Assignment([Var(p.NAME)], [p.exp0]), p.exp1, p.exp2, p.stmtlist)

    @_("FOR namelist IN explist DO stmtlist END")
    def stmt(self, p):
        return Forin(p.namelist, p.explist, p.stmtlist)

    @_("FUNCTION function")
    def stmt(self, p):
        return DefFunction(p.function)

    @_("LOCAL FUNCTION function")
    def stmt(self, p):
        return DefFunction(p.function,True)

    @_("LOCAL namelist")
    def stmt(self, p):
        Nilcout = []
        for i in p.namelist:
            Nilcout.append(Nil())
        return Assignment(p.namelist,Nilcout,True)

    @_("LOCAL namelist '=' explist")
    def stmt(self, p):
        return Assignment(p.namelist,p.explist, True)

    @_("empty")
    def elsepart(self, p):
        return []

    @_("ELSE stmtlist")
    def elsepart(self, p):
        return p.stmtlist

    @_("ELSEIF exp THEN stmtlist elsepart")
    def elsepart(self, p):
        return [If(p.exp,p.stmtlist,p.elsepart)]

    @_("NAME funcbody")
    def function(self, p):
        return Function(Name(p.NAME),p.funcbody)

    @_("NAME ':' NAME funcbody")
    def function(self, p):
        return Function(Name(p.NAME0+'.'+p.NAME1),p.funcbody)

    @_("'(' params ')' stmtlist END")
    def funcbody(self, p):
        return FunctionBody(p.params,p.stmtlist)

    @_("empty")
    def params(self, p):
        return []

    @_("namelist")
    def params(self, p):
        return p.namelist

    @_("NAME")
    def namelist(self, p):
        return [Name(p.NAME)]

    @_("NAME ',' namelist")
    def namelist(self, p):
        return p.namelist + [Name(p.NAME)]

    @_("var")
    def varlist(self, p): 
        return [p.var]

    @_("var ',' varlist")
    def varlist(self, p):
        return p.varlist + [p.var]

    @_("NAME")
    def var(self, p):
        return Var(p.NAME)

    @_("prefixexp '[' exp ']'")
    def var(self, p):
        return CallTable(p.prefixexp,p.exp)

    @_("prefixexp '.' NAME")
    def var(self, p):
        return prefixexp + [Var(p.NAME)]

    @_("exp")
    def explist(self, p):
        return [p.exp]

    @_("exp ',' explist")
    def explist(self, p):
        return p.explist + [p.exp]

    @_("exp OR exp",
        "exp AND exp",
        "exp LT exp",
        "exp LE exp",
        "exp GT exp",
        "exp GE exp",
        "exp EQ exp",
        "exp NE exp",
        "exp CONCAT exp",
        "exp '+' exp",
        "exp '-' exp",
        "exp '*' exp",
        "exp '/' exp",
        "exp '%' exp",
        "exp '^' exp")
    def exp(self, p):
        return Binop(p.exp0,p[1],p.exp1)

    @_("'-' exp %prec UMINUS",
        "NOT exp")
    def exp(self, p):
        try:
            if p.NOT:
                return Not(p.exp)
        except AttributeError:
            pass
        try:
            if p[0] == '-':
                p.exp.value = -p.exp.value
                return p.exp
        except AttributeError:
            pass

    '''@_("exp '!'")
    def exp(self, p):
        pass'''

    @_("NIL",
        "TRUE",
        "FALSE",
        "STRING")
    def exp(self, p):
        try:
            if p.TRUE:
                return Boolean(True)
        except AttributeError:
            pass
        try:
            if p.FALSE:
                return Boolean(False)
        except AttributeError:
            pass
        try:
            if p.STRING:
                return String(p.STRING)
        except AttributeError:
            pass
        try:
            if p.NIL:
                return Nil()
        except AttributeError:
            pass

    @_("NUMBER")
    def exp(self, p):
        return Number(p.NUMBER)

    @_("FUNCTION funcbody")
    def exp(self, p):
        return p.funcbody

    @_("prefixexp")
    def exp(self, p):
        return p.prefixexp

    @_("'{' fieldlist '}'")
    def exp(self, p):
        return Table(p.fieldlist)

    @_("NAME")
    def prefixexp(self, p):
        return Name(p.NAME)

    @_("prefixexp '[' exp ']'")
    def prefixexp(self, p):
        return CallTable(p.exp,p.prefixexp)

    @_("prefixexp '.' NAME")
    def prefixexp(self, p):
        p.prefixexp.value += '.'+ p.NAME
        return p.prefixexp

    @_("functioncall")
    def prefixexp(self, p):
        return p.functioncall

    @_("'(' exp ')'")
    def prefixexp(self, p):
        return p.exp

    @_("prefixexp args")
    def functioncall(self, p):
        return CallFunction(p.prefixexp,p.args)

    @_("prefixexp '.' NAME args")
    def functioncall(self, p):
        p.prefixexp._add(p.NAME)
        return CallFunction(p.prefixexp,p.args)

    @_("'(' ')'")
    def args(self, p):
        return []

    @_("'(' explist ')'")
    def args(self, p):
        return p.explist

    @_("'{' fieldlist '}'")
    def args(self, p):
        return Table(p.fieldlist)

    @_("empty")
    def fieldlist(self, p):
        return []
    
    @_("field")
    def fieldlist(self, p):
        return [p.field]

    @_("field ',' fieldlist")
    def fieldlist(self, p):
        return p.fieldlist + [p.field]

    @_("'[' exp ']' '=' exp")
    def field(self, p):
        return TableData(p.exp0,p.exp1)

    @_("NAME '=' exp")
    def field(self, p):
        return TableData(Name(p.NAME),p.exp)

    @_("")
    def empty(self, p):
        pass

    def error(self, p):
        if p:
            print(p.lineno, "Error de sintaxis en la entrada en el token '%s'" % p.value)
        else:
            print('EOF', 'Error de sintaxis. No mas entrada.')

# ----------------------------------------
# NO MODIFIQUE NADA A CONTINUACION
# ----------------------------------------

### AST ###

import os
os.environ["PATH"] += os.pathsep + 'C:/Graphviz/bin'

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
        self.dot = Digraph('AST', comment='AST para MiniLua')
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
    
    def visit(self, node: Expression):
        name = self._id()
        label = 'Expression\nvalue: {}'.format(node)
        self.dot.node(name, label, color='orange')   # color amarillo
        return name
    
    def visit(self, node: Statement):
        name = self._id()
        label = 'Statement\nvalue: {}'.format(node)
        self.dot.node(name, label, color='orange')   # color amarillo
        return name

    def visit(self, node: Number, type=''):
        name = self._id()
        label = '{} constant\nvalue: {}'.format(type,node.value)
        self.dot.node(name, label, color='orange')   # color amarillo
        return name
    
    def visit(self, node: Var, type=''):
        name = self._id()
        label = 'variable\nname: {}'.format(node.value)
        self.dot.node(name, label, color='darkolivegreen3')
        return name
    
    def visit(self, node: Name, type=''):
        name = self._id()
        label = '{} name: {}'.format(type,node.value)
        self.dot.node(name, label, color='cyan3')
        return name
    
    def visit(self, node: String, type=''):
        name = self._id()
        label = '{} string: {}'.format(type,node.value)
        self.dot.node(name, label, color='yellow')
        return name
    
    def visit(self, node: Boolean, type=''):
        name = self._id()
        label = '{}'.format(node.value)
        self.dot.node(name, label, color='orange')
        return name
    
    def visit(self, node: Nil, type=''):
        name = self._id()
        label = 'Nil'
        self.dot.node(name, label, color='orange')
        return name
    
    def visit(self, node: Not, type=''):
        name = self._id()
        label = 'Not'
        self.dot.node(name, label, color='coral')
        self.dot.edge(name, self.visit(node.value))
        return name
    
    def visit(self, node: Table, type=''):
        name = self._id()
        label = 'Table'
        self.dot.node(name, label, color='lightblue')
        for i in range(len(node.data)):
            self.dot.edge(name, self.visit(node.data[i]))
        return name
    
    def visit(self, node: TableData, type=''):
        name = self._id()
        label = 'Data'
        self.dot.node(name, label, color='orange')
        self.dot.edge(name, self.visit(node.value))
        self.dot.edge(name, self.visit(node.exp))
        return name

    def visit(self, node: Binop, type=''):
        name = self._id()
        label = '{} binop\nop: {}'.format(type,node.operator)
        self.dot.node(name, label, color='lightblue')
        self.dot.edge(name, self.visit(node.left))
        self.dot.edge(name, self.visit(node.right))
        return name

    def visit(self, node: Assignment, type=''):
        name = self._id()
        if node.local:
            label = 'Local assign'
        else:
            label = 'assign'
        self.dot.node(name, label, color='lightblue')
        for i in range(len(node.varlist)):
            self.dot.edge(name, self.visit(node.varlist[i]))
            self.dot.edge(name, self.visit(node.explist[i]))
        return name

    def visit(self, node: While, type=''):
        name = self._id()
        label = 'While'
        self.dot.node(name, label, color='lightblue')
        self.dot.edge(name, self.visit(node.cond))
        for i in range(len(node.stmtlist)):
            self.dot.edge(name, self.visit(node.stmtlist[i]))
        return name

    def visit(self, node: Return, type=''):
        name = self._id()
        label = 'Return'
        self.dot.node(name, label, color='pink')
        for i in range(len(node.exprlist)):
            self.dot.edge(name, self.visit(node.exprlist[i]))
        return name
    
    def visit(self, node: Break):
        name = self._id()
        label = 'Break'
        self.dot.node(name, label, color='pink')
        return name
    
    def visit(self, node: If, type=''):
        name = self._id()
        label = 'If\nthen, cond, else:'
        self.dot.node(name, label, color='lightblue')
        for i in range(len(node.stmtlist)):
            self.dot.edge(name, self.visit(node.stmtlist[i]))
        self.dot.edge(name, self.visit(node.cond, 'cond:\n'))
        for i in range(len(node.elsepart)):
            self.dot.edge(name, self.visit(node.elsepart[i]))
        return name
    
    def visit(self, node: For, type=''):
        name = self._id()
        label = 'For'
        self.dot.node(name, label, color='lightblue')
        self.dot.edge(name, self.visit(node.limit))
        self.dot.edge(name, self.visit(node.step))
        self.dot.edge(name, self.visit(node.assign))
        for i in range(len(node.stmtlist)):
            self.dot.edge(name, self.visit(node.stmtlist[i]))
        return name
    
    def visit(self, node: Forin, type=''):
        name = self._id()
        label = 'Forin'
        self.dot.node(name, label, color='lightblue')
        for i in range(len(node.namelist)):
            self.dot.edge(name, self.visit(node.namelist[i]))
        for i in range(len(node.exprlist)):
            self.dot.edge(name, self.visit(node.exprlist[i]))
        for i in range(len(node.stmtlist)):
            self.dot.edge(name, self.visit(node.stmtlist[i]))
        return name

    def visit(self, node: CallTable, type=''):
        name = self._id()
        label = '{} CallTable'.format(type)
        self.dot.node(name, label, color='limegreen')
        self.dot.edge(name, self.visit(node.field, 'field\n'))
        self.dot.edge(name, self.visit(node.table, 'table\n'))
        return name
    
    def visit(self, node: CallFunction, type=''):
        name = self._id()
        label = 'CallFunction'
        self.dot.node(name, label, color='limegreen')
        self.dot.edge(name, self.visit(node.value, 'call\n'))
        for i in range(len(node.explist)):
            self.dot.edge(name, self.visit(node.explist[i], 'arg\n'))
        return name

    def visit(self, node: DefFunction, type=''):
        name = self._id()
        if node.local:
            label = 'DefLocalFunction'
        else:
            label = 'DefFunction'
        self.dot.node(name, label, color='limegreen')
        self.dot.edge(name, self.visit(node.function))
        return name
    
    def visit(self, node: Function, type=''):
        name = self._id()
        label = 'Function'
        self.dot.node(name, label, color='lightblue')
        self.dot.edge(name, self.visit(node.value, 'func\n'))
        self.dot.edge(name, self.visit(node.funcbody))
        return name
    
    def visit(self, node: FunctionBody, type=''):
        name = self._id()
        label = 'Function\nbody:'
        self.dot.node(name, label, color='orange')
        for i in range(len(node.params)):
            self.dot.edge(name, self.visit(node.params[i],'args\n'))
        for i in range(len(node.stmtlist)):
            self.dot.edge(name, self.visit(node.stmtlist[i]))
        return name
    
    def visit(self, node: Program, type=''):
        name = self._id()
        label = 'Program'
        self.dot.node(name, label, color='green')
        for i in range(len(node.stmtlist)):
            self.dot.edge(name, self.visit(node.stmtlist[i]))
        return name

### AST ###