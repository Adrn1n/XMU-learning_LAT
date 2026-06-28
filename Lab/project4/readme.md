<!--
语言分析技术实验4
 
1．实验目的：
c—语言的句法分析器。读入一个C--语言程序，判断该程序是不是一个合法的C--语言程序。如果程序有语法和语义错误，请给出错误信息。至少处理以下错误：
（1）所有语法错误。C――的语法参见C――的文档；
（2）语义错误：
​2a：标志符未定义错误，多次定义错误（需要采用符号表。关于符号表的实现，请大家参阅龙书的有关章节或我的symbol_table.ppt。）
​2b: 类型错误。判断运算符的参数是否具有所需要的类型。注意：算术运算符包括：＋，－，*,/,％只作用于整数。关系运算符（<,>，等）可以作用于整数表达式，字符表达式，但是不要求作用于字符串表达式（否则C－－就不是C语言的子集了，虽然理论上支持“ab” < “ac”还是挺有意思的）。类型错误包括函数调用的参数。
 
2．程序要做成命令行程序，带一个参数，表示输入的C--文件名。
 
3．实例输入文件为 s1.c, s2.c，s3.c其中s1.c和s3.c有错误，s2.c没有错误。
 
4．实验除了提交C语言源程序外，提交实验报告，说明设计思想，花了多少时间，和谁讨论（还是独立完成），采用什么编译器。遇到什么问题，如何解决的。实验报告一般命名为readme.txt 或readme.doc，提交文件到服务器上。
-->
# Report4
## Requirements
1. Syntax and semantic analyzer for the C-- language. It reads a C-- program, judges whether it is valid, and outputs error messages if syntax or semantic errors are found.
2. The analyzer must handle:
    - All syntax errors.
    - Semantic error 2a: Undefined identifiers and multiple definition errors (using a symbol table).
    - Semantic error 2b: Type mismatch errors. Verify if operands match operator requirements (arithmetic operators `+`, `-`, `*`, `/`, `%` only apply to integers; relational operators `<`, `>`, `<=`, `>=`, `==`, `!=` apply to comparable types like integers and characters, but not strings). Verify function call arguments (both count and types).
3. Command-line program taking one parameter representing the input C-- file name.
4. Correctly process the provided example files: s1.c (contains undefined variable error), s2.c (no errors), and s3.c (contains function argument type mismatch error).

## Design Ideas
The program is divided into three parts: the lexical analyzer (`c--l`), the syntax analyzer (`c--.y`), and a symbol table implementation embedded in the parser.

- Lexical Analyzer (`c--.l`): Identifies keywords, constants, operators, and identifiers. Instead of printing tokens directly, it returns token IDs to the parser and updates `yylval` with semantic values (e.g., `atoi` for integers, `strdup` for strings).
- Symbol Table & Scope Management:
    - Implemented using a linked list structure (`Symbol`) storing name, symbol kind (variable or function), type, scope level, and function parameters.
    - Controls scope levels via `enter_scope()` and `leave_scope()` when entering or leaving compound blocks `{}`.
    - Supports duplicate definition detection by checking the current scope, and undefined variable detection by searching recursively from the current scope outward to the global scope.
- Semantic & Type Checking:
    - Arithmetic operations: Checked by `check_arithmetic()`. Operands must be of type `int`.
    - Relational operations: Checked by `check_relation()`. Operands must be comparable (`int` or `char`) and of the same type.
    - Function calls: Checked by `check_function_call()`. Verifies that the identifier is a function, and that the number and types of arguments match the function declaration.
    - Return statements: Verifies return type compatibility with the enclosing function.

## Time Spent
Whole laboratory session.

## Discussion
LLMs and class materials (symbol_table.ppt).

## Compiler Used
GCC, Flex, and Bison.

## Problems
1. Bison Compatibility: Older Bison versions do not support the `%code requires` directive, causing compiler errors like `invalid directive: %code`.

## Solutions
1. Removed the `%code requires` block. Defined the `TypeList` structure within the `%{ ... %}` block and updated `%union` to use `struct TypeList *list` to bypass the limitation.
