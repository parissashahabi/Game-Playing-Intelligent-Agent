from pathfinding import FindPath, Node
from operator import attrgetter
from itertools import permutations
from permutation import Permutation
from calculate_diagonal_distance import calculate_diagonal_distance

GEM_SEQUENCE_SCORE = [
    [50,   0,   0, 0],
    [50, 200, 100, 0],
    [100, 50, 200, 100],
    [50, 100, 50,  200],
    [250, 50, 100, 50]
]


class ChooseGoalsSequence:
    def __init__(self, gems_list, coloring, grid, grid_height, grid_width, last_goal, last_gem,
                 agent, max_turn_count, turn_count, gems_dispersion_coefficient):
        self.last_gem = last_gem
        self.agent = agent
        self.last_goal = last_goal
        self.gems_list = gems_list
        self.finished = False
        self.coloring = coloring
        self.grid = grid
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.max_turn_count = max_turn_count
        self.turn_count = turn_count
        self.gems_dispersion_coefficient = gems_dispersion_coefficient

    def evaluate_permutation(self, perms) -> list:
        evaluated_permutations = []
        for seq in perms:
            permutation = Permutation()
            permutation.sequence_tuple = seq
            evaluation_result = 0
            current_agent_loc = self.agent
            last_goal_type = self.last_gem
            total_distance = 0
            is_reachable = True
            for gem in seq:
                diagonal_distance = calculate_diagonal_distance(current_agent_loc, gem)
                total_distance += diagonal_distance
                if self.max_turn_count - self.turn_count + 1 <= total_distance:
                    is_reachable = False
                    break
                gem_seq_score = GEM_SEQUENCE_SCORE[last_goal_type][int(gem.type)-1]
                evaluation_result += gem_seq_score - (diagonal_distance * ((self.grid_height * self.grid_width) / self.max_turn_count) * self.gems_dispersion_coefficient)
                current_agent_loc = gem
                last_goal_type = int(gem.type)
            if is_reachable:
                permutation.evaluation_result = evaluation_result
                evaluated_permutations.append(permutation)

        return evaluated_permutations

    def choose_goals_sequence(self, perms) -> list:
        evaluated_permutations = self.evaluate_permutation(perms)
        evaluated_permutations.sort(key=attrgetter("evaluation_result"), reverse=True)
        return evaluated_permutations

    def find_permutations(self):
        if len(self.gems_list) >= 2:
            return permutations(self.gems_list, 2)
        else:
            return permutations(self.gems_list, len(self.gems_list))

    def generate_actions(self):
        temp_gems_list = []
        for gem in self.gems_list:
            if self.coloring.contains(gem):
                temp_gems_list.append(gem)

        self.gems_list = temp_gems_list

        perms = list(self.find_permutations())
        if len(perms[0]) == 0:
            self.finished = True
            return

        self.agent = self.last_goal

        if not self.last_goal.type == '':
            self.last_gem = int(self.last_goal.type)
        permutations_list = self.choose_goals_sequence(perms)

        for perm in permutations_list:
            agent_location = (self.agent.x, self.agent.y)
            final_path = []
            is_reachable = True
            for goal in perm.sequence_tuple:
                f = FindPath(self.grid, self.grid_height, self.grid_width)
                goal_location = (goal.x, goal.y)
                path = f.find_path(agent_location, goal_location)
                if not len(path) == 0:
                    path.reverse()
                    if not len(final_path) == 0:
                        final_path.pop()
                    for tup in path:
                        final_path.append(tup)
                    if len(final_path) - 1 > self.max_turn_count - self.turn_count + 1:
                        is_reachable = False
                        break
                    agent_location = (goal.x, goal.y)
                else:
                    is_reachable = False
            if is_reachable:
                final_path.reverse()
                self.last_goal = perm.sequence_tuple[-1]
                return final_path, self.last_goal

        self.finished = True
