grammar compiler;

WS: [ \t\n\r]+ -> skip; // toss out whitespace
/** The start rule; begin parsing here. */
prog: stat+;

LINE_COMMENT: '//' ~[\r\n]*;
COMMENT: '/*' .*? '*/';

stat:
	expr SEMI
	| main
	| newVariable SEMI
    | assignment SEMI
    | LINE_COMMENT
    | COMMENT
    | typedef;

typedef: TYPEDEF TYPE typedefname SEMI;
typedefname: ID | TYPE;

expr:
	expr ('*') expr
	| expr ('/') expr
	| expr '%' expr
	| expr ('+' | '-') expr
	| ('!' | '-' | '+') expr
	| expr ('<' | '>') expr
	| expr '||' expr
	| expr '==' expr
	| expr ('<=' | '>=' | '!=') expr
	| literal
	| printf
	| pointer
	| RETURN expr
	| address
	| variable
	| LPAREN expr RPAREN
	| unaryminusminus
	| unaryplusplus
	| expr '&&' expr
	| expr LSHIFT expr
	| expr RSHIFT expr
	| expr AMPERSAND expr
	| expr BITOR expr
	| expr BITXOR expr
	| expr BITNOT expr;


unaryplusplus: PLUSPLUS variable
    | variable PLUSPLUS;

unaryminusminus: MINUSMINUS variable
    | variable MINUSMINUS;

variable: ID;

printf: PRINTF LPAREN STRING (COMMA expr)* RPAREN;

main: TYPE 'main' LPAREN RPAREN LBRACKET stat* RBRACKET;

newVariable:
	CONST* (TYPE | ID) variable
	| CONST* (TYPE | ID) variable '=' expr
	| CONST* (TYPE | ID) pointer '=' address
	| CONST* (TYPE | ID) pointer '=' expr;

pointer: POINTER+ variable;

address: AMPERSAND ID;

assignment:
	ID '=' expr
	| expr '=' expr;

TYPE: 'int' | 'float' | 'char' | 'string' | 'bool' | 'void';

literal: FLOAT | INT | CHAR | STRING | BOOL;

INCLUDE: '#include';
PRINTF: 'printf';
RETURN: 'return';
BREAK: 'break';
CONTINUE: 'continue';
FOR: 'for';
SEMI: ';';
COMMA: ',';
IF: 'if';
WHILE: 'while';
TYPEDEF: 'typedef';
ELIF: 'else if';
ELSE: 'else';
LBRACKET: '{';
RBRACKET: '}';
LPAREN: '(';
RPAREN: ')';
CONST: 'const';
ID: [_a-zA-Z][_a-zA-Z0-9.]*;
POINTER: '*';
PLUSPLUS: '++';
MINUSMINUS: '--';
SQUOTE: ['];
DQUOTE: ["];
DSLASH: '/' '/';
CHAR: SQUOTE . SQUOTE | SQUOTE '\\' . SQUOTE;
BOOL: 'true' | 'false';
FLOAT: [-]?[0-9]* '.' [0-9]*;
INT: [0] | [1-9][0-9]*; // TODO: handle '+' before an integer
STRING: ["] .*? ["];
LSHIFT: '<<';
RSHIFT: '>>';
AMPERSAND: '&';
BITOR: '|';
BITXOR: '^';
BITNOT: '~';
