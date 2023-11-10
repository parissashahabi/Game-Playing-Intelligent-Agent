import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from utils import grid_to_float_convertor
import math


class MDP:
    def __init__(self, grid, reward, count, normal_cells_probabilities, slider_cells_probabilities,
                 barbed_cells_probabilities, teleport_cells_probabilities, state_space, time_limit=1000):
        self.count = count
        self.state_space = state_space
        self.map = np.array(grid)
        self.num_rows = self.map.shape[0]
        self.num_cols = self.map.shape[1]
        self.map = grid_to_float_convertor(self.map, self.num_rows, self.num_cols)
        self.num_states = self.num_rows * self.num_cols
        self.num_actions = 9
        self.normal_cells_probabilities = normal_cells_probabilities
        self.slider_cells_probabilities = slider_cells_probabilities
        self.barbed_cells_probabilities = barbed_cells_probabilities
        self.teleport_cells_probabilities = teleport_cells_probabilities
        self.reward = reward
        self.numeric_rewards = self.split_reward()[1]
        self.nan_rewards = self.split_reward()[0]
        self.time_limit = time_limit
        self.reward_function = self.get_reward_function()
        self.transition_model = self.get_transition_model()

    def get_state_from_pos(self, pos):
        return pos[0] * self.num_cols + pos[1]

    def get_pos_from_state(self, state):
        return state // self.num_cols, state % self.num_cols

    def get_reward_function(self):
        reward_table = np.zeros(self.num_states)
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if (r, c) in self.state_space:
                    s = self.get_state_from_pos((r, c))
                    reward_table[s] = self.reward[self.map[r, c]]
        return reward_table

    def get_transition_model(self):
        transition_model = np.zeros((self.num_states, self.num_actions, self.num_states))
        allowed_cells = [0, 12, 13]
        for nr in self.numeric_rewards:
            if nr in [6, 7, 8]:
                allowed_cells.append(nr)
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if (r, c) in self.state_space:
                    cell_type = self.map[r, c]
                    s = self.get_state_from_pos((r, c))
                    neighbor_s = np.zeros(self.num_actions)
                    if self.map[r, c] in allowed_cells:
                        for a in range(self.num_actions):
                            new_r, new_c = r, c
                            if a == 0:  # Up
                                new_r = max(r - 1, 0)
                            elif a == 1:  # Down
                                new_r = min(r + 1, self.num_rows - 1)
                            elif a == 2:  # Left
                                new_c = max(c - 1, 0)
                            elif a == 3:  # Right
                                new_c = min(c + 1, self.num_cols - 1)
                            elif a == 4:  # Up Right
                                new_r = max(r - 1, 0)
                                new_c = min(c + 1, self.num_cols - 1)
                                if not(new_c == c + 1 and new_r == r - 1):
                                    new_r, new_c = r, c
                            elif a == 5:  # Up Left
                                new_r = max(r - 1, 0)
                                new_c = max(c - 1, 0)
                                if not(new_c == c - 1 and new_r == r - 1):
                                    new_r, new_c = r, c
                            elif a == 6:  # Down Right
                                new_r = min(r + 1, self.num_rows - 1)
                                new_c = min(c + 1, self.num_cols - 1)
                                if not(new_c == c + 1 and new_r == r + 1):
                                    new_r, new_c = r, c
                            elif a == 7:  # Down Left
                                new_r = min(r + 1, self.num_rows - 1)
                                new_c = max(c - 1, 0)
                                if not(new_c == c - 1 and new_r == r + 1):
                                    new_r, new_c = r, c
                            elif a == 8:  # NOOP
                                new_r, new_c = r, c
                            if self.map[new_r, new_c] in self.nan_rewards:
                                new_r, new_c = r, c
                            s_prime = self.get_state_from_pos((new_r, new_c))
                            neighbor_s[a] = s_prime
                    else:
                        neighbor_s = np.ones(self.num_actions) * s
                    for a in range(self.num_actions):
                        for i, neighbor in enumerate(neighbor_s):
                            if cell_type in [0, 6, 7, 8]:
                                transition_model[s, a, int(neighbor)] += self.normal_cells_probabilities[a, i]
                            elif cell_type in [1, 2, 3, 4, 9, 10, 11]:
                                transition_model[s, a, int(neighbor)] += self.slider_cells_probabilities[a, i]
                            elif cell_type == 12:
                                transition_model[s, a, int(neighbor)] += self.barbed_cells_probabilities[a, i]
                            elif cell_type == 13:
                                transition_model[s, a, int(neighbor)] += self.teleport_cells_probabilities[a, i]
        return transition_model

    def split_reward(self):
        nan_list = []
        float_list = []
        for r in self.reward.items():
            if math.isnan(r[1]):
                nan_list.append(r[0])
            else:
                float_list.append(r[0])
        return nan_list, float_list

    def visualize_value_policy(self, policy, values, fig_size=(12, 10)):
        unit = min(fig_size[1] // self.num_rows, fig_size[0] // self.num_cols)
        unit = max(1, unit)
        fig, ax = plt.subplots(1, 1, figsize=fig_size)
        ax.axis('off')

        for i in range(self.num_cols + 1):
            if i == 0 or i == self.num_cols:
                ax.plot([i * unit, i * unit], [0, self.num_rows * unit],
                        color='black')
            else:
                ax.plot([i * unit, i * unit], [0, self.num_rows * unit],
                        alpha=0.7, color='grey', linestyle='dashed')
        for i in range(self.num_rows + 1):
            if i == 0 or i == self.num_rows:
                ax.plot([0, self.num_cols * unit], [i * unit, i * unit],
                        color='black')
            else:
                ax.plot([0, self.num_cols * unit], [i * unit, i * unit],
                        alpha=0.7, color='grey', linestyle='dashed')

        for i in range(self.num_rows):
            for j in range(self.num_cols):
                y = (self.num_rows - 1 - i) * unit
                x = j * unit
                s = self.get_state_from_pos((i, j))
                if self.map[i, j] == 5:
                    rect = patches.Rectangle((x, y), unit, unit, edgecolor='none', facecolor='black',
                                             alpha=0.6)
                    ax.add_patch(rect)
                elif self.map[i, j] == 12:
                    rect = patches.Rectangle((x, y), unit, unit, edgecolor='none', facecolor='red',
                                             alpha=0.6)
                    ax.add_patch(rect)
                elif self.map[i, j] in [1, 2, 3, 4]:
                    rect = patches.Rectangle((x, y), unit, unit, edgecolor='none', facecolor='green',
                                             alpha=0.6)
                    ax.add_patch(rect)
                elif self.map[i, j] in [9, 10, 11]:
                    rect = patches.Rectangle((x, y), unit, unit, edgecolor='none', facecolor='yellow',
                                             alpha=0.6)
                    ax.add_patch(rect)
                elif self.map[i, j] in [6, 7, 8]:
                    rect = patches.Rectangle((x, y), unit, unit, edgecolor='none', facecolor='blue',
                                             alpha=0.6)
                    ax.add_patch(rect)
                if self.map[i, j] not in [5, 6, 7, 8]:
                    ax.text(x + 0.5 * unit, y + 0.5 * unit, f'{values[s]:.4f}',
                            horizontalalignment='center', verticalalignment='center',
                            fontsize=max(fig_size)*unit*0.5)
                if policy is not None:
                    if self.map[i, j] == 0:
                        a = policy[s]
                        symbol = ['^', 'v', '<', '>', '$U_R$', '$U_L$', '$D_R$', '$D_L$', '$N$']
                        ax.plot([x + 0.5 * unit], [y + 0.5 * unit], marker=symbol[a], alpha=0.4,
                                linestyle='none', markersize=max(fig_size)*unit, color='#1f77b4')

        # plt.tight_layout()
        plt.savefig(f'images/EMG {self.count}.jpg')
        # plt.show()
