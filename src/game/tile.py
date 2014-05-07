import entity
import resources
from pyglet.app import WeakSet

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

    COLLISION_TYPE = 1

    def __init__(self, x, y, space, *args, **kwargs):
        self.space = space
        super(Tile, self).__init__(space,
                x = x * Tile.SIZE,
                y = y * Tile.SIZE,
                angle = 0,
                width = Tile.SIZE,
                height = Tile.SIZE,
                friction = Tile.FRICTION,
                collision_type = Tile.COLLISION_TYPE,
                mass = Tile.MASS,
                static = True,
                texture=resources.box)

        # random colour
        if random.random() < Tile.WHITE_RATIO:
            brightness = random.random() % Tile.BRIGHTNESS_RANGE + Tile.BRIGHTNESS_MIN
            self.rgb = brightness, brightness, brightness

        self.orig_color = self.rgb
        self.tints = WeakSet()

    def drop(self):
        self.static = False
        self.pymunk_body.apply_impulse(random.choice(Tile.DROP_IMPULSES), Tile.DROP_OFFSET)

    def set_last_tile_for(self, bro):
        self.tint(bro.color)

    def unset_last_tile_for(self, bro):
        self.untint(bro.color)

    def tint(self, color):
        self.tints.add(color)
        self._color()

    def untint(self, color):
        if color in self.tints:
            self.tints.remove(color)
        self._color()

    def _color(self):
        self.red = self.orig_color[0]
        self.green = self.orig_color[1]
        self.blue = self.orig_color[2]
        for tint in self.tints:
            t = tint.fade(Tile.BRIGHTNESS_RANGE).invert()
            self.red -= t.red
            self.green -= t.green
            self.blue -= t.blue

