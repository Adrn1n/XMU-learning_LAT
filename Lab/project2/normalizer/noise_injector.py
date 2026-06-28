# normalizer/noise_injector.py

import json
import random
from typing import Dict, List, Tuple

class NoiseInjector:
    """
    噪声注入模块。
    用于从规范句子自动生成非规范句子。
    """

    def __init__(self, mapping_path: str = "data/mapping.json", seed: int = 42):
        random.seed(seed)

        with open(mapping_path, "r", encoding="utf-8") as f:
            self.noise_to_standard = json.load(f)

        # 将 mapping 反转：规范词 -> 非规范词列表
        self.standard_to_noise = self.reverse_mapping(self.noise_to_standard)

        # 可插入的间隔符
        self.separators = ["-", "·", "*", "/", "_"]

    def reverse_mapping(self, mapping: Dict[str, str]) -> Dict[str, List[str]]:
        """
        将 非规范词 -> 规范词 反转成 规范词 -> 非规范词列表
        """
        reversed_map = {}

        for noise, standard in mapping.items():
            reversed_map.setdefault(standard, []).append(noise)

        return reversed_map

    def inject_dictionary_noise(self, text: str, prob: float = 0.5) -> str:
        """
        根据反向词典，将规范词替换为非规范词。
        """
        keys = sorted(self.standard_to_noise.keys(), key=len, reverse=True)

        for standard_word in keys:
            if standard_word in text and random.random() < prob:
                noise_candidates = self.standard_to_noise[standard_word]
                noise_word = random.choice(noise_candidates)
                text = text.replace(standard_word, noise_word)

        return text

    def inject_separator_noise(self, text: str, prob: float = 0.1) -> str:
        """
        随机在连续汉字之间插入分隔符。
        """
        result = []

        for i, char in enumerate(text):
            result.append(char)

            if i < len(text) - 1:
                next_char = text[i + 1]

                if self.is_chinese(char) and self.is_chinese(next_char):
                    if random.random() < prob:
                        result.append(random.choice(self.separators))

        return "".join(result)

    def is_chinese(self, char: str) -> bool:
        """
        判断是否为汉字
        """
        return "\u4e00" <= char <= "\u9fff"

    def inject(self, text: str,
               dict_noise_prob: float = 0.5,
               sep_noise_prob: float = 0.05) -> str:
        """
        总噪声注入函数。
        """
        text = self.inject_dictionary_noise(text, dict_noise_prob)
        text = self.inject_separator_noise(text, sep_noise_prob)
        return text

    def build_parallel_data(self,
                            input_path: str,
                            output_path: str,
                            num_aug_per_sentence: int = 1):
        """
        从规范语料生成平行数据：
        非规范文本 \\t 规范文本
        """
        pairs = []

        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                standard_text = line.strip()
                if not standard_text:
                    continue

                for _ in range(num_aug_per_sentence):
                    noisy_text = self.inject(standard_text)
                    pairs.append((noisy_text, standard_text))

        with open(output_path, "w", encoding="utf-8") as f:
            for noisy, standard in pairs:
                f.write(noisy + "\t" + standard + "\n")

        print(f"成功生成 {len(pairs)} 条平行数据，保存至 {output_path}")
