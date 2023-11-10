from pathfinding import Node


class Gem(Node):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.score = None
        self.color = None
        self.evaluation_result = None
