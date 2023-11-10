from enum import Enum


class Actions(Enum):
    UP = 'UP'
    DOWN = 'DOWN'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'
    UP_RIGHT = "UP_RIGHT"
    UP_LEFT = "UP_LEFT"
    DOWN_RIGHT = "DOWN_RIGHT"
    DOWN_LEFT = "DOWN_LEFT"
    NOOP = 'NOOP'
    # TELEPORT = 'TELEPORT'
