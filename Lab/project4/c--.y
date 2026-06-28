%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int yylex(void);
extern int line_no;
extern FILE *yyin;

void yyerror(const char *s);

#define MAX_PARAMS 64

typedef enum
{
    TYPE_INT = 1,
    TYPE_CHAR,
    TYPE_VOID,
    TYPE_STRING,
    TYPE_ERROR
} TypeKind;

typedef enum
{
    SYM_VAR = 1,
    SYM_FUNC
} SymbolKind;

typedef struct TypeList
{
    int n;
    int types[MAX_PARAMS];
} TypeList;

typedef struct Symbol
{
    char *name;
    SymbolKind kind;
    TypeKind type;
    int scope;
    int param_count;
    TypeKind params[MAX_PARAMS];
    struct Symbol *next;
} Symbol;

static Symbol *symbol_table = NULL;
static int current_scope = 0;
static int error_count = 0;
static TypeKind current_decl_type = TYPE_ERROR;
static TypeKind current_func_return = TYPE_ERROR;
static Symbol *current_func_symbol = NULL;
static char *pending_name = NULL;
static TypeKind pending_type = TYPE_ERROR;
static TypeList current_params;

static char *my_strdup2(const char *s)
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

static const char *type_name(TypeKind t)
{
    switch (t)
    {
    case TYPE_INT:
        return "int";
    case TYPE_CHAR:
        return "char";
    case TYPE_VOID:
        return "void";
    case TYPE_STRING:
        return "string";
    case TYPE_ERROR:
        return "error";
    default:
        return "unknown";
    }
}

static void semantic_error(const char *msg, const char *name)
{
    if (name)
        fprintf(stderr, "Semantic error at line %d: %s '%s'\n", line_no, msg, name);
    else
        fprintf(stderr, "Semantic error at line %d: %s\n", line_no, msg);
    error_count++;
}

static void type_error2(const char *msg, TypeKind a, TypeKind b)
{
    fprintf(stderr,
            "Semantic error at line %d: %s, left is %s, right is %s\n",
            line_no, msg, type_name(a), type_name(b));
    error_count++;
}

static void enter_scope(void)
{
    current_scope++;
}

static void leave_scope(void)
{
    Symbol *p = symbol_table;
    Symbol *prev = NULL;
    while (p)
        if (p->scope == current_scope)
        {
            Symbol *del = p;

            if (prev)
                prev->next = p->next;
            else
                symbol_table = p->next;
            p = p->next;
            free(del->name);
            free(del);
        }
        else
        {
            prev = p;
            p = p->next;
        }
    current_scope--;
}

static Symbol *lookup_current_scope(const char *name)
{
    Symbol *p = symbol_table;
    while (p)
    {
        if (p->scope == current_scope && strcmp(p->name, name) == 0)
            return p;
        p = p->next;
    }
    return NULL;
}

static Symbol *lookup_symbol(const char *name)
{
    Symbol *p = symbol_table;
    Symbol *best = NULL;
    int best_scope = -1;
    while (p)
    {
        if (strcmp(p->name, name) == 0 && p->scope <= current_scope)
            if (p->scope > best_scope)
            {
                best = p;
                best_scope = p->scope;
            }
        p = p->next;
    }
    return best;
}

static Symbol *insert_symbol(const char *name, SymbolKind kind, TypeKind type)
{
    Symbol *s = (Symbol *)malloc(sizeof(Symbol));
    if (!s)
    {
        fprintf(stderr, "out of memory\n");
        exit(1);
    }
    s->name = my_strdup2(name);
    s->kind = kind;
    s->type = type;
    s->scope = current_scope;
    s->param_count = 0;
    s->next = symbol_table;
    symbol_table = s;
    return s;
}

static void declare_variable(const char *name, TypeKind type)
{
    if (type == TYPE_VOID)
    {
        semantic_error("variable cannot have type void", name);
        return;
    }
    if (lookup_current_scope(name))
    {
        semantic_error("redefinition of identifier", name);
        return;
    }
    insert_symbol(name, SYM_VAR, type);
}

