import numpy as np
import matplotlib.pyplot as plt


class ValueIteration:
    def __init__(self, reward_function, transition_model, state_space, num_cols, gamma):
        self.num_states = transition_model.shape[0]
        self.num_actions = transition_model.shape[1]
        self.reward_function = np.nan_to_num(reward_function)
        self.transition_model = transition_model
        self.gamma = gamma
        self.state_space = state_space
        self.values = np.zeros(self.num_states)
        self.policy = None
        self.num_cols = num_cols

    def get_pos_from_state(self, state):
        return state // self.num_cols, state % self.num_cols

    def one_iteration(self):
        delta = 0
        for s in range(self.num_states):
            r, c = self.get_pos_from_state(s)
            if (r, c) in self.state_space:
                temp = self.values[s]
                v_list = np.zeros(self.num_actions)
                for a in range(self.num_actions):
                    p = self.transition_model[s, a]
                    if a in [0, 1, 2, 3]:
                        v_list[a] = self.reward_function[s] + self.gamma * np.sum(p * self.values)
                    elif a in [4, 5, 6, 7]:
                        v_list[a] = 2 * self.reward_function[s] + self.gamma * np.sum(p * self.values)
                    elif a == 8:
                        v_list[a] = self.gamma * np.sum(p * self.values)

                self.values[s] = max(v_list)
                delta = max(delta, abs(temp - self.values[s]))
        return delta

    def get_policy(self):
        pi = np.ones(self.num_states) * -1
        for s in range(self.num_states):
            r, c = self.get_pos_from_state(s)
            if (r, c) in self.state_space:
                v_list = np.zeros(self.num_actions)
                for a in range(self.num_actions):
                    p = self.transition_model[s, a]
                    if a in [0, 1, 2, 3]:
                        v_list[a] = self.reward_function[s] + self.gamma * np.sum(p * self.values)
                    elif a in [4, 5, 6, 7]:
                        v_list[a] = 2 * self.reward_function[s] + self.gamma * np.sum(p * self.values)
                    elif a == 8:
                        v_list[a] = self.gamma * np.sum(p * self.values)

                max_index = []
                max_val = max(v_list)
                for a in range(self.num_actions):
                    if v_list[a] == max_val:
                        max_index.append(a)
                if 8 in max_index:
                    pi[s] = 8
                else:
                    direct_actions = [action for action in max_index if action < 4]
                    if len(direct_actions) > 0:
                        pi[s] = np.random.choice(direct_actions)
                    else:
                        pi[s] = np.random.choice(max_index)
                # pi[s] = np.random.choice(max_index)
        return pi.astype(int)

    def train(self, tol=1e-1, plot=True):
        epoch = 0
        delta = self.one_iteration()
        delta_history = [delta]
        while delta > tol:
            epoch += 1
            delta = self.one_iteration()
            delta_history.append(delta)
            if delta < tol:
                break
        self.policy = self.get_policy()

        # if plot is True:
        #     fig, ax = plt.subplots(1, 1, figsize=(3, 2), dpi=200)
        #     ax.plot(np.arange(len(delta_history)) + 1, delta_history, marker='o', markersize=4,
        #             alpha=0.7, color='#2ca02c', label=r'$\gamma= $' + f'{self.gamma}')
        #     ax.set_xlabel('Iteration')
        #     ax.set_ylabel('Delta')
        #     ax.legend()
        #     plt.tight_layout()
        #     plt.show()
