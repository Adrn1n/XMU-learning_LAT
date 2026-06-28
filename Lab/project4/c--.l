%{
#include "c--.tab.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

    int line_no = 1;

    static char *my_strdup(const char *s)
    {
        char *p = (char *)malloc(strlen(s) + 1);
        if (!p)
        {
            fprintf(stderr, "out of memory\n");
            exit(1);
        }
        strcpy(p, s);
        return p;
    }
%}

%option noyywrap

%x COMMENT

D [0-9]
L [A-Za-z_]
ID {L}({L}|{D})*
NUM {D}+
CHARC \'(\\.|[^\\'\n])\'
STRING \"(\\.|[^\\\"\n])*\"

%%

[ \t\r]+ ;

\n {
line_no++;
}

"//".* ;

"/*" {
BEGIN(COMMENT);
}
<COMMENT>"*/" {
BEGIN(INITIAL);
}
<COMMENT>\n {
line_no++;
}
<COMMENT>. ;
<COMMENT><<EOF>> {
    fprintf(stderr, "Lexical error at line %d: unterminated comment\n", line_no);
    return 0;
}

"int" {
return INT;
}
"char" {
return CHAR;
}
"void" {
return VOID;
}
"long" {
return LONG;
}

"if" {
return IF;
}
"else" {
return ELSE;
}
"while" {
return WHILE;
}
"return" {
return RETURN;
}

"==" {
return EQ;
}
"!=" {
return NE;
}
"<=" {
return LE;
}
">=" {
return GE;
}
"<" {
return LT;
}
">" {
return GT;
}

"+" {
return ADD;
}
"-" {
return SUB;
}
"*" {
return MUL;
}
"/" {
return DIV;
}
"%" {
return MOD;
}

"=" {
return ASSIGN;
}

"(" {
return LP;
}
")" {
return RP;
}
"{" {
return LB;
}
"}" {
return RB;
}
"," {
return COMMA;
}
";" {
return SEMI;
}

{NUM} {
    yylval.ival = atoi(yytext);
    return NUM;
}

{CHARC} {
    yylval.sval = my_strdup(yytext);
    return CHAR_CONST;
}

{STRING} {
    yylval.sval = my_strdup(yytext);
    return STRING_CONST;
}

{ID} {
    yylval.sval = my_strdup(yytext);
    return ID;
}

. {
    fprintf(stderr, "Lexical error at line %d: unknown character '%s'\n", line_no, yytext);
}

%%
