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
    : 'var' IDENT '=' expr ';'
    ;

assign
    : expr '=' expr ';'
    ;

exprStmt: expr ';';

stmt
    : exprStmt
    | varDecl
    | assign
    ;

expr
    : expr '+' expr # additiveBinopExpr
    | expr '<' expr # logicalBinopExpr
    | INT_LITERAL # intLit
    | BOOL_LITERAL # boolLit
    | STRINGLITERAL # strLit
    | IDENT '(' commaSeparatedExprs? ')' # funCall
    | IDENT # reference
    ;

commaSeparatedExprs: expr (',' expr)*;

STRINGLITERAL: '"' ~["\\\r\n]* '"';
BOOL_LITERAL: 'true' | 'false';
INT_LITERAL: [1-9][0-9]*;
IDENT: [a-zA-Z_]+[a-zA-Z_0-9]*;
WS: [ \n\t\r]+ -> skip;
