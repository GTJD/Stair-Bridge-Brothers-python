import entity
import resources

import random

# A single tile making up the world
class Tile(entity.Entity):

    MASS = 20
    FRICTION = 0.5
    SIZE = 32

    WHITE_RATIO = 0.5

    BRIGHTNESS_MIN = 0.7
    BRIGHTNESS_RANGE = 1.0 - BRIGHTNESS_MIN

    DROP_IMPULSES = [ (100, 0), (-100,0) ]

    DROP_OFFSET = (0, SIZE // 2)

    def __init__(self, x, y, space, *args, **kwargs):
        self.space = space
        super(Tile, self).__init__(space,
                x = x * Tile.SIZE,
                y = y * Tile.SIZE,
                angle = 0,
                width = Tile.SIZE,
                height = Tile.SIZE,
                friction = Tile.FRICTION,
                mass = Tile.MASS,
                static = True,
                texture=resources.box)

        # random colour
        if random.random() < Tile.WHITE_RATIO:
            brightness = random.random() % Tile.BRIGHTNESS_RANGE + Tile.BRIGHTNESS_MIN
            self.red = brightness
            self.green = brightness
            self.blue = brightness

    def drop(self):
        self.static = False
        self.pymunk_body.apply_impulse(random.choice(Tile.DROP_IMPULSES), Tile.DROP_OFFSET)

