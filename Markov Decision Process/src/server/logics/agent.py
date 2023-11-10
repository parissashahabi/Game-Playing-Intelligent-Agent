from logics.network import Socket
from logics.map import Tile
from logics import game_rules
from logics.actions import Actions

PLAYER_CHARACTERS = ["A", "B", "C", "D"]


class Agent:
    def __init__(self, agent_id, tile, init_score, connection: Socket):
        self.tile = tile
        self.init_score = init_score  # change_it maybe
        self._id = agent_id
        self.connection = connection
        self.gems = []
        self.hit_hurts = []
        self.turn_age = 0
        self.action_history = []
        self.keys = []
        self.barbed_history = []

    @property
    def id(self):
        return self._id + 1

    def get_diagonal_move_history_count(self):
        return sum([self.action_history.count(item) for item in
                    [Actions.UP_LEFT, Actions.UP_RIGHT,
                     Actions.DOWN_LEFT, Actions.DOWN_RIGHT]
                    ])

    def get_straight_move_history_count(self):
        return sum([self.action_history.count(item) for item in
                    [Actions.UP, Actions.DOWN, Actions.RIGHT, Actions.LEFT]
                    ])

    def get_action_score(self):
        return self.get_diagonal_move_history_count() * game_rules.DIAGONAL_MOVE_HURT + \
               self.get_straight_move_history_count() * game_rules.STRAIGHT_MOVE_HURT

    def get_gem_score(self):
        point = 0
        # gem_counts = self.get_gems_count()
        # for i, gem_count in enumerate(gem_counts.values()):
        #     point += gem_count * game_rules.GEM_SCORES[i]
        gems = [None]+self.gems.copy()

        for i in range(1, len(gems)):
            if i == 1:
                first = 0
            else:
                first = int(gems[i - 1].value)
            second = int(gems[i].value)-1
            point += game_rules.GEM_SEQUENCE_SCORE[first][second]

        return point

    @property
    def score(self):
        # change_it
        point = self.init_score
        point += self.get_gem_score()
        point += len(self.hit_hurts) * game_rules.HIT_HURT
        point += len(self.barbed_history) * game_rules.BARBED_HURT
        point += self.get_action_score()
        return point

    @property
    def character(self):
        return PLAYER_CHARACTERS[self._id]

    @property
    def name(self):
        return PLAYER_CHARACTERS[self._id]

    def add_gem(self, gem):
        self.gems.append(gem)

    def add_key(self, key):
        # TODO validate
        # can agent agg duplicated keys??
        self.keys.append(key)

    def get_keys_count(self):
        return {
            "key1": self.gems.count(Tile.TileType.KEY1),
            "key2": self.gems.count(Tile.TileType.KEY2),
            "key3": self.gems.count(Tile.TileType.KEY3),
        }

    def has_key(self, key):
        return key in self.keys

    def get_gems_count(self):
        return {
            "gem1": self.gems.count(Tile.TileType.GEM1),
            "gem2": self.gems.count(Tile.TileType.GEM2),
            "gem3": self.gems.count(Tile.TileType.GEM3),
            "gem4": self.gems.count(Tile.TileType.GEM4),
        }

    def get_information(self):
        gem1, gem2, gem3, gem4 = self.get_gems_count().values()

        return {
            "score": self.score,
            "hit_hurts_count": len(self.hit_hurts),
            "barbed_hurts_count": len(self.barbed_history),
            "gem1": gem1,
            "gem2": gem2,
            "gem3": gem3,
            "gem4": gem4,

        }

    def add_barbed_history(self, tile):
        self.barbed_history.append(tile)

    def get_action_history_information(self):
        return {action.value: self.action_history.count(action) for action in Actions}

    def add_action_history(self, action):
        self.action_history.append(action)