static Symbol *declare_function(const char *name, TypeKind ret_type)
{
    Symbol *old;
    if (current_scope != 0)
        semantic_error("function definition is only allowed in global scope", name);
    old = lookup_current_scope(name);
    if (old)
    {
        semantic_error("redefinition of function", name);
        return old;
    }
    return insert_symbol(name, SYM_FUNC, ret_type);
}

static void reset_param_list(void)
{
    current_params.n = 0;
}

static void add_param_type(TypeKind t)
{
    if (current_params.n >= MAX_PARAMS)
    {
        semantic_error("too many parameters", NULL);
        return;
    }
    current_params.types[current_params.n++] = t;
}

static void finish_function_params(Symbol * func)
{
    if (!func)
        return;
    func->param_count = current_params.n;
    for (int i = 0; i < current_params.n; i++)
        func->params[i] = current_params.types[i];
}

static int is_integer(TypeKind t)
{
    return t == TYPE_INT;
}

static int is_comparable(TypeKind t)
{
    return t == TYPE_INT || t == TYPE_CHAR;
}

static int type_compatible(TypeKind a, TypeKind b)
{
    if (a == TYPE_ERROR || b == TYPE_ERROR)
        return 1;
    return a == b;
}

static TypeList *new_type_list(void)
{
    TypeList *list = (TypeList *)malloc(sizeof(TypeList));
    if (!list)
    {
        fprintf(stderr, "out of memory\n");
        exit(1);
    }
    list->n = 0;
    return list;
}

static TypeList *append_type(TypeList * list, TypeKind t)
{
    if (!list)
        list = new_type_list();
    if (list->n >= MAX_PARAMS)
    {
        semantic_error("too many arguments", NULL);
        return list;
    }
    list->types[list->n++] = t;
    return list;
}

static TypeKind check_identifier(const char *name)
{
    Symbol *s = lookup_symbol(name);
    if (!s)
    {
        semantic_error("undefined identifier", name);
        return TYPE_ERROR;
    }
    if (s->kind == SYM_FUNC)
    {
        semantic_error("function used as variable", name);
        return TYPE_ERROR;
    }
    return s->type;
}

static TypeKind check_function_call(const char *name, TypeList *args)
{
    Symbol *s = lookup_symbol(name);
    if (!args)
        args = new_type_list();
    if (!s)
    {
        semantic_error("undefined function", name);
        free(args);
        return TYPE_ERROR;
    }
    if (s->kind != SYM_FUNC)
    {
        semantic_error("identifier is not a function", name);
        free(args);
        return TYPE_ERROR;
    }
    if (s->param_count != args->n)
    {
        fprintf(stderr,
                "Semantic error at line %d: function '%s' expects %d argument(s), but %d provided\n",
                line_no, name, s->param_count, args->n);
        error_count++;
        free(args);
        return s->type;
    }
    for (int i = 0; i < args->n; i++)
    {
        if (!type_compatible(s->params[i], args->types[i]))
        {
            fprintf(stderr,
                    "Semantic error at line %d: argument %d of function '%s' should be %s, but %s provided\n",
                    line_no,
                    i + 1,
                    name,
                    type_name(s->params[i]),
                    type_name(args->types[i]));
            error_count++;
        }
    }
    free(args);
    return s->type;
}

static TypeKind check_arithmetic(TypeKind a, TypeKind b)
{
    if (a == TYPE_ERROR || b == TYPE_ERROR)
        return TYPE_ERROR;
    if (!is_integer(a) || !is_integer(b))
    {
        type_error2("arithmetic operands must be int", a, b);
        return TYPE_ERROR;
    }
    return TYPE_INT;
}

static TypeKind check_relation(TypeKind a, TypeKind b)
{
    if (a == TYPE_ERROR || b == TYPE_ERROR)
        return TYPE_ERROR;
    if (!is_comparable(a) || !is_comparable(b))
    {
        type_error2("relational operands must be int or char", a, b);
        return TYPE_ERROR;
    }
    if (a != b)
    {
        type_error2("relational operands should have same type", a, b);
        return TYPE_ERROR;
    }
    return TYPE_INT;
}
%}

%union
{
    int ival;
    char *sval;
    int type;
    struct TypeList *list;
}

%token INT CHAR VOID LONG %token IF ELSE WHILE RETURN

