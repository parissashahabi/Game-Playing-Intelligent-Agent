import pandas as pd
import numpy as np
from mdp_solver import MDPSolver
from base import BaseAgent, Action
from time import time
from utils import GridColoring, GoalsPermutation, Gem, powerset

GEM_SEQUENCE_SCORE = [
    [50, 0, 0, 0],
    [50, 200, 100, 0],
    [100, 50, 200, 100],
    [50, 100, 50, 200],
    [250, 50, 100, 50]
]

REWARD = {'normal_cell': -1.0, 'forbidden_cell': np.NAN, 'barbed': -20.0, 'teleport': 0.0, 'key': 85.0, 'first_gem': 300.0}


class Agent(BaseAgent):
    def __init__(self):
        super(Agent, self).__init__()
        self.num_states = self.grid_width * self.grid_height
        self.policy = None
        self.finished = False
        self.last_gem = 0
        self.agent = (0, 0)
        self.gems_locations = []
        self.keys_locations = []
        self.teleports_locations = []
        self.gem_nodes = []
        self.required_keys = []
        self.required_keys_locations = set()
        self.keys = set()
        self.initial_grid = None
        self.forbidden_cells = []
        self.normal_cells_probabilities = pd.DataFrame(self.probabilities['normal']).transpose().to_numpy()
        self.slider_cells_probabilities = pd.DataFrame(self.probabilities['slider']).transpose().to_numpy()
        self.barbed_cells_probabilities = pd.DataFrame(self.probabilities['barbed']).transpose().to_numpy()
        self.teleport_cells_probabilities = pd.DataFrame(self.probabilities['teleport']).transpose().to_numpy()

    def find_teleports(self):
        teleports = []
        for x in range(self.grid_height):
            for y in range(self.grid_width):
                if self.grid[x][y] == 'T':
                    teleports.append((x, y))
        self.teleports_locations = teleports

    def find_required_keys_locations(self):
        for key in self.keys_locations:
            if (self.grid[key[0]][key[1]] == 'g' and 9 in self.required_keys) or (self.grid[key[0]][key[1]] == 'r' and 10 in self.required_keys) or (self.grid[key[0]][key[1]] == 'y' and 11 in self.required_keys):
                self.required_keys_locations.add(key)

    def calculate_teleport_reward(self):
        self.find_required_keys_locations()
        initial_colored_grid = GridColoring(self.grid, self.grid_height, self.grid_width, self.forbidden_cells, False)
        initial_colored_grid.bfs(self.agent[0], self.agent[1])
        agent_can_teleport = False
        for teleport_loc in self.teleports_locations:
            if teleport_loc in initial_colored_grid.available_cells:
                agent_can_teleport = True
        for teleport_loc in self.teleports_locations:
            teleported_colored_grid = GridColoring(self.grid, self.grid_height, self.grid_width, self.forbidden_cells, False)
            teleported_colored_grid.bfs(teleport_loc[0], teleport_loc[1])
            if self.agent not in teleported_colored_grid.available_cells:
                for cell in teleported_colored_grid.available_cells:
                    if (cell in self.gems_locations or cell in list(self.required_keys_locations)) and agent_can_teleport:
                        REWARD['teleport'] = 50

    def get_reward(self):
        # TODO -> E
        self.calculate_teleport_reward()
        reward = {0: REWARD['normal_cell'], 5: REWARD['forbidden_cell'], 12: REWARD['barbed'], 13: REWARD['teleport']}
        door_allowed = []
        for key in list(self.keys):
            if key == 9:
                door_allowed.append(6)
            elif key == 10:
                door_allowed.append(7)
            elif key == 11:
                door_allowed.append(8)
        for door_type in [6, 7, 8]:
            if door_type in door_allowed:
                reward[door_type] = REWARD['normal_cell']
                continue
            reward[door_type] = REWARD['forbidden_cell']
        for key_type in [9, 10, 11]:
            if key_type in self.required_keys and key_type not in list(self.keys):
                reward[key_type] = REWARD['key']
            else:
                reward[key_type] = REWARD['normal_cell']

        if self.last_gem == 0:
            colored_grid = GridColoring(self.grid, self.grid_height, self.grid_width, self.forbidden_cells, False)
            colored_grid.bfs(0, 0)
            goals_permutation = GoalsPermutation(self.gem_nodes, colored_grid, self.grid, self.grid_height,
                                                 self.grid_width, self.last_gem, self.agent, self.max_turn_count, self.turn_count, 10)
            permutation = goals_permutation.generate_actions()
            if permutation == (None, None) or (len(permutation.sequence) == 1 and int(permutation.sequence[0].type) in [2, 3, 4]):
                self.finished = True
                for gem_type in [1, 2, 3, 4]:
                    reward[gem_type] = REWARD['normal_cell']
                return reward
            valuable_gem = int(permutation.sequence[0].type)
            reward[valuable_gem] = REWARD['first_gem']
            gems = [1, 2, 3, 4]
            gems.remove(valuable_gem)
            for gem_type in gems:
                reward[gem_type] = float(GEM_SEQUENCE_SCORE[self.last_gem][gem_type - 1])
        else:
            for gem_type in [1, 2, 3, 4]:
                reward[gem_type] = float(GEM_SEQUENCE_SCORE[self.last_gem][gem_type - 1])
        return reward

    def map_required_keys_to_nums(self):
        for key in self.required_keys:
            if key == 'g':
                key_index = self.required_keys.index(key)
                self.required_keys[key_index] = 9
            elif key == 'r':
                key_index = self.required_keys.index(key)
                self.required_keys[key_index] = 10
            elif key == 'y':
                key_index = self.required_keys.index(key)
                self.required_keys[key_index] = 11

    def get_state_from_pos(self, pos):
        return pos[0] * self.grid_width + pos[1]

    def find_sliders(self):
        keys, gems, gem_nodes = [], [], []
        for x in range(self.grid_height):
            for y in range(self.grid_width):
                if self.grid[x][y] in ['1', '2', '3', '4']:
                    gem = Gem(x, y)
                    gem.type = self.grid[x][y]
                    gem_nodes.append(gem)
                    gems.append((x, y))
                elif self.grid[x][y] in ['g', 'r', 'y']:
                    keys.append((x, y))
        self.keys_locations = keys
        self.gems_locations = gems
        self.gem_nodes = gem_nodes

    def get_action(self, state):
        action = self.policy[state]
        if action == 0:  # Up
            return Action.UP
        elif action == 1:  # Down
            return Action.DOWN
        elif action == 2:  # Left
            return Action.LEFT
        elif action == 3:  # Right
            return Action.RIGHT
        elif action == 4:  # Up Right
            return Action.UP_RIGHT
        elif action == 5:  # Up Left
            return Action.UP_LEFT
        elif action == 6:  # Down Right
            return Action.DOWN_RIGHT
        elif action == 7:  # Down Left
            return Action.DOWN_LEFT
        elif action == 8:  # NOOP
            return Action.NOOP

    def get_policy(self):
        self.find_required_keys()
        state_space = self.get_state_space()
        reward = self.get_reward()
        if not reward:
            self.policy = np.ones(self.num_states) * 8
            return
        mdp_solver = MDPSolver(self.grid, reward, self.turn_count, self.normal_cells_probabilities,
                               self.slider_cells_probabilities, self.barbed_cells_probabilities,
                               self.teleport_cells_probabilities, state_space, self.grid_width)
        mdp_solver.train()
        # mdp_solver.visualize_value_policy()
        self.policy = mdp_solver.get_policy()

    def get_agent_location(self):
        for x in range(self.grid_height):
            for y in range(self.grid_width):
                if 'A' in self.grid[x][y]:
                    self.agent = (x, y)

    def update_last_gem(self):
        last_gem_index = self.gems_locations.index(self.agent)
        x, y = self.gems_locations[last_gem_index]
        self.last_gem = int(self.initial_grid[x][y])

    def update_reached_keys_list(self):
        key_index = self.keys_locations.index(self.agent)
        x, y = self.keys_locations[key_index]
        if self.initial_grid[x][y] == 'g':
            self.keys.add(9)
        elif self.initial_grid[x][y] == 'r':
            self.keys.add(10)
        elif self.initial_grid[x][y] == 'y':
            self.keys.add(11)

    def get_state_space(self):
        self.forbidden_cells = self.remove_keys_from(['W', 'G', 'R', 'Y'])
        colored_grid = GridColoring(self.grid, self.grid_height, self.grid_width, self.forbidden_cells, True)
        colored_grid.bfs(0, 0)
        return colored_grid.available_cells

    def first_round_operations(self):
        # Initialize grid
        self.initial_grid = self.grid

        # Find gems and keys
        self.find_sliders()

        # Find teleports
        self.find_teleports()

    def remove_keys_from(self, lst):
        for key in list(self.keys):
            if key == 9:
                lst.remove('G')
            elif key == 10:
                lst.remove('R')
            elif key == 11:
                lst.remove('Y')
        return lst

    def find_required_keys(self):
        self.required_keys = []
        keys = self.remove_keys_from(['G', 'Y', 'R'])
        doors_subset = list(powerset(keys))
        for i, subset in enumerate(doors_subset):
            forbidden_cells = self.remove_keys_from(['W', 'G', 'R', 'Y'])
            colored_grid = GridColoring(self.grid, self.grid_height, self.grid_width, forbidden_cells, False)
            colored_grid.bfs(self.agent[0], self.agent[1])
            available_cells_without_any_key = colored_grid.available_cells
            for door in subset:
                forbidden_cells.remove(door)
            colored_grid = GridColoring(self.grid, self.grid_height, self.grid_width, forbidden_cells, False)
            colored_grid.bfs(self.agent[0], self.agent[1])
            available_cells_with_key = colored_grid.available_cells
            difference = list(set(available_cells_with_key) - set(available_cells_without_any_key))
            if available_cells_with_key != available_cells_without_any_key:
                for cell in difference:
                    if cell in self.gems_locations:
                        for door in subset:
                            if door.lower() not in self.required_keys:
                                self.required_keys.append(door.lower())
        self.map_required_keys_to_nums()

    def do_turn(self) -> Action:
        start_time = int(round(time() * 1000))
        if self.turn_count == 1:
            self.first_round_operations()

        self.get_agent_location()

        # If the agent reaches a key/gem:
        if self.agent in self.gems_locations or self.agent in self.keys_locations or self.turn_count == 1:
            if self.turn_count != 1:
                if self.agent in self.gems_locations:
                    self.update_last_gem()
                else:
                    self.update_reached_keys_list()
            self.find_sliders()
            self.get_policy()

        state = self.get_state_from_pos(self.agent)
        action = self.get_action(state)
        cur_time = int(round(time() * 1000)) - start_time
        print(f'time {cur_time}')
        return action


if __name__ == '__main__':
    data = Agent().play()
    print("FINISH : ", data)
