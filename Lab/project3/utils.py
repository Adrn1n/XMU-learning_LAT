# utils.py

import re
from pypinyin import lazy_pinyin, Style

def clean_chinese_text(text: str) -> str:
    """
    只保留中文。
    忽略标点、数字、英文等。
    """
    return "".join(re.findall(r"[\u4e00-\u9fa5]", text))

def text_to_full_pinyin(text: str):
    """
    中文转全拼列表。
    """
    text = clean_chinese_text(text)
    return lazy_pinyin(text, style=Style.NORMAL)

def get_initial(py: str) -> str:
    """
    提取拼音声母。
    注意 zh/ch/sh 是整体声母。
    """
    if not py:
        return ""

    py = py.lower()

    for sm in ["zh", "ch", "sh"]:
        if py.startswith(sm):
            return sm

    if py[0] in "bpmfdtnlgkhjqxzcsrwy":
        return py[0]

    # 零声母字，例如 ai, an, ou
    return py[0]

def text_to_initials(text: str):
    """
    中文转声母列表。
    """
    return [get_initial(py) for py in text_to_full_pinyin(text)]

def split_user_input(s: str):
    """
    用户输入格式支持：
    1. wo de zhong guo
    2. wo,de,zhong,guo
    3. w d z g
    4. wd zg 不推荐，但可以先按空格处理

    实验中建议让用户用空格分隔每个字的拼音或声母。
    """
    s = s.strip().lower()
    if not s:
        return []

    s = s.replace(",", " ")
    parts = [x for x in s.split() if x]
    return parts
