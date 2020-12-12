def showAST(source):
    '''
    Transform the source code {source} in a Abstract Syntax Tree (AST).\n
    Shows the AST.
    '''
    from Parser import LuaParser
    from Parser import ASTRender
    from Lexer import LuaLexer

    l = LuaLexer()
    p = LuaParser()
    root = p.parse(l.tokenize(source))
    dot = ASTRender()
    root.accept(dot)
    dot.dot.view()

def parseSource(source):
    '''
    Transform the source code {source} in a Abstract Syntax Tree (AST).\n
    Shows the results of the parser.
    '''
    from Parser import LuaParser
    from Lexer import LuaLexer

    l = LuaLexer()
    p = LuaParser()
    root = p.parse(l.tokenize(source))
    print(root)

def tokenizeSource(source):
    '''
    Transform the source code {source} in a list of Tokens.\n
    Prints the list in console.
    '''
    from Lexer import LuaLexer

    l = LuaLexer()
    for tok in l.tokenize(source):
        print(tok)

def main(argv):
    if len(argv) != 3:
        raise SystemExit(f'Usage: {argv[0]} -action filename\nAllowed actions:\n0: Tokenize, Token, T.\n1: Parserize, Parse, P.\n2: ShowAST, SAST, S.\n3: RunLua, Run, R.\n')
    else:
        with open(argv[2]) as file:
            if argv[1] == '0' or argv[1].lower() == '-tokenize' or argv[1].lower() == '-token' or argv[1].lower() == '-t':
                tokenizeSource(file.read())
            elif argv[1] == '1' or argv[1].lower() == '-parserize' or argv[1].lower() == '-parse' or argv[1].lower() == '-p':
                parseSource(file.read())
            elif argv[1] == '2' or argv[1].lower() == '-showast' or argv[1].lower() == '-sast' or argv[1].lower() == '-s':
                showAST(file.read())
            elif argv[1] == '3' or argv[1].lower() == '-runlua' or argv[1].lower() == '-run' or argv[1].lower() == '-r':
                raise SystemExit("WIP")
            else:
                raise SystemExit(f'\nAction: [{argv[1]}] not recognized.\nAllowed actions:\n0: Tokenize, Token, T.\n1: Parserize, Parse, P.\n2: ShowAST, SAST, S.\n3: RunLua, Run, R.\n')
        

if __name__ == "__main__":
    import sys
    main(sys.argv)