import numpy as np
from collections import deque as queue
from operator import attrgetter
from itertools import permutations

# def get_probabilities(sheet_name):
#     df_dict = pd.read_excel('probabilities/1.xlsx', sheet_name=sheet_name, usecols='B:K', header=None, skiprows=1)
#     return df_dict.to_numpy()


def grid_to_float_convertor(grid, num_rows, num_cols):
    for r in range(num_rows):
        for c in range(num_cols):
            # TODO -> 'A'
            if grid[r, c] == 'E' or grid[r, c] == 'EA':
                grid[r, c] = 0
            elif grid[r, c] == '1':
                grid[r, c] = 1
            elif grid[r, c] == '2':
                grid[r, c] = 2
            elif grid[r, c] == '3':
                grid[r, c] = 3
            elif grid[r, c] == '4':
                grid[r, c] = 4
            elif grid[r, c] == 'W':
                grid[r, c] = 5
            elif grid[r, c] == 'G':
                grid[r, c] = 6
            elif grid[r, c] == 'R':
                grid[r, c] = 7
            elif grid[r, c] == 'Y':
                grid[r, c] = 8
            elif grid[r, c] == 'g':
                grid[r, c] = 9
            elif grid[r, c] == 'r':
                grid[r, c] = 10
            elif grid[r, c] == 'y':
                grid[r, c] = 11
            elif grid[r, c] == '*':
                grid[r, c] = 12
            elif grid[r, c] == 'T':
                grid[r, c] = 13
    return np.array(grid, float)


def calculate_diagonal_distance(source, destination):
    dx = abs(source[0] - destination[0])
    dy = abs(source[1] - destination[1])
    return 2 * min(dx, dy) + (max(dx, dy) - min(dx, dy))


def create_grid(initial_grid, height, width):
    grid = []
    for i in range(height):
        grid.append([])
        for j in range(width):
            grid[-1].append(0)
            grid[i][j] = Node(i, j)
            grid[i][j].type = initial_grid[i][j]
    return grid


def find_teleports(grid, height, width):
    teleports = []
    for x in range(height):
        for y in range(width):
            if grid[x][y] == 'T':
                teleport = Node(x, y)
                teleport.type = 'T'
                teleports.append(teleport)
    return teleports


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = ''
        self.seen = False


class Gem(Node):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.score = None
        self.color = None
        self.evaluation_result = None


class GridColoring:
    def __init__(self, initial_grid, height, width, forbidden_cells, teleport):
        self.dRow = [0, 1, 1, 1, 0, -1, -1, -1]
        self.dCol = [-1, -1, 0, 1, 1, 1, 0, -1]
        self.vis = [[False for i in range(width)] for i in range(height)]
        self.grid = create_grid(initial_grid, height, width)
        self.height = height
        self.width = width
        self.available_cells = []
        self.forbidden_cells = forbidden_cells
        self.teleports_locations = find_teleports(initial_grid, height, width)
        self.can_teleport = teleport

    def is_valid(self, row, col):
        if row < 0 or col < 0 or row >= self.height or col >= self.width:
            return False
        if self.vis[row][col]:
            return False
        return True

    def bfs(self, row, col):
        q = queue()
        q.append((row, col))
        self.vis[row][col] = True
        while len(q) > 0:
            cell = q.popleft()
            x = cell[0]
            y = cell[1]
            if (x, y) not in self.available_cells:
                self.available_cells.append((x, y))

            if self.can_teleport is True and self.grid[x][y].type == 'T' and self.grid[x][y].seen is False:
                self.grid[x][y].seen = True
                for cell in self.teleports_locations:
                    if cell.x == x and cell.y == y:
                        index = self.teleports_locations.index(cell)
                        self.teleports_locations[index].seen = True
                    if cell.seen is False:
                        self.bfs(cell.x, cell.y)

            for i in range(8):
                adj_x = x + self.dRow[i]
                adj_y = y + self.dCol[i]
                if self.is_valid(adj_x, adj_y) and not self.grid[adj_x][adj_y].type in self.forbidden_cells:
                    q.append((adj_x, adj_y))
                    self.vis[adj_x][adj_y] = True

    def contains(self, tup):
        for cell in self.available_cells:
            if cell[0] == tup[0] and cell[1] == tup[1]:
                return True
        return False


class Permutation:
    def __init__(self):
        self.sequence = None
        self.evaluation_result = None


GEM_SEQUENCE_SCORE = [
    [50, 0, 0, 0],
    [50, 200, 100, 0],
    [100, 50, 200, 100],
    [50, 100, 50, 200],
    [250, 50, 100, 50]
]


class GoalsPermutation:
    def __init__(self, gems_list, coloring, grid, grid_height, grid_width, last_gem,
                 agent, max_turn_count, turn_count, gems_dispersion_coefficient):
        self.last_gem = last_gem
        self.agent = agent
        self.gems_list = gems_list
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
            permutation.sequence = seq
            evaluation_result = 0
            current_agent_loc = self.agent
            last_goal_type = self.last_gem
            total_distance = 0
            is_reachable = True
            for gem in seq:
                diagonal_distance = calculate_diagonal_distance(current_agent_loc, (gem.x, gem.y))
                total_distance += diagonal_distance
                if self.max_turn_count - self.turn_count + 1 <= total_distance:
                    is_reachable = False
                    break
                gem_seq_score = GEM_SEQUENCE_SCORE[last_goal_type][int(gem.type) - 1]
                evaluation_result += gem_seq_score - (diagonal_distance * self.gems_dispersion_coefficient *
                                                      ((self.grid_height * self.grid_width) / self.max_turn_count))
                current_agent_loc = (gem.x, gem.y)
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
            g = (gem.x, gem.y)
            if self.coloring.contains(g):
                temp_gems_list.append(gem)
        self.gems_list = temp_gems_list
        perms = list(self.find_permutations())
        if len(perms[0]) == 0:
            return None, None
        permutations_list = self.choose_goals_sequence(perms)
        return permutations_list[0]


def powerset(s):
    x = len(s)
    masks = [1 << i for i in range(x)]
    for i in range(1 << x):
        yield [ss for mask, ss in zip(masks, s) if i & mask]
