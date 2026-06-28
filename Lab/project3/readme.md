<!--
语言分析技术实验3
 
1．实验目的：
写一个基于HMM的拼音输入法，可以是汉语也可以是你知道的其他语言。
原理：
  汉语有很多字拼音相同。可以根据上下文来挑选概率大的字。如“wo”可对应汉字“我、窝、握、卧”等，“de”也可以对于“的、得、地、德”等。但是“wode”对应的概率比较大的应该属于“我的”。
    我们把拼音作为观察值，把汉字当作状态，那么可以用HMM来建模拼音输入。转移概率可从语料库训练而得，生成概率则需考虑多音字（在不知道多音字概率的情况下可假设等概率）。
    这个实验的主要目的是让大家实现Viterbi算法。不是要做一个真实的输入法。
 
2．程序要做成GUI方式，概率比较大的候选要排在前面。根据输入一段文本所需要的击键次数来判断程序的好坏。
 
3．采用给定的pinyin.txt来读取每个汉字的拼音。采用pinyin_train.txt来训练你的HMM，采用输入pinyin_test.txt中的一段文本来测试你的击键次数。需给出你自己测试的击键次数。
 
4．实验除了提交C语言源程序外，提交实验报告，说明设计思想，花了多少时间，和谁讨论（还是独立完成），采用什么编译器。遇到什么问题，如何解决的。实验报告一般命名为readme.txt 或readme.doc，提交文件可以命名为 2005xx00_lex.rar，其中2005xx00是你的学号。


---

语言分析技术实验3说明
 
1． 注音工具
可采用pypinyin:
如 pip install pypinyin 可安装python模块。
命令行下运行：
E:\>pypinyin 长长的大腿
cháng cháng de dà tuǐ
 
python 下面运行：
>>> from pypinyin import pinyin
>>> pinyin('她长着长长的大腿')
[['tā'], ['zhǎng'], ['zhe'], ['cháng'], ['cháng'], ['de'], ['dà'], ['tuǐ']]
 
因此训练从汉字到拼音的概率不成问题。
 
2． 拼音编码：
a) 我们不希望采用ā，á，ǎ，à 这些符号，因此应该统一转换成a；
b) 我们不希望采用全拼，能简单就简单。最简单的简拼是输入词组方式下只写声母输入。如“扪心自问”的拼音编码可以为 mxzw。另外，对于不喜欢卷舌音的南方人，模糊音的处理也是必要的。
c) 因此，我们需要把汉字（词）到拼音的概率转换为到编码的概率。
d) 编码如何定义是一个很有意思的话题。
 
3.支持词组输入？
  本实验不要求支持词组输入，除非你想要做一个真正的输入法。
以下是我以前做多语言词组输入法时从编码到概率表的例子：
汉语：
aa|傲岸 0.00813008130081301
aa|嗷嗷 0.0548780487804878
aa|昂昂 0.0101626016260163
aa|暗暗 0.747967479674797
aa|皑皑 0.178861788617886
ab|奥博 0.539370078740158
ab|安瓿 0.0118110236220472
ab|岸标 0.00393700787401575
ab|敖包 0.188976377952756
ab|案板 0.255905511811024
achangzu|阿昌族 1
acz|阿昌族 1
ac|哀愁 0.0592300098716683
ac|哀辞 0.000987166831194472
ac|安厝 0.000987166831194472
ac|安插 0.197433366238894
ac|挨次 0.00296150049358342
藏语：
aa|འུར་འུར 0.628571428571429
aa|འབ་འུབ 0.0857142857142857
aa|འ་འུར 0.0571428571428571
aa|འར་འུར 0.0571428571428571
aa|འོར་འོད 0.0571428571428571
aa|འལ་འོལ 0.0571428571428571
aa|འའ 0.0285714285714286
aa|ྰ 0.0285714285714286
aabrael|འའབྲེལ 1
aabum|འའབུམ 1
aabyaung|འའབྱུང 1
aach|འུལ་འུར་ཆེམ་ཆེམ 0.263157894736842
aach|འུར་འུར་ཆལ་ཆིལ 0.263157894736842
aach|འུར་འུར་ཆེམ་ཆེམ 0.263157894736842
 
4． 整句输入还是词组输入
  以前哈工大的王晓龙老师做过整句输入法，还成功地卖给了微软，非常励志。如果我们采用Viterbi算法，显然可以实现整句输入法。但是，其正确率就不好说了。实际上，如果考虑实用性，那么基于词组的输入法是更合适的。不妨看看下面的例子：




可见，猜测用户心中的句子是比较困难的。如果输入太长，万一不是你期望的输入，需要回头删除很多字符，导致输入速度变慢。
 
