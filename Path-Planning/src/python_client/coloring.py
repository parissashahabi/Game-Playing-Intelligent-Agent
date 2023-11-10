from collections import deque as queue
from pathfinding import Node, FindPath


class Coloring:
    def __init__(self, initial_grid, height, width):
        self.dRow = [0, 1, 1, 1, 0, -1, -1, -1]
        self.dCol = [-1, -1, 0, 1, 1, 1, 0, -1]
        self.vis = [[False for i in range(width)] for i in range(height)]
        self.path = FindPath(initial_grid, height, width)
        self.grid = self.path.create_grid(initial_grid)
        self.height = height
        self.width = width
        self.available_cells = []

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
            self.available_cells.append(self.grid[x][y])

            for i in range(8):
                adj_x = x + self.dRow[i]
                adj_y = y + self.dCol[i]
                if self.is_valid(adj_x, adj_y) and not self.grid[adj_x][adj_y].type == "W":
                    q.append((adj_x, adj_y))
                    self.vis[adj_x][adj_y] = True

    def contains(self, node):
        for cell in self.available_cells:
            if cell.x == node.x and cell.y == node.y:
                return True
        return False
