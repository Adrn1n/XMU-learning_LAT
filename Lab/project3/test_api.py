# test_api.py

import requests
from utils import clean_chinese_text, text_to_full_pinyin, text_to_initials

API_URL = "http://127.0.0.1:5000/api/decode"

def decode(obs_list, top_k=9):
    s = " ".join(obs_list)

    resp = requests.post(
        API_URL,
        json={
            "input": s,
            "top_k": top_k,
        },
        timeout=30,
    )

    resp.raise_for_status()
    return resp.json()["candidates"]

def test_one_sentence(sentence, mode="full", top_k=9):
    target = clean_chinese_text(sentence)

    if not target:
        return None

    if mode == "full":
        obs = text_to_full_pinyin(target)
    elif mode == "initial":
        obs = text_to_initials(target)
    else:
        raise ValueError("mode must be full or initial")

    candidates = decode(obs, top_k=top_k)
    texts = [x["text"] for x in candidates]

    hit_rank = -1
    for i, text in enumerate(texts):
        if text == target:
            hit_rank = i + 1
            break

    # 击键数估计：
    # 输入字符数量 + 空格数量 + 选择数字一次
    input_string = " ".join(obs)
    key_count = len(input_string)

    if hit_rank == 1:
        # 如果第一个候选，可以按 Enter 或数字 1
        key_count += 1
    elif hit_rank > 1:
        # 按对应数字
        key_count += 1
    else:
        # 没命中，实际需要人工修改，这里记为失败
        pass

    return {
        "target": target,
        "mode": mode,
        "obs": obs,
        "top_candidates": texts[:top_k],
        "hit_rank": hit_rank,
        "key_count": key_count,
    }

def read_test_file(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        content = f.read()

    # 按行测，也可以按句号切分
    lines = []
    for line in content.splitlines():
        line = line.strip()
        if line:
            cleaned = clean_chinese_text(line)
            if cleaned:
                lines.append(cleaned)

    return lines

def run_test(file_name="pinyin_test.txt"):
    sentences = read_test_file(file_name)

    for mode in ["full", "initial"]:
        print("=" * 80)
        print(f"测试模式：{mode}")
        print("=" * 80)

        total = 0
        hit = 0
        total_keys = 0

        for idx, sent in enumerate(sentences, 1):
            result = test_one_sentence(sent, mode=mode, top_k=9)

            if result is None:
                continue

            total += 1
            total_keys += result["key_count"]

            if result["hit_rank"] > 0:
                hit += 1

            print(f"\n[{idx}] 目标：{result['target']}")
            print(f"编码：{' '.join(result['obs'])}")
            print(f"候选前几项：{result['top_candidates'][:3]}")
            print(f"命中排名：{result['hit_rank']}")
            print(f"估计击键数：{result['key_count']}")

        print("\n统计结果：")
        print(f"总句数：{total}")
        print(f"命中句数：{hit}")
        print(f"命中率：{hit / total if total else 0:.4f}")
        print(f"总击键数：{total_keys}")
        print(f"平均每句击键数：{total_keys / total if total else 0:.2f}")

if __name__ == "__main__":
    run_test("pinyin_test.txt")