5． 词组哪里来？
这个实验的初始目的是，不希望你仅仅采用现成的词组，而是用Viterbi解码来合成“新词”。或者叫“常用n元组合”！这样应该可以加快速度。如何与已有词典结合，这是一个需要大家考虑的问题。
 
6． GUI可以简单点。别花太多时间。
 
7． pinyin.txt可能不全面。上一届的李迅潮同学已经发现“谁”的拼音漏了“shui”。
-->
# Report3
## Requirements
1. Implement a Chinese pinyin input method based on Hidden Markov Model (HMM).
2. The program must have a Graphical User Interface (GUI) where candidates with higher probabilities are ranked first. It should record the number of keystrokes and backspaces to evaluate performance.
3. Use the provided `pinyin.txt` to map Chinese characters to pinyin, and `pinyin_train.txt` to train the HMM parameters (transition, emission, and start probabilities).
4. Test the input method using sentences from `pinyin_test.txt` (ignoring punctuation and numbers) for both full pinyin and initials (声母) modes. Provide statistics on keystroke counts.
5. Submit the source code and a report (readme.txt/doc) detailing design ideas, time spent, discussions, runtime environment, problems encountered, and solutions.

## Design Ideas
- Architecture: A Client-Server architecture. The backend is implemented in Python using Flask to handle HMM training and Viterbi decoding. The frontend is a web-based GUI (HTML/JS/CSS) that interacts with the backend API.
- HMM Modeling:
    - States ($S$): Chinese characters
    - Observations ($O$): Pinyin syllables or initials
    - Start Probability ($\pi$): Calculated from the starting characters of sentences in `pinyin_train.txt`
    - Transition Probability ($A$): Character-level bigram transition probabilities $P(c_i|c_{i-1})$ trained from `pinyin_train.txt`
    - Emission Probability ($B$): Mixed from the dictionary (`pinyin.txt`, weighted at 0.4) and the training corpus (`pinyin_train.txt` annotated via `pypinyin`, weighted at 0.6) to balance general coverage and domain-specific frequency
- Viterbi Decoder: Implemented a $k$-best Viterbi algorithm using log-probabilities to prevent floating-point underflow. It maintains the top $K$ (default 9) most probable paths at each step using Python's `heapq` module
- Initials (声母) Support: During training and dictionary initialization, both full pinyin and their corresponding initials are mapped to the emission matrix. This allows the decoder to process mixed inputs of full pinyin and initials
- GUI & Interaction:
    - Listens to input events in real-time (with debouncing) and sends requests to the Flask backend
    - Displays the top 9 candidates; Users can press numeric keys `1-9` to select a candidate or press `Enter` to select the first one
    - Tracks total keystrokes, backspace counts, selection counts, and current input length dynamically at the bottom of the page
- Automated Testing: A test script (`test_api.py`) automatically cleans `pinyin_test.txt` (removing punctuation and numbers), converts text to full pinyin or initials, queries the API, and calculates the hit rate and estimated keystrokes

## Time Spent
Whole laboratory session.

## Discussion
LLMs (for skeleton code optimization and debugging Viterbi path merging).

## Compiler/Runtime Used
- Python Version: Python 3.11.15 (managed via PDM virtual environment)
- Package Manager: PDM (Python Development Master)
- Dependencies:
    - `flask >= 3.1.3` (Web backend server)
    - `flask-cors >= 6.0.5` (Cross-Origin Resource Sharing handling)
    - `pypinyin >= 0.55.0` (Pinyin generation tool for corpus mapping)
    - `requests >= 2.34.2` (API request client for testing)
- Frontend Runtime: VSCode Live Server (for local web GUI testing)

## Problems
1. Viterbi Path Breakage (Dead Ends): When the input contains character transitions or character-pinyin emissions that never appeared in the training corpus, the probability drops to zero, causing the Viterbi algorithm to return no candidates.
2. Poor Performance in Initials Mode on Whole Sentences: In the initial test run, the full-pinyin mode achieved a 90% sentence-level accuracy, but the initials mode scored 0%. This is because initials are highly ambiguous, and a first-order character-level HMM cannot constrain the search space over long sentences without semantic constraints.

## Solutions
1. Probability Smoothing: Introduced smoothing factors (`smooth_trans`, `smooth_start`, `smooth_emis` set to $10^{-8}$) to assign a baseline probability to unseen transitions and emissions, ensuring the Viterbi trellis remains active.
2. Chunk-based Input & Analysis: Added a chunking mechanism in the test script to simulate how real users type with initials (typing 4-6 characters at a time instead of an entire sentence). This demonstrates that initials mode is highly usable for short phrases, while indicating that a higher-order language model (e.g., trigram HMM) or a word-based dictionary model is required for long-sentence initials input.
