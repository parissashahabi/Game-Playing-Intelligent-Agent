from enum import Enum
import numpy as np


class Tile:
    class TileType(Enum):
        WALL = 'W'
        EMPTY = 'E'
        TELEPORT = 'T'
        GEM1 = '1'
        GEM2 = '2'
        GEM3 = '3'
        GEM4 = '4'
        DOOR1 = "G"
        DOOR2 = "Y"
        DOOR3 = "R"
        KEY1 = "g"
        KEY2 = "y"
        KEY3 = "r"
        BARBED = "*"

    @classmethod
    def get_tile_characters(cls):
        return [e.value for e in cls.TileType]

    def __init__(self, x, y, tile_type=TileType.EMPTY):
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.teleports = []

    @property
    def address(self):
        return self.y, self.x

    def __repr__(self):
        return self.tile_type.value

    def get_gem(self):
        if self.tile_type in [self.TileType.GEM1, self.TileType.GEM2, self.TileType.GEM3, self.TileType.GEM4]:
            return self.tile_type

        else:
            return None

    def is_wall(self):
        return self.tile_type == self.TileType.WALL

    def is_empty(self):
        return self.tile_type == self.TileType.EMPTY

    def is_teleport(self):
        return self.tile_type == self.TileType.TELEPORT

    def is_barbed(self):
        return self.tile_type == self.TileType.BARBED

    def get_door(self):
        if self.tile_type in [self.TileType.DOOR1, self.TileType.DOOR2, self.TileType.DOOR3]:
            return self.tile_type

        else:
            return None


    def get_key(self):
        if self.tile_type in [self.TileType.KEY1, self.TileType.KEY2, self.TileType.KEY3]:
            return self.tile_type

        else:
            return None






class Map:
    def __init__(self, map_content):

        map_tiles = []
        teleports = []
        for y, row in enumerate(map_content):
            row_tiles = []
            for x, item in enumerate(row):
                tile = Tile(x=x, y=y, tile_type=Tile.TileType(item))
                row_tiles.append(tile)
                if tile.is_teleport():
                    teleports.append(tile)

            map_tiles.append(row_tiles)

        self.tiles = np.array(map_tiles)
        self.height, self.width = self.tiles.shape
        self._teleports = teleports

    def __repr__(self):
        return str(self.tiles)

    def get_tile(self, y, x):
        if y not in range(self.height) or x not in range(self.width):
            return None
        return self.tiles[y][x]

    def get_show(self):
        height, width = self.tiles.shape

        return np.array([[self.tiles[y][x].tile_type.value for x in range(width)] for y in range(height)])

    def get_teleports(self):
        return self._teleports

    def has_any_gems(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.get_tile(y,x).get_gem() is not None:
                    return True

        return False
