grammar Herb;

prog : importDecl* funcDecl* EOF;

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

stmt
    : expr ';' # exprStmt
    ;

expr
    : INT_LITERAL # intLit
    | IDENT '(' commaSeparatedExprs? ')' # funCall
    ;

commaSeparatedExprs: expr (',' expr)*;

INT_LITERAL: [1-9][0-9]*;
IDENT: [a-zA-Z_]+[a-zA-Z_0-9]*;
WS: [ \n\t\r]+ -> skip;
