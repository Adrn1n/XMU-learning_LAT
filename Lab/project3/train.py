# train.py

from pypinyin import pinyin, Style
from collections import defaultdict
import re
from utils import get_initial

def train(corpus_file, enable_initial=True, *args, **kwargs):
    trans = defaultdict(lambda: defaultdict(float))
    emis = defaultdict(lambda: defaultdict(float))
    start = defaultdict(float)

    line_cnt = 0
    pattern = re.compile(r"[^\u4e00-\u9fa5]")

    with open(corpus_file, "r", *args, **kwargs) as f:
        for line in f:
            line = line.strip()
            line = pattern.sub("", line)

            if not line:
                continue

            line_cnt += 1
            pinyin_list = pinyin(line, style=Style.NORMAL)

            for i, c in enumerate(line):
                py = pinyin_list[i][0].lower()

                # 全拼发射
                emis[c][py] += 1.0

                # 声母发射
                if enable_initial:
                    sm = get_initial(py)
                    if sm:
                        emis[c][sm] += 1.0

                # 起始概率
                if i == 0:
                    start[c] += 1.0

                # 转移概率
                if i < len(line) - 1:
                    trans[c][line[i + 1]] += 1.0

    # 发射概率归一化
    for c, py_dict in emis.items():
        total = sum(py_dict.values())
        if total > 0:
            for py in py_dict:
                emis[c][py] /= total

    # 转移概率归一化
    for c, next_dict in trans.items():
        total = sum(next_dict.values())
        if total > 0:
            for next_c in next_dict:
                trans[c][next_c] /= total

    # 起始概率归一化
    if line_cnt > 0:
        for c in start:
            start[c] /= line_cnt

    return trans, emis, start

if __name__ == "__main__":
    trans, emis, start = train("pinyin_train.txt", enable_initial=True, encoding="utf-8")
    print("transition states:", len(trans))
    print("emission states:", len(emis))
    print("start states:", len(start))
