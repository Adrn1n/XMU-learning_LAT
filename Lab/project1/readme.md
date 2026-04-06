<!--
语言分析技术实验一
 
1．实验目的：
C--语言的词法分析器。将一个C--语言程序分割成token串的序列。处理C--语言的所有token类型。
 
2．程序要做成命令行程序，带两个参数，分别表示输入和输出文件名。
 
3．实例输入输出文件为 y.c y.out, z.c z.out，提交前保证你的分析器能够正确处理这些文件。
 
4．实验除了提交C语言源程序外，提交实验报告，说明设计思想，花了多少时间，和谁讨论（还是独立完成），采用什么编译器。遇到什么问题，如何解决的。实验报告一般命名为readme.txt 或readme.doc，提交文件可以命名为 2005xx00_lex.rar，其中2005xx00是你的学号。
-->
# Report1
## Requirements
1. Lexical analyzer for C-- language, which can split a C-- program into a sequence of tokens, handling all token types of C-- language.
2. Command-line program with two parameters for input and output file names.
3. The analyzer should correctly process the provided example files y.c and z.c, producing y.out and z.out respectively.
4. Submit the C language source program and a report explaining the design ideas, time spent, discussion (or independent work), compiler used, problems encountered, and solutions. The report should be named readme.txt or readme.doc, and the submission file should be named 2005xx00_lex.rar, where 2005xx00 is your student ID.

## Design Ideas
Referencing to the [implementation](http://10.26.63.123:8080/courses/lat/c--.rar) of C-- language by the teacher. But it needs some modifications to fit the requirements of this experiment (to align with the provided example).

- Add `long` as a keyword
- Add `PUN` as a token type for punctuation characters (`=`, `+`, `-`, `*`, `/` are also regarded as punctuation characters in this experiment from the provided example)
- Add `CHAR_CONST` as a token type for character constants (for any single character enclosed in single quotes)
- Add `STRING` as a token type for string literals (for any sequence of characters enclosed in double quotes)
- Add `main()` function as the entry point of the program, which reads the input file, processes it, and writes the output to the specified output file; will report error if parameters are not provided correctly or file cannot be opened
- `yylval` and return type is useless in this experiment, so remove it from the implementation

## Time Spent
Whole laboratory session.

## Discussion
LLMs.

## Compiler Used
GCC.

## Problems
1. Windows's `CRLF` line endings' `\r` character is regarded as an invalid character, which causes the program to report an error when processing files with `CRLF` line endings

## Solutions
1. Add a rule `\r\n` to cope with `CRLF` line endings, which will ignore the `\r` character and treat it as a normal line ending.
