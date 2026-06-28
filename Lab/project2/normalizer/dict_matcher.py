# normalizer/dict_matcher.py

import json
import re
from typing import Dict, List, Tuple

class DictMatcher:
    """
    基于词典的非规范词恢复模块。
    使用最长优先匹配策略。
    """

    def __init__(self, dict_path: str = "data/mapping.json"):
        self.dict_path = dict_path
        self.mapping = self.load_mapping(dict_path)

        # 按 key 长度降序排序，保证优先匹配长词
        self.keys = sorted(self.mapping.keys(), key=len, reverse=True)

    def load_mapping(self, path: str) -> Dict[str, str]:
        """
        加载 JSON 词典
        """
        with open(path, "r", encoding="utf-8") as f:
            mapping = json.load(f)
        return mapping

    def normalize_by_dict(self, text: str) -> Tuple[str, List[Tuple[str, str]]]:
        """
        使用词典进行替换。
        返回：
        1. 规范化后的文本
        2. 替换记录列表
        """
        replace_records = []

        for key in self.keys:
            if key in text:
                value = self.mapping[key]
                count = text.count(key)
                text = text.replace(key, value)

                for _ in range(count):
                    replace_records.append((key, value))

        return text, replace_records

    def remove_chinese_separators(self, text: str) -> str:
        """
        去除汉字之间的分隔符。
        例如：
        日-本-人 -> 日本人
        总·书·记 -> ***

        注意：只去除两个汉字之间的符号，不影响英文、数字和普通标点。
        """
        pattern = r"([\u4e00-\u9fff])[\-\*·•/\\_]+(?=[\u4e00-\u9fff])"

        while re.search(pattern, text):
            text = re.sub(pattern, r"\1", text)

        return text

    def normalize(self, text: str) -> Tuple[str, List[Tuple[str, str]]]:
        """
        总规范化入口：
        1. 去除汉字间隔符
        2. 词典替换
        """
        text = self.remove_chinese_separators(text)
        text, records = self.normalize_by_dict(text)
        return text, records