%token EQ NE LE GE LT GT %token ADD SUB MUL DIV MOD %token ASSIGN

%token LP RP LB RB COMMA SEMI

%token<ival> NUM %token<sval> ID %token<sval> CHAR_CONST %token<sval> STRING_CONST

%type<type> type_specifier %type<type> expression assignment_expression equality_expression relational_expression %type<type> additive_expression multiplicative_expression unary_expression primary_expression %type<list> argument_list argument_list_opt

%nonassoc LOWER_THAN_ELSE %nonassoc ELSE

%start program

%%

program
: external_list;

external_list
    : external |
      external_list external;

external
    : type_specifier ID
{
    pending_type = $1;
    pending_name = $2;
}
external_suffix
{
    free(pending_name);
    pending_name = NULL;
};

external_suffix
    : LP
{
    current_func_return = pending_type;
    current_func_symbol = declare_function(pending_name, pending_type);
    reset_param_list();
    enter_scope();
}
function_parameter_part RP
{
    finish_function_params(current_func_symbol);
}
function_body
{
    leave_scope();
    current_func_return = TYPE_ERROR;
    current_func_symbol = NULL;
}
|
{
    current_decl_type = pending_type;
    declare_variable(pending_name, current_decl_type);
}
optional_initializer global_declarator_more SEMI;

function_parameter_part
    : |
      VOID | parameter_list;

parameter_list
    : parameter |
      parameter_list COMMA parameter;

parameter
    : type_specifier ID
{
    if ($1 == TYPE_VOID)
        semantic_error("parameter cannot have type void", $2);
    else
    {
        declare_variable($2, $1);
        add_param_type($1);
    }
    free($2);
};

global_declarator_more
    : |
      COMMA ID
{
    declare_variable($2, current_decl_type);
    free($2);
}
optional_initializer global_declarator_more;

declaration
    : type_specifier
{
    current_decl_type = $1;
}
declarator_list SEMI;

declarator_list
    : declarator |
      declarator_list COMMA declarator;

declarator
    : ID
{
    declare_variable($1, current_decl_type);
    free($1);
}
optional_initializer;

optional_initializer
    : |
      ASSIGN expression
{
    if (!type_compatible(current_decl_type, $2))
        type_error2("initialization type mismatch", current_decl_type, $2);
};

type_specifier
    : INT
{
    $$ = TYPE_INT;
}
| LONG
{
    $$ = TYPE_INT;
}
| CHAR
{
    $$ = TYPE_CHAR;
}
| VOID
{
    $$ = TYPE_VOID;
};

function_body
    : LB block_item_list_opt RB;

compound_statement
    : LB
{
    enter_scope();
}
block_item_list_opt RB
{
    leave_scope();
};

block_item_list_opt
    : |
      block_item_list;

block_item_list
    : block_item |
      block_item_list block_item;

block_item
    : declaration |
      statement;

statement
    : expression_statement |
      compound_statement | selection_statement | iteration_statement | return_statement | error SEMI
{
    fprintf(stderr, "Recover from syntax error at line %d\n", line_no);
    yyerrok;
};

expression_statement
    : SEMI |
      expression SEMI;

selection_statement
    : IF LP expression RP statement %prec LOWER_THAN_ELSE
{
    if ($3 == TYPE_STRING || $3 == TYPE_VOID)
        semantic_error("condition expression has invalid type", NULL);
}
| IF LP expression RP statement ELSE statement
{
    if ($3 == TYPE_STRING || $3 == TYPE_VOID)
        semantic_error("condition expression has invalid type", NULL);
};

iteration_statement
    : WHILE LP expression RP statement
{
    if ($3 == TYPE_STRING || $3 == TYPE_VOID)
        semantic_error("condition expression has invalid type", NULL);
};

return_statement
    : RETURN SEMI
{
    if (current_func_return != TYPE_VOID)
        semantic_error("non-void function should return a value", NULL);
}
| RETURN expression SEMI
{
    if (current_func_return == TYPE_VOID)
        semantic_error("void function should not return a value", NULL);
    else if (!type_compatible(current_func_return, $2))
        type_error2("return type mismatch", current_func_return, $2);
};

