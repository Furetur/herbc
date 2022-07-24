grammar Herb;

prog : importDecl*;

importDecl
    : 'import' importPath ';' #importWithoutAlias
    | 'import' IDENT '=' importPath ';' #importWithAlias
    ;

importPath
    : IDENT ('.' IDENT)* #absImportPath
    | '.' IDENT ('.' IDENT) #relImport
    ;

IDENT: [a-zA-Z_]+[a-zA-Z_0-9]*;
WS: [ \n\t\r]+ -> skip;
