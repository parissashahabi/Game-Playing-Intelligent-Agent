from mdp import MDP
from value_iteration import ValueIteration


class MDPSolver:
    def __init__(self, grid, reward, count, normal_cells_probabilities, slider_cells_probabilities,
                 barbed_cells_probabilities, teleport_cells_probabilities, state_space, num_cols):
        self.problem = MDP(grid, reward, count, normal_cells_probabilities, slider_cells_probabilities,
                           barbed_cells_probabilities, teleport_cells_probabilities, state_space)
        self.solver = ValueIteration(self.problem.reward_function, self.problem.transition_model, state_space, num_cols,
                                     gamma=0.85)

    def train(self):
        self.solver.train()

    def visualize_value_policy(self):
        self.problem.visualize_value_policy(policy=self.solver.policy, values=self.solver.values)

    def get_policy(self):
        return self.solver.policy
