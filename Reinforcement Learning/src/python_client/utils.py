from base import Action
import json
import numpy as np
from collections import deque as queue


def get_action(action):
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


def get_map(config_path):
    with open(config_path) as config_file:
        config = json.load(config_file)
        map_ = config['map']
        map_path = '../server/maps/'
        map_path += map_
    return map_path


def fetch_grid(height, width):
    map_path = get_map("../server/config.json")
    map_ = open(map_path, 'r').read().replace('\n', '')
    return np.array(list(map_)).reshape(height, width)


def init_q(s, a, init_type="ones"):
    if init_type == "ones":
        return np.ones((s, a))
    elif init_type == "random":
        return np.random.random((s, a))
    elif init_type == "zeros":
        return np.zeros((s, a))


def epsilon_greedy(q_table, epsilon, num_actions, s, train=False):
    if train or np.random.rand() > epsilon:
        return np.argmax(q_table[s, :])
    else:
        return np.random.randint(0, num_actions)

# ---------------------------------------------------------------------------------------------


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
