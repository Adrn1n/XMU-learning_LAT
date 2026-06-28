# normalizer/preprocess.py

import re

try:
    from opencc import OpenCC
except ImportError:
    OpenCC = None

class Preprocessor:
    """
    文本预处理模块：
    1. 繁体转简体
    2. 全角转半角
    3. 去除多余空格
    4. 统一部分标点
    """

    def __init__(self, use_opencc=True):
        self.use_opencc = use_opencc and OpenCC is not None
        if self.use_opencc:
            self.converter = OpenCC("t2s")
        else:
            self.converter = None

    def fullwidth_to_halfwidth(self, text: str) -> str:
        """
        全角字符转半角字符
        """
        result = []
        for char in text:
            code = ord(char)
            if code == 0x3000:
                code = 32
            elif 0xFF01 <= code <= 0xFF5E:
                code -= 0xFEE0
            result.append(chr(code))
        return "".join(result)

    def normalize_punctuation(self, text: str) -> str:
        """
        简单统一标点
        """
        punctuation_map = {
            "，": ",",
            "。": ".",
            "！": "!",
            "？": "?",
            "：": ":",
            "；": ";",
            "（": "(",
            "）": ")",
            "【": "[",
            "】": "]"
        }

        for old, new in punctuation_map.items():
            text = text.replace(old, new)

        return text

    def remove_extra_spaces(self, text: str) -> str:
        """
        去除多余空格
        """
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def preprocess(self, text: str) -> str:
        """
        预处理入口函数
        """
        if not text:
            return ""

        text = self.fullwidth_to_halfwidth(text)

        if self.use_opencc:
            text = self.converter.convert(text)

        text = self.normalize_punctuation(text)
        text = self.remove_extra_spaces(text)

        return text