expression
    : assignment_expression
{
    $$ = $1;
};

assignment_expression
    : ID ASSIGN assignment_expression
{
    TypeKind left_type;
    Symbol *s = lookup_symbol($1);
    if (!s)
    {
        semantic_error("undefined identifier", $1);
        $$ = TYPE_ERROR;
    }
    else if (s->kind != SYM_VAR)
    {
        semantic_error("left side of assignment is not variable", $1);
        $$ = TYPE_ERROR;
    }
    else
    {
        left_type = s->type;
        if (!type_compatible(left_type, $3))
        {
            type_error2("assignment type mismatch", left_type, $3);
            $$ = TYPE_ERROR;
        }
        else
            $$ = left_type;
    }
    free($1);
}
| equality_expression
{
    $$ = $1;
};

equality_expression
    : relational_expression
{
    $$ = $1;
}
| equality_expression EQ relational_expression
{
    $$ = check_relation($1, $3);
}
| equality_expression NE relational_expression
{
    $$ = check_relation($1, $3);
};

relational_expression
    : additive_expression
{
    $$ = $1;
}
| relational_expression LT additive_expression
{
    $$ = check_relation($1, $3);
}
| relational_expression GT additive_expression
{
    $$ = check_relation($1, $3);
}
| relational_expression LE additive_expression
{
    $$ = check_relation($1, $3);
}
| relational_expression GE additive_expression
{
    $$ = check_relation($1, $3);
};

additive_expression
    : multiplicative_expression
{
    $$ = $1;
}
| additive_expression ADD multiplicative_expression
{
    $$ = check_arithmetic($1, $3);
}
| additive_expression SUB multiplicative_expression
{
    $$ = check_arithmetic($1, $3);
};

multiplicative_expression
    : unary_expression
{
    $$ = $1;
}
| multiplicative_expression MUL unary_expression
{
    $$ = check_arithmetic($1, $3);
}
| multiplicative_expression DIV unary_expression
{
    $$ = check_arithmetic($1, $3);
}
| multiplicative_expression MOD unary_expression
{
    $$ = check_arithmetic($1, $3);
};

unary_expression
    : primary_expression
{
    $$ = $1;
}
| ADD unary_expression
{
    if ($2 != TYPE_INT && $2 != TYPE_ERROR)
    {
        semantic_error("unary + requires int operand", NULL);
        $$ = TYPE_ERROR;
    }
    else
        $$ = $2;
}
| SUB unary_expression
{
    if ($2 != TYPE_INT && $2 != TYPE_ERROR)
    {
        semantic_error("unary - requires int operand", NULL);
        $$ = TYPE_ERROR;
    }
    else
        $$ = $2;
};

primary_expression
    : ID
{
    $$ = check_identifier($1);
    free($1);
}
| NUM
{
    $$ = TYPE_INT;
}
| CHAR_CONST
{
    $$ = TYPE_CHAR;
    free($1);
}
| STRING_CONST
{
    $$ = TYPE_STRING;
    free($1);
}
| ID LP argument_list_opt RP
{
    $$ = check_function_call($1, $3);
    free($1);
}
| LP expression RP
{
    $$ = $2;
};

argument_list_opt
    :
{
    $$ = new_type_list();
}
| argument_list
{
    $$ = $1;
};

argument_list
    : assignment_expression
{
    $$ = new_type_list();
    append_type($$, $1);
}
| argument_list COMMA assignment_expression
{
    $$ = append_type($1, $3);
};

%%

void yyerror(const char *s)
{
    fprintf(stderr, "Syntax error at line %d: %s\n", line_no, s);
    error_count++;
}

int main(int argc, char **argv)
{
    if (argc != 2)
    {
        fprintf(stderr, "Usage: %s input_file\n", argv[0]);
        return 1;
    }
    yyin = fopen(argv[1], "r");
    if (!yyin)
    {
        fprintf(stderr, "Cannot open input file: %s\n", argv[1]);
        return 1;
    }
    yyparse();
    fclose(yyin);
    if (error_count == 0)
    {
        printf("No error.\n");
        return 0;
    }
    else
    {
        printf("%d error(s).\n", error_count);
        return 1;
    }
}
