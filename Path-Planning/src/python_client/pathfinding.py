import math
from math import sqrt

final_keys = []


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.f = 0
        self.g = 0
        self.h = 0
        self.type = ''

        # neighbors = []
        self.previous = None
        # self.obstacle = False


class FindPath:
    def __init__(self, initial_grid, height, width):
        # start = None
        # end = None
        self.initial_grid = initial_grid
        self.height = height
        self.width = width
        self.grid = self.create_grid(initial_grid)
        self.open_set = []
        self.closed_set = []
        self.current_node = None
        self.final_path = []
        self.keys = []
        self.doors = []
        self.door_allowed = False

    def find_path(self, source, goal):
        self.open_set = []
        self.closed_set = []
        self.final_path = []
        start = self.grid[source[0]][source[1]]
        end = self.grid[goal[0]][goal[1]]
        global final_keys
        self.open_set.append(start)
        while len(self.open_set) > 0:
            self.a_star(start, end)
            if len(self.final_path) > 0:
                break
        if len(self.final_path) == 0 and not self.door_allowed:
            self.find_path_with_keys(start, end)
        return self.final_path

    def a_star(self, start, end):
        best_way = 0
        for i in range(len(self.open_set)):
            if self.open_set[i].f < self.open_set[best_way].f:
                best_way = i

        self.current_node = self.open_set[best_way]
        self.find_keys_in_the_path(self.current_node)

        self.open_set.pop(best_way)
        self.final_path = []
        if self.current_node == end:
            self.find_keys_in_the_path(self.current_node)
            global final_keys
            final_keys = [key for key in self.keys]
            temp = self.current_node
            while temp.previous:
                if self.door_allowed:
                    if temp.type in ['R', 'Y', 'G']:
                        self.doors.append(temp.type)
                self.final_path.append((temp.x, temp.y))
                temp = temp.previous
            self.final_path.append((start.x, start.y))

        neighbors = self.find_neighbors(self.current_node)
        for i, neighbor in enumerate(neighbors):
            if self.can_go(neighbor, end):
                temp_g = self.current_node.g + self.g_score(neighbor)

                if neighbor in self.open_set:
                    if temp_g < neighbor.g:
                        self.update_node(neighbor, temp_g, end)
                else:
                    self.update_node(neighbor, temp_g, end)
                    self.open_set.append(neighbor)

                self.closed_set.append(self.current_node)

    def update_node(self, node, temp_g, end):
        node.g = temp_g
        node.h = self.h_score(node, end)
        node.f = node.g + node.h
        node.previous = self.current_node

    def h_score(self, node, end):
        distance = sqrt(abs(node.x - end.x)**2 + abs(node.y - end.y)**2)
        return distance

    def can_go(self, node, end):
        if node.x == end.x and node.y == end.y:
            return True
        # elif (node in self.closed_set) or (node.type in ['W', '1', '2', '3', '4']):
        #     return False

        if (node in self.closed_set) or (node.type == 'W'):
            return False

        elif node.type in ['R', 'Y', 'G']:
            if node.type.lower() in self.keys:
                return True
            else:
                if self.door_allowed:
                    return True
                else:
                    return False
        else:
            return True

    def find_neighbors(self, node):
        x = node.x
        y = node.y
        neighbors = []
        if x < self.height - 1:
            neighbors.append(self.grid[x + 1][y])
        if x > 0:
            neighbors.append(self.grid[x - 1][y])
        if y < self.width - 1:
            neighbors.append(self.grid[x][y + 1])
        if y > 0:
            neighbors.append(self.grid[x][y - 1])
        # diagonals
        if x > 0 and y > 0:
            neighbors.append(self.grid[x - 1][y - 1])
        if x < self.height - 1 and y > 0:
            neighbors.append(self.grid[x + 1][y - 1])
        if x > 0 and y < self.width - 1:
            neighbors.append(self.grid[x - 1][y + 1])
        if x < self.height - 1 and y < self.width - 1:
            neighbors.append(self.grid[x + 1][y + 1])
        return neighbors

    def create_grid(self, initial_grid):
        grid = []
        for i in range(self.height):
            grid.append([])
            for j in range(self.width):
                grid[-1].append(0)
                grid[i][j] = Node(i, j)
                grid[i][j].type = initial_grid[i][j]
        return grid

    def g_score(self, node):
        if node.type == "*":
            return 20
        elif node.type in ['r', 'y', 'g'] and node.type not in self.keys:
            return -2
        elif abs(node.x - self.current_node.x) == 1 and abs(node.y - self.current_node.y) == 1:
            return 2
        else:
            return 1

    def find_keys_in_the_path(self, current_node):
        self.keys = []
        global final_keys
        for key in final_keys:
            self.keys.append(key)
        temp = current_node
        while temp.previous:
            if temp.type in ['r', 'g', 'y']:
                self.keys.append(temp.type)
            temp = temp.previous

    def find_path_with_keys(self, start, end):
        self.door_allowed = True
        self.find_path((start.x, start.y), (end.x, end.y))
        if len(self.final_path) != 0:
            self.doors.reverse()
            for door in self.doors:
                if door.lower() not in self.keys:
                    keys_list = self.find_key(door)
                    if len(keys_list) != 0:
                        nearest_key = self.nearest_key(keys_list, start)
                        self.door_allowed = False
                        path1 = self.find_path((start.x, start.y), (nearest_key.x, nearest_key.y))
                        self.open_set = []
                        self.closed_set = []
                        self.current_node = None
                        f2 = FindPath(self.initial_grid, self.height, self.width)
                        path2 = f2.find_path((nearest_key.x, nearest_key.y), (end.x, end.y))
                        path2.pop(path2.index((nearest_key.x, nearest_key.y)))
                        path = path2 + path1
                        self.final_path = path
                        return

    def find_key(self, door):
        keys_list = []
        for x in range(self.height):
            for y in range(self.width):
                if self.grid[x][y].type == door.lower():
                    keys_list.append(self.grid[x][y])
        return keys_list

    def nearest_key(self, keys_list, start):
        f2 = FindPath(self.grid, self.height, self.width)
        distance = math.inf
        nearest_key = None
        for key in keys_list:
            path = f2.find_path((start.x, start.y), (key.x, key.y))
            if len(path) < distance and len(path) != 0:
                distance = len(path)
                nearest_key = key
        return nearest_key
