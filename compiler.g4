grammar compiler;

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
    | COMMENT;

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
	| pointer
	| RETURN expr
	| address
	| variable
	| LPAREN expr RPAREN
	| ('++' | '--') expr
	| expr ('++' | '--')
	| expr '&&' expr
	| expr LSHIFT expr
	| expr RSHIFT expr
	| expr AMPERSAND expr
	| expr BITOR expr
	| expr BITXOR expr
	| expr BITNOT expr;

variable: ID;

main: TYPE 'main' LPAREN RPAREN LBRACKET stat* RBRACKET;

newVariable:
	CONST* TYPE variable
	| CONST* TYPE variable '=' expr
	| CONST* TYPE pointer '=' address;

pointer: POINTER+ variable;

address: AMPERSAND ID;

assignment:
	ID '=' expr
	| expr '=' expr;

TYPE: 'int' | 'float' | 'char' | 'string' | 'bool' | 'void';

literal: FLOAT | INT | CHAR | STRING | BOOL;

WS: [ \t\n\r]+ -> skip; // toss out whitespace
INCLUDE: '#include';
RETURN: 'return';
BREAK: 'break';
CONTINUE: 'continue';
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
POINTER: '*';
CONST: 'const';
SQUOTE: ['];
DQUOTE: ["];
DSLASH: '/' '/';
CHAR: SQUOTE . SQUOTE | SQUOTE '\\' . SQUOTE;
ID: [_a-zA-Z][_a-zA-Z0-9.]*;
BOOL: 'true' | 'false';
FLOAT: [-]?[0-9]* '.' [0-9]*;
INT: ('-')? [0-9]+; // TODO: handle '+' before an integer
STRING: ["] .*? ["];
LSHIFT: '<<';
RSHIFT: '>>';
AMPERSAND: '&';
BITOR: '|';
BITXOR: '^';
BITNOT: '~';