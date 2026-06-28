# config.py

TRAIN_FILE = "pinyin_train.txt"
PINYIN_FILE = "pinyin.txt"

# 发射概率混合比例
# final_emission = INIT_WEIGHT * init_emission + TRAIN_WEIGHT * train_emission
INIT_WEIGHT = 0.4
TRAIN_WEIGHT = 0.6

# Viterbi 返回候选数量
TOP_K = 9

# 平滑概率，避免路径断掉
SMOOTH_TRANS = 1e-8
SMOOTH_START = 1e-8
SMOOTH_EMIS = 1e-8

# 是否支持声母输入
ENABLE_INITIAL = True
