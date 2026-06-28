# main.py

import argparse
from normalizer import Preprocessor, DictMatcher, NoiseInjector

class TextNormalizer:
    """
    中文非规范词恢复系统。
    本版本主要实现：
    1. 预处理
    2. 汉字间隔符清理
    3. 词典匹配替换
    """

    def __init__(self, dict_path: str = "data/mapping.json"):
        self.preprocessor = Preprocessor()
        self.matcher = DictMatcher(dict_path)

    def normalize(self, text: str, show_records: bool = False) -> str:
        """
        规范化单句文本
        """
        text = self.preprocessor.preprocess(text)
        normalized_text, records = self.matcher.normalize(text)

        if show_records:
            if records:
                print("替换记录：")
                for src, tgt in records:
                    print(f"  {src} -> {tgt}")
            else:
                print("无词典替换记录。")

        return normalized_text

def normalize_sentence(args):
    """
    单句模式
    """
    normalizer = TextNormalizer(args.dict)
    result = normalizer.normalize(args.sentence, show_records=args.verbose)
    print(result)

def normalize_file(args):
    """
    文件批处理模式
    """
    normalizer = TextNormalizer(args.dict)

    with open(args.file, "r", encoding="utf-8") as fin, \
            open(args.output, "w", encoding="utf-8") as fout:

        for line in fin:
            line = line.strip()
            if not line:
                fout.write("\n")
                continue

            result = normalizer.normalize(line)
            fout.write(result + "\n")

    print(f"处理完成，结果已保存至：{args.output}")

def build_data(args):
    """
    构造平行数据模式
    """
    injector = NoiseInjector(args.dict)
    injector.build_parallel_data(
        input_path=args.raw,
        output_path=args.output,
        num_aug_per_sentence=args.num
    )

def main():
    parser = argparse.ArgumentParser(
        description="中文社交媒体非规范词恢复程序"
    )

    parser.add_argument(
        "-d", "--dict",
        default="data/mapping.json",
        help="规范化词典路径，默认为 data/mapping.json"
    )

    subparsers = parser.add_subparsers(dest="mode")

    # 单句模式
    sentence_parser = subparsers.add_parser("sentence", help="单句规范化模式")
    sentence_parser.add_argument("-s", "--sentence", required=True, help="输入句子")
    sentence_parser.add_argument("-v", "--verbose", action="store_true", help="显示替换记录")

    # 文件模式
    file_parser = subparsers.add_parser("file", help="文件批处理模式")
    file_parser.add_argument("-f", "--file", required=True, help="输入文件路径")
    file_parser.add_argument("-o", "--output", default="output/result.txt", help="输出文件路径")

    # 数据构造模式
    data_parser = subparsers.add_parser("build-data", help="噪声注入，构造平行数据")
    data_parser.add_argument("--raw", required=True, help="规范语料路径")
    data_parser.add_argument("-o", "--output", default="output/synthetic_pairs.txt", help="输出平行数据路径")
    data_parser.add_argument("-n", "--num", type=int, default=1, help="每条句子增强次数")

    args = parser.parse_args()

    if args.mode == "sentence":
        normalize_sentence(args)
    elif args.mode == "file":
        normalize_file(args)
    elif args.mode == "build-data":
        build_data(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
