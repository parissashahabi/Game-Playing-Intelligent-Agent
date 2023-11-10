import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from numpy import loadtxt

reward_history = loadtxt('reward_history.csv', delimiter=',')
epochs = len(reward_history)
total_reward_history = np.zeros(epochs)
total_reward = 0

for i in range(epochs):
    reward_episode = reward_history[i]
    total_reward += reward_episode
    reward_history[i] = reward_episode
    total_reward_history[i] = total_reward

fig, axes = plt.subplots(2, 1, figsize=(5, 4), dpi=200, sharex='all')
axes[0].plot(np.arange(len(total_reward_history)), total_reward_history, alpha=0.7, color='yellowgreen')
axes[0].set_ylabel('Total rewards')
axes[1].plot(np.arange(len(reward_history)), reward_history, marker='o', markersize=2, alpha=0.7, color='tomato', linestyle='none')
axes[1].set_xlabel('Episode')
axes[1].set_ylabel('Reward from\na single game')
axes[1].xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
axes[0].grid(axis='x')
axes[1].grid(axis='x')
plt.tight_layout()
plt.show()
