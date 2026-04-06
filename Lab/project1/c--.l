%{
#include <stdio.h>
#include <string.h>

#define HASHLEN 1024

int nline=1;

struct id_entry
{
    char *id;
    struct id_entry *next; /* next entry on hash chain */
};

struct id_entry *id_hash_table[HASHLEN];

int hash(char *name)
{
    int h=*name++;
    while(*name)
        //h=h<<4+*name++;
        h=(h<<4)+(*name++);
    return h;
}

char *insert_id(char *name)
{
    int h=hash(name)&(HASHLEN-1);
    struct id_entry *p=id_hash_table[h];
    while(p&&(strcmp(p->id,name)!=0))
        p=p->next;
    if(p)
        return p->id;
    p=(struct id_entry *)malloc(sizeof *p);
    p->id=(char *)malloc(strlen(name)+1);
    strcpy(p->id,name);
    p->next=id_hash_table[h];
    id_hash_table[h]=p; /* 新名字在表头 */
    return p->id;
}

char out(char *id,char *val)
{
    if(id&&val)
        fprintf(yyout,"%s %s\n",id,val);
    return -1;
}
%}

delim [ \t]
ws {delim}+
leter [A-Za-z]
digit [0-9]
id {leter}({leter}|{digit})*
number {digit}+(\.{digit}+)?(E[+\-]?{digit}+)?
comment (\#[^\n]*)|(\/\*(((\*)*[^\*\/]+(\/)*)*|(\*)*|(\/)*)\*\/)|(\/\/[^\n]*)
sentence \"(.)*\"
chartype (\'([^\n]|\n)\')|\'\'
special [\@\~\\\$\`]

PUN [(){};,.=+\-*/]
CHAR_CONST '(\\.|[^\\'])'
STRING \"(\\.|[^\\"])*\"

%%

"\n" {nline++;}
"\r\n" {nline++;}
{comment} {/*对预处理和注释部分没有动作和返回值*/}
{ws} {/*对空白串没有动作和返回值*/}
{number} {out("NUM",yytext);}
"__stdcall" {out("KEYWORD",yytext);}
"__cdecl" {out("KEYWORD",yytext);}
"if" {out("KEYWORD",yytext);}
"int" {out("KEYWORD",yytext);}

"long" {out("KEYWORD",yytext);}

"void" {out("KEYWORD",yytext);}
"char" {out("KEYWORD",yytext);}
"else" {out("KEYWORD",yytext);}
"while" {out("KEYWORD",yytext);}
"return" {out("KEYWORD",yytext);}
{id} {out("ID",yytext);}
"<=" {out("REL_OP",yytext);}
">=" {out("REL_OP",yytext);}
"<" {out("REL_OP",yytext);}
">" {out("REL_OP",yytext);}
"!=" {out("REL_OP",yytext);}
"==" {out("REL_OP",yytext);}
[+-] {out("PUN",yytext);}

{PUN} {out("PUN",yytext);}
{CHAR_CONST} {out("CHAR_CONST",yytext);}
{STRING} {out("STRING",yytext);}

. {fprintf(stderr,"ERR: line %d unknown %s",nline,yytext);return yytext[0];}

%%

//error(char *m)
//{
//    fprintf(stderr,"%s\n",m);
//    exit(1); /*非正常终止*/
//}

int yywrap()
{
    return 1;
}

int main(int argc,char **argv)
{
    if(argc>=3)
    {
        if(argc>3)
            fprintf(stderr,"Warn: param num > 2, only use first 2 (%s %s %s)",argv[0],argv[1],argv[2]);
        if((yyin=fopen(argv[1],"r")))
            if((yyout=fopen(argv[2],"w")))
            {
                yylex();
                fclose(yyout),fclose(yyin);
                return 0;
            }
            else
                fprintf(stderr,"ERR: can't open output %s",argv[2]);
        else
            fprintf(stderr,"ERR: can't open input %s",argv[1]);
    }
    else
        fprintf(stderr,"ERR: param num must be 2 (Usage: %s in out)",argv[0]);
    return -1;
}
