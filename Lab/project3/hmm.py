# hmm.py

import heapq
import itertools
import math

class HMM:
    def __init__(
        self,
        transition_probability,
        emission_probability,
        start_probability,
        smooth_trans=1e-8,
        smooth_start=1e-8,
        smooth_emis=1e-8,
    ):
        self.transition_probability = transition_probability
        self.emission_probability = emission_probability
        self.start_probability = start_probability

        self.smooth_trans = smooth_trans
        self.smooth_start = smooth_start
        self.smooth_emis = smooth_emis

        self.states = (
            set(self.start_probability.keys())
            | set(self.transition_probability.keys())
            | set(self.emission_probability.keys())
            | {
                next_state
                for curr in self.transition_probability.values()
                for next_state in curr.keys()
            }
        )

        # observation -> possible states
        self.obs_to_states = {}
        for state, obs_dict in self.emission_probability.items():
            for obs, prob in obs_dict.items():
                if prob > 0:
                    self.obs_to_states.setdefault(obs, set()).add(state)

    def get_start_prob(self, state):
        return self.start_probability.get(state, self.smooth_start)

    def get_trans_prob(self, prev_state, curr_state):
        return self.transition_probability.get(prev_state, {}).get(
            curr_state, self.smooth_trans
        )

    def get_emis_prob(self, state, obs):
        return self.emission_probability.get(state, {}).get(obs, 0.0)

    def viterbi(self, observations, k=5):
        """
        返回：
        [
            {
                "prob": 概率,
                "text": "我的中国",
                "path": ["我", "的", "中", "国"]
            }
        ]
        """

        if not observations:
            return []

        observations = [x.lower() for x in observations]

        V = []

        # 第 0 个观测
        first_obs = observations[0]
        first_states = self.obs_to_states.get(first_obs, set())

        if not first_states:
            return []

        V.append({})

        for state in first_states:
            p_s = self.get_start_prob(state)
            p_e = self.get_emis_prob(state, first_obs)

            if p_e > 0:
                V[0][state] = [
                    (
                        math.log(p_s) + math.log(p_e),
                        [state],
                    )
                ]

        # 后续观测
        for t in range(1, len(observations)):
            obs = observations[t]
            curr_states = self.obs_to_states.get(obs, set())

            V.append({})

            if not curr_states:
                return []

            for curr_state in curr_states:
                p_e = self.get_emis_prob(curr_state, obs)

                if p_e <= 0:
                    continue

                log_p_e = math.log(p_e)
                candi = []

                for prev_state in V[t - 1]:
                    p_t = self.get_trans_prob(prev_state, curr_state)
                    log_p_t = math.log(p_t)

                    for prev_prob, prev_path in V[t - 1][prev_state]:
                        candi.append(
                            (
                                prev_prob + log_p_t + log_p_e,
                                prev_path + [curr_state],
                            )
                        )

                if candi:
                    V[t][curr_state] = heapq.nlargest(k, candi, key=lambda x: x[0])

        n = len(observations) - 1

        if not V[n]:
            return []

        all_paths = []
        for state in V[n]:
            all_paths.extend(V[n][state])

        best = heapq.nlargest(k, all_paths, key=lambda x: x[0])

        result = []
        for log_prob, path in best:
            result.append(
                {
                    "prob": math.exp(log_prob),
                    "text": "".join(path),
                    "path": path,
                }
            )

        return result
