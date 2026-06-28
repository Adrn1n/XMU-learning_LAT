# app.py

from flask import Flask, jsonify, request
from flask_cors import CORS
from collections import defaultdict

from init import load
from train import train
from hmm import HMM
from utils import split_user_input

import config

app = Flask(__name__)
CORS(app)

def mix_emission(init_emis, train_emis, init_weight=0.4, train_weight=0.6):
    """
    混合 pinyin.txt 发射概率和训练语料发射概率。
    """

    result = defaultdict(lambda: defaultdict(float))

    chars = set(init_emis.keys()) | set(train_emis.keys())

    for c in chars:
        obs_set = set(init_emis.get(c, {}).keys()) | set(train_emis.get(c, {}).keys())

        for obs in obs_set:
            p1 = init_emis.get(c, {}).get(obs, 0.0)
            p2 = train_emis.get(c, {}).get(obs, 0.0)
            result[c][obs] = init_weight * p1 + train_weight * p2

    # 再归一化一次
    for c, obs_dict in result.items():
        total = sum(obs_dict.values())
        if total > 0:
            for obs in obs_dict:
                obs_dict[obs] /= total

    return result

print("正在加载 pinyin.txt...")
init_emis = load(
    config.PINYIN_FILE,
    enable_initial=config.ENABLE_INITIAL,
    encoding="utf-8",
)

print("正在训练 HMM...")
trans, train_emis, start = train(
    config.TRAIN_FILE,
    enable_initial=config.ENABLE_INITIAL,
    encoding="utf-8",
)

print("正在混合发射概率...")
emis = mix_emission(
    init_emis,
    train_emis,
    config.INIT_WEIGHT,
    config.TRAIN_WEIGHT,
)

model = HMM(
    transition_probability=trans,
    emission_probability=emis,
    start_probability=start,
    smooth_trans=config.SMOOTH_TRANS,
    smooth_start=config.SMOOTH_START,
    smooth_emis=config.SMOOTH_EMIS,
)

print("模型加载完成！")

@app.route("/api/decode", methods=["POST"])
def decode():
    """
    请求示例：
    {
        "input": "wo de zhong guo",
        "top_k": 9
    }

    返回：
    {
        "ok": true,
        "observations": ["wo", "de", "zhong", "guo"],
        "candidates": [...]
    }
    """

    data = request.get_json(force=True)
    raw_input = data.get("input", "")
    top_k = int(data.get("top_k", config.TOP_K))

    observations = split_user_input(raw_input)

    candidates = model.viterbi(observations, top_k)

    return jsonify(
        {
            "ok": True,
            "input": raw_input,
            "observations": observations,
            "candidates": candidates,
        }
    )

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "message": "HMM 拼音输入法后端运行中"})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
