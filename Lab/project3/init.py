# init.py

from collections import defaultdict
from utils import get_initial

def load(file_name, enable_initial=True, *args, **kwargs):
    """
    从 pinyin.txt 读取字到拼音的发射概率。

    pinyin.txt 格式假设：
    a:阿啊呵腌吖嗄
    ai:爱矮挨...
    """

    emis = defaultdict(lambda: defaultdict(float))

    with open(file_name, "r", *args, **kwargs) as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue

            py, chars = line.split(":", 1)
            py = py.strip().lower()
            chars = chars.strip()

            if not py or not chars:
                continue

            for c in chars:
                emis[c][py] += 1.0

                if enable_initial:
                    sm = get_initial(py)
                    if sm:
                        emis[c][sm] += 1.0

    # 对每个汉字的发射概率归一化
    for c, py_dict in emis.items():
        total = sum(py_dict.values())
        if total > 0:
            for py in py_dict:
                py_dict[py] /= total

    return emis
