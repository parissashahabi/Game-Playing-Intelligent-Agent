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
    TELEPORT = 'TELEPORT'

    @classmethod
    def two_near_move(cls, move_action):
        ordered_actions = [cls.UP, cls.UP_RIGHT, cls.RIGHT, cls.DOWN_RIGHT, cls.DOWN, cls.DOWN_LEFT, cls.LEFT,
                           cls.UP_LEFT]
        if move_action in ordered_actions[1:-1]:
            index = ordered_actions.index(move_action)
            return ordered_actions[index - 1], ordered_actions[index + 1]
        elif move_action == cls.UP:
            return cls.UP_LEFT, cls.UP_RIGHT
        elif move_action == cls.UP_LEFT:
            return cls.LEFT, cls.UP

    @classmethod
    def accepted_action(cls):
        return [cls.UP, cls.UP_RIGHT, cls.RIGHT, cls.DOWN_RIGHT, cls.DOWN, cls.DOWN_LEFT, cls.LEFT, cls.UP_LEFT,cls.NOOP]

