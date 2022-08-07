grammar Herb;

prog : importDecl* topLevelDecl* EOF;

topLevelDecl
    : funcDecl
    | varDecl
    ;

importDecl
    : 'import' importPath ';' #importWithoutAlias
    | 'import' IDENT '=' importPath ';' #importWithAlias
    ;

importPath
    : IDENT ('.' IDENT)* #absImportPath
    | '.' IDENT ('.' IDENT)* #relImportPath
    ;

funcDecl
    : 'fn' IDENT '(' ')' '{' stmt* '}'
    ;

varDecl
    : 'const' IDENT '=' expr ';'
    ;

stmt
    : expr ';' # exprStmt
    | varDecl # varDeclStmt
    ;

expr
    : INT_LITERAL # intLit
    | BOOL_LITERAL # boolLit
    | IDENT '(' commaSeparatedExprs? ')' # funCall
    | IDENT # reference
    ;

commaSeparatedExprs: expr (',' expr)*;

BOOL_LITERAL: 'true' | 'false';
INT_LITERAL: [1-9][0-9]*;
IDENT: [a-zA-Z_]+[a-zA-Z_0-9]*;
WS: [ \n\t\r]+ -> skip;
