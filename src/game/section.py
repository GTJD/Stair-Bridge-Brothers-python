import tile

import random
from operator import attrgetter

# A collection of Tiles with a CheckPoint at the end
class Section(object):

    TILE_SETS = [
        [
            [0,0,0,1,0,0,0,0,0,0,0],
            [0,0,1,1,1,0,0,0,0,0,0],
            [1,1,1,1,1,0,0,0,0,1,1],
        ],
        [
            [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1],
        ],
        [
            [0,0,0,0,0,1,0,0,0],
            [0,0,0,0,0,1,0,0,0],
            [0,0,0,0,0,1,0,0,0],
            [0,0,0,0,0,1,0,0,0],
            [1,1,1,1,1,1,0,1,1],
        ],
        [
            [0,0,0,0,0,1,1,1,0],
            [0,0,0,0,0,1,1,1,0],
            [0,0,0,0,0,1,1,1,1],
            [0,0,0,0,0,1,1,1,1],
            [0,0,0,0,0,1,1,1,1],
            [0,0,0,0,0,0,0,1,1],
            [0,0,0,0,0,1,0,1,1],
            [0,0,0,0,0,1,0,1,1],
            [0,0,0,0,0,1,0,1,1],
            [0,0,0,0,0,1,0,0,0],
            [1,1,1,1,1,1,0,1,1],
        ]
    ]

    def __init__(self, offset, space, *args, **kwargs):
        self.offset = offset
        tile_set = random.choice(Section.TILE_SETS)
        self.tiles, self.length = self.create_tiles(tile_set, space)
        #self.check_point = check_point
        self.completed = False

    def create_tiles(self, array, space):
        tiles = []
        height = len(array) - 1
        for y, row in enumerate(array):
            for x, val in enumerate(row):
                if val == 1:
                    tiles.append(tile.Tile(x + self.offset, height - y, space))
        length = len(array[0])
        return tiles, length

    def complete(self):
        self.check_point.complete = True

    def first_tile_offset(self):
        min_tile = min(self.tiles, key = attrgetter('x'))
        return min_tile.x

    def active_tiles(self):
        return [tile for tile in self.tiles if tile.static]
