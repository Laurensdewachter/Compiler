grammar compiler;

/** The start rule; begin parsing here. */
prog: stat+;

LINE_COMMENT: '//' ~[\r\n]*;
COMMENT: '/*' .*? '*/';

stat:
	expr SEMI
	| newVariable SEMI
    | assignment SEMI
    | LINE_COMMENT
    | COMMENT;

expr:
	expr ('*' | '/') expr
	| expr '%' expr
	| expr ('+' | '-') expr
	| ('!' | '-' | '+') expr
	| expr ('<' | '>') expr
	| expr '||' expr
	| expr '==' expr
	| expr ('<=' | '>=' | '!=') expr
	| literal
	| pointer
	| address
	| variable
	| '(' expr ')'
	| ('++' | '--') expr
	| expr ('++' | '--')
	| expr '&&' expr;


variable: ID;

newVariable:
	CONST* TYPE variable
	| CONST* TYPE variable '=' expr
	| CONST* TYPE pointer '=' address
	| CONST* TYPE pointer '=' ID;

pointer: POINTER+ variable;

address: ADDRESS ID;

assignment:
	POINTER* variable '=' expr
	| POINTER* ID '=' expr
	| expr '=' expr;

TYPE: 'int' | 'float' | 'char' | 'string' | 'bool' | 'void';

literal: FLOAT | INT | CHAR | STRING | BOOL;

WS: [ \t\n\r]+ -> skip; // toss out whitespace
INCLUDE: '#include';
BREAK: 'break';
CONTINUE: 'continue';
RETURN: 'return';
FOR: 'for';
SEMI: ';';
COMMA: ',';
IF: 'if';
WHILE: 'while';
ELIF: 'else if';
ELSE: 'else';
LBRACKET: '{';
RBRACKET: '}';
LPAREN: '(';
RPAREN: ')';
CONST: 'const';
SQUOTE: ['];
DQUOTE: ["];
DSLASH: '/' '/';
CHAR: SQUOTE . SQUOTE | SQUOTE '\\' . SQUOTE;
ID: [_a-zA-Z][_a-zA-Z0-9.]*;
BOOL: 'true' | 'false';
FLOAT: [-]?[0-9]* '.' [0-9]*;
INT: [-]?[1-9][0-9]* | '0';
STRING: ["] .*? ["];
POINTER: '*';
ADDRESS: '&';