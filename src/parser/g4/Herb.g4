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
    : 'fn' IDENT '(' ( argDecl (',' argDecl)* )? ')' ('->' retTyp=typ)? block
    ;

varDecl
    : 'var' IDENT '=' expr ';'
    ;

argDecl: IDENT ':' typ;

assign
    : expr '=' expr ';'
    ;

exprStmt: expr ';';

ifStmt: 'if' expr thenBlock=block ( 'else' (elseIf=ifStmt | elseBlock=block) )?;

whileStmt: 'while' expr block;

stmt
    : exprStmt
    | varDecl
    | assign
    | ifStmt
    | whileStmt
    ;

expr
    : INT_LITERAL #intLit
    | BOOL_LITERAL #boolLit
    | STRINGLITERAL #strLit
    | IDENT #reference
    | '(' expr ')' #parenExpr
    | IDENT '(' commaSeparatedExprs? ')' #funCall
    | op=('-' | '!') expr #unaryopExpr
    | expr op=('*' | '/' | '%' | '&') expr #binopExpr
    | expr op=('+' | '-' | '|') expr #binopExpr
    | expr op=('<' | '<=' | '==' | '!=' | '>' | '>=' ) expr #binopExpr
    | expr op='&&' expr #binopExpr
    | expr op='||' expr #binopExpr
    ;

typ
    : IDENT #typLit
    | '(' ( typ (',' typ)* )? ')' '->' typ #typFunc
    ;


commaSeparatedExprs: expr (',' expr)*;
block: '{' stmt* '}';


STRINGLITERAL: '"' ~["\\\r\n]* '"';
BOOL_LITERAL: 'true' | 'false';
INT_LITERAL: [0-9]+;
IDENT: [a-zA-Z_]+[a-zA-Z_0-9]*;
WS: [ \n\t\r]+ -> skip;
